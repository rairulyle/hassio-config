// Loads the Inter font used by the kohbo theme.
(function () {
  if (document.getElementById('kohbo-inter-font')) return;
  const link = document.createElement('link');
  link.id = 'kohbo-inter-font';
  link.rel = 'stylesheet';
  link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap';
  document.head.appendChild(link);
})();
