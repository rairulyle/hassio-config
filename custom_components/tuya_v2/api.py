"""Tuya OpenAPI client and Pulsar (message service) listener, both on HA's aiohttp session.

The lock is a Wi-Fi low-power device: it sleeps and only connects to the Tuya cloud when
woken (a key press, the bell, an unlock). There is no local path, so everything goes through
the Tuya IoT platform project:

* OpenAPI (HMAC-SHA256 signed REST) to read the device once at startup.
* Pulsar message service (websocket) to hear the lock's DP reports the moment it wakes,
  i.e. every unlock, the bell key, alarms and the battery level.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import time
from collections.abc import Callable

import aiohttp
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_LOGGER = logging.getLogger(__name__)

EMPTY_BODY_SHA = hashlib.sha256(b"").hexdigest()
TOKEN_MARGIN = 60  # refresh the access token this many seconds before it expires


class TuyaApiError(Exception):
    """A Tuya OpenAPI call failed."""


class TuyaOpenApi:
    """Minimal signed client for the Tuya OpenAPI."""

    def __init__(self, session: aiohttp.ClientSession, client_id: str, client_secret: str, region: str) -> None:
        self._session = session
        self._client_id = client_id
        self._secret = client_secret
        self._base = f"https://openapi.tuya{region}.com"
        self._token: str | None = None
        self._token_expires = 0.0
        self._token_lock = asyncio.Lock()

    async def _get_token(self) -> str:
        async with self._token_lock:
            if self._token and time.time() < self._token_expires - TOKEN_MARGIN:
                return self._token
            result = await self._request("GET", "/v1.0/token?grant_type=1", token="")
            self._token = result["access_token"]
            self._token_expires = time.time() + result["expire_time"]
            return self._token

    async def request(self, method: str, path: str, body: dict | None = None) -> dict | list | bool:
        """Signed business call; returns the 'result' field."""
        return await self._request(method, path, body, token=await self._get_token())

    async def _request(self, method: str, path: str, body: dict | None = None, *, token: str) -> dict | list | bool:
        if "?" in path:  # Tuya signs the query string with keys in dictionary order
            base_path, query = path.split("?", 1)
            path = base_path + "?" + "&".join(sorted(query.split("&")))
        data = json.dumps(body).encode() if body is not None else b""
        t = str(int(time.time() * 1000))
        string_to_sign = "\n".join([method, hashlib.sha256(data).hexdigest() if data else EMPTY_BODY_SHA, "", path])
        sign = hmac.new(
            self._secret.encode(), (self._client_id + token + t + string_to_sign).encode(), hashlib.sha256
        ).hexdigest().upper()
        headers = {
            "client_id": self._client_id,
            "sign": sign,
            "t": t,
            "sign_method": "HMAC-SHA256",
            "Content-Type": "application/json",
        }
        if token:
            headers["access_token"] = token
        try:
            async with self._session.request(
                method, self._base + path, data=data or None, headers=headers, timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                payload = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise TuyaApiError(f"{method} {path}: {err}") from err
        if not payload.get("success"):
            raise TuyaApiError(f"{method} {path}: {payload.get('code')} {payload.get('msg')}")
        return payload["result"]

    async def get_device(self, device_id: str) -> dict:
        return await self.request("GET", f"/v1.0/devices/{device_id}")


class TuyaPulsar:
    """Listener on Tuya's message service, delivering decrypted device messages to a callback."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_id: str,
        client_secret: str,
        region: str,
        on_message: Callable[[dict], None],
    ) -> None:
        self._session = session
        self._client_id = client_id
        self._on_message = on_message
        self._url = (
            f"wss://mqe.tuya{region}.com:8285/ws/v2/consumer/persistent/{client_id}/out/event/{client_id}-sub"
            "?ackTimeoutMillis=3000&subscriptionType=Failover"
        )
        secret_md5 = hashlib.md5(client_secret.encode()).hexdigest()  # noqa: S324 - Tuya's scheme
        self._password = hashlib.md5((client_id + secret_md5).encode()).hexdigest()[8:24]  # noqa: S324
        self._aes_key = client_secret[8:24].encode()
        self._task: asyncio.Task | None = None
        self.connected = False

    def start(self) -> None:
        self._task = asyncio.get_running_loop().create_task(self._run(), name="tuya_v2 pulsar")

    def stop(self) -> None:
        """Cancel the listener task (used as a config entry unload callback)."""
        if self._task:
            self._task.cancel()
            self._task = None

    async def _run(self) -> None:
        backoff = 5
        while True:
            try:
                await self._listen()
                backoff = 5
            except asyncio.CancelledError:
                raise
            except aiohttp.WSServerHandshakeError as err:
                _LOGGER.error(
                    "Tuya message service refused the connection (%s). Enable Message Service "
                    "for the project in the Tuya IoT platform; retrying in %ss", err.status, backoff,
                )
            except Exception as err:  # noqa: BLE001 - keep the listener alive whatever happens
                _LOGGER.warning("Tuya message service connection lost: %s; retrying in %ss", err, backoff)
            self.connected = False
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 300)

    async def _listen(self) -> None:
        headers = {"username": self._client_id, "password": self._password}
        async with self._session.ws_connect(self._url, headers=headers, heartbeat=30) as ws:
            self.connected = True
            _LOGGER.info("Connected to the Tuya message service")
            async for msg in ws:
                if msg.type != aiohttp.WSMsgType.TEXT:
                    continue
                envelope = json.loads(msg.data)
                if message_id := envelope.get("messageId"):  # ack first, whatever the content
                    await ws.send_str(json.dumps({"messageId": message_id}))
                try:
                    payload = json.loads(base64.b64decode(envelope["payload"]))
                    data = self._decrypt(payload["data"])
                except (KeyError, ValueError) as err:
                    _LOGGER.warning("Undecodable Tuya message (%s): %s", err, msg.data[:200])
                    continue
                _LOGGER.debug("Tuya message: %s", data)
                self._on_message(data)

    def _decrypt(self, data_b64: str) -> dict:
        """Decrypt a message's data: AES-GCM (12-byte nonce in front, 16-byte tag at the end,
        the platform's recommended setting) or legacy AES-ECB with PKCS7 padding."""
        blob = base64.b64decode(data_b64)
        try:
            raw = AESGCM(self._aes_key).decrypt(blob[:12], blob[12:], None)
        except (InvalidTag, ValueError):
            decryptor = Cipher(algorithms.AES(self._aes_key), modes.ECB()).decryptor()
            raw = decryptor.update(blob) + decryptor.finalize()
            raw = raw[: -raw[-1]]
        return json.loads(raw)
