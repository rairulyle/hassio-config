// Page transitions between dashboard views, built on the browser's View Transitions API and Material 3
// motion. Every move between views (navbar taps, swipes, links, the room follow automation) cross-fades
// the page while the new view's cards ease in: swipes slide them in from the side the swipe came from
// (Material "shared axis X"), everything else fades through with a slight scale (Material "fade through").
// The old and new snapshots' opacities add up to 1 on every frame, so the navbar, which looks the same on
// every view, stays still (it lives in shadow DOM, where it can't get a view-transition-name of its own).
// Pop-ups (hash changes), background tabs and browsers without the API navigate as before; reduced motion
// keeps only a short cross-fade. Swipe navigation's own animation is off (swipe_nav in ui-lovelace.yaml).
(function () {
  if (window.__appViewTransitions || !document.startViewTransition) return;
  window.__appViewTransitions = true;

  const DASHBOARD = '/lovelace/';
  // Material 3 tokens: standard easing for the page cross-fade (short2-short4 range), emphasized
  // decelerate for entering content (medium2), shared axis travel 30px, fade-through start scale 0.92
  // softened to 0.96 because it applies per card instead of to the whole page.
  const FADE_MS = 200;
  const FADE_REDUCED_MS = 150;
  const FADE_EASING = 'cubic-bezier(0.2, 0, 0, 1)';
  const ENTER_MS = 300;
  const ENTER_EASING = 'cubic-bezier(0.05, 0.7, 0.1, 1)';
  const SLIDE_PX = 30;
  const SCALE_FROM = 0.96;
  const STAGGER_MS = 20;
  const STAGGER_MAX = 6;
  const WAIT_MS = 400;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

  const style = document.createElement('style');
  style.textContent = `
    ::view-transition-old(root), ::view-transition-new(root) {
      animation-duration: ${FADE_MS}ms;
      animation-timing-function: ${FADE_EASING};
    }
    @media (prefers-reduced-motion: reduce) {
      ::view-transition-old(root), ::view-transition-new(root) { animation-duration: ${FADE_REDUCED_MS}ms; }
    }`;
  document.head.appendChild(style);

  // A quick horizontal swipe just before a navigation means swipe navigation made it: 1 = to the next
  // view (content comes in from the right), -1 = to the previous one.
  let touch = null;
  let swipe = null;
  addEventListener('touchstart', (e) => {
    const t = e.touches[0];
    touch = e.touches.length === 1 ? { x: t.clientX, y: t.clientY, at: Date.now() } : null;
  }, { capture: true, passive: true });
  addEventListener('touchend', (e) => {
    if (!touch) return;
    const t = e.changedTouches[0];
    const dx = t.clientX - touch.x;
    const dy = t.clientY - touch.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy) && Date.now() - touch.at < 800) {
      swipe = { dir: dx < 0 ? 1 : -1, at: Date.now() };
    }
    touch = null;
  }, { capture: true, passive: true });

  const kids = (n) => [...(n.shadowRoot ? n.shadowRoot.children : []), ...n.children];
  const find = (n, tag) => {
    if (n.localName === tag) return n;
    for (const c of kids(n)) {
      const found = find(c, tag);
      if (found) return found;
    }
    return null;
  };
  const currentView = () =>
    find(document.querySelector('home-assistant'), 'hui-root')?.shadowRoot.querySelector('#view > hui-view') || null;
  // Top-level cards on screen, without the navbar's card (it must not move).
  const visibleCards = (view) => {
    const cards = [];
    const walk = (n) => {
      for (const c of kids(n)) {
        if (c.localName !== 'hui-card') walk(c);
        else if (!kids(c).some((k) => k.localName === 'navbar-card')) cards.push(c);
      }
    };
    walk(view);
    return cards.filter((c) => {
      const r = c.getBoundingClientRect();
      return r.width > 0 && r.bottom > 0 && r.top < innerHeight;
    });
  };

  // Resolves once the new view is in place with its cards laid out, or after WAIT_MS regardless.
  const nextView = (oldView) =>
    new Promise((resolve) => {
      const start = Date.now();
      const check = () => {
        const view = currentView();
        if (view && view !== oldView && visibleCards(view).length) return resolve(view);
        if (Date.now() - start >= WAIT_MS) return resolve(view !== oldView ? view : null);
        setTimeout(check, 16);
      };
      check();
    });

  const animateIn = (view, dir) => {
    const from = dir ? `translateX(${dir * SLIDE_PX}px)` : `scale(${SCALE_FROM})`;
    visibleCards(view).forEach((card, i) =>
      card.animate([{ opacity: 0, transform: from }, { opacity: 1, transform: 'none' }], {
        duration: ENTER_MS,
        easing: ENTER_EASING,
        delay: Math.min(i, STAGGER_MAX) * STAGGER_MS,
        fill: 'backwards',
      }),
    );
  };

  const viewOf = (path) => (path.startsWith(DASHBOARD) ? path.slice(DASHBOARD.length).split('/')[0] : null);
  let lastPath = location.pathname;
  let replaying = false;

  // Holds back Home Assistant's own location-changed handling until the old page is captured, then
  // replays the event inside the transition.
  addEventListener('location-changed', (e) => {
    const from = lastPath;
    const to = location.pathname;
    lastPath = to;
    if (replaying || from === to || viewOf(from) === null || viewOf(to) === null) return;
    if (document.visibilityState !== 'visible') return;
    e.stopImmediatePropagation();
    const dir = swipe && Date.now() - swipe.at < 600 ? swipe.dir : 0;
    swipe = null;
    const oldView = currentView();
    document.startViewTransition(async () => {
      replaying = true;
      try {
        dispatchEvent(new CustomEvent('location-changed', { detail: e.detail }));
      } finally {
        replaying = false;
      }
      const view = await nextView(oldView);
      if (view && !reducedMotion.matches) animateIn(view, dir);
    });
  }, true);
})();
