// Loads the Inter font for the dashboard and makes it the Home Assistant body/heading font.
// A per-view theme cannot change the body font (it inherits from <html>), so the variables are
// set on the root and re-applied whenever Home Assistant rewrites its theme variables there.
(function () {
  if (!document.getElementById('app-inter-font')) {
    const link = document.createElement('link');
    link.id = 'app-inter-font';
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap';
    document.head.appendChild(link);
  }
  const FONT = '"Inter", Roboto, Noto, sans-serif';
  const root = document.documentElement;
  const apply = () => {
    for (const v of ['--ha-font-family-body', '--ha-font-family-heading', '--primary-font-family', '--paper-font-common-base_-_font-family']) {
      if (root.style.getPropertyValue(v) !== FONT) root.style.setProperty(v, FONT);
    }
  };
  apply();
  new MutationObserver(apply).observe(root, { attributes: true, attributeFilter: ['style'] });
})();
