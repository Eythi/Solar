// Mobile menu toggle. The site works without it: links stay reachable on wide screens.
(function () {
  var btn = document.querySelector('.menu-btn');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var open = document.body.classList.toggle('menu-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.body.classList.contains('menu-open')) {
      document.body.classList.remove('menu-open');
      btn.setAttribute('aria-expanded', 'false');
      btn.focus();
    }
  });
})();
