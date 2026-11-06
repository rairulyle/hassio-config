"""Constants for the Tuya Cloud Lock integration."""

DOMAIN = "tuya_v2"  # a retired Tuya domain: the HA brand server still serves the Tuya logo for it, a private domain gets none

CONF_LOCKS = "locks"
CONF_DEVICE_ID = "device_id"
CONF_AUTO_LOCK_SECONDS = "auto_lock_seconds"
CONF_GATE_SENSOR = "gate_sensor"  # entity whose state is "open" / "closed" (a Frigate state classifier)

# Lock DP codes (Tuya category jtmspro, Wi-Fi low-power lock)
DP_DOORBELL = "doorbell"
DP_BATTERY = "residual_electricity"
DP_ALARM = "alarm_lock"
DP_UNLOCK_CODES = {  # DP code -> event type, value is the user/key id on the lock
    "unlock_fingerprint": "fingerprint",
    "unlock_password": "password",
    "unlock_temporary": "temporary_password",
    "unlock_card": "card",
    "unlock_app": "app",
    "open_inside": "inside",
}
ALARM_TYPES = [
    "wrong_finger", "wrong_password", "wrong_card", "wrong_face", "tongue_bad", "too_hot",
    "unclosed_time", "tongue_not_out", "pry", "key_in", "low_battery", "power_off", "shock",
    "defense", "stay_alarm", "doorbell", "wrong_unlock",
]

JAMMED_ALARMS = ("tongue_bad", "tongue_not_out")  # the bolt failed to come out: not locked

SIGNAL_UPDATE = f"{DOMAIN}_update_{{}}"  # per device id
DOORBELL_HOLD_SECONDS = 5
