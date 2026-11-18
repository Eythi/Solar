// Site-wide motion: scroll reveal, 3D tilt, cursor glow, scroll progress, page transitions,
// 3D orbit decoration on page headers, word-by-word headline rise. All of it is skipped
// when the visitor asks the system for reduced motion.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(pointer: fine)').matches;
  var root = document.documentElement;
  root.classList.add('js');
  if (reduce) { root.classList.add('reduce'); return; }

  // ---- page enter / leave ----
  requestAnimationFrame(function () { root.classList.add('ready'); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || a.target || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    var href = a.getAttribute('href');
    if (!/^[\w-]+\.html(#.*)?$/.test(href) || href.split('#')[0] === location.pathname.split('/').pop()) return;
    e.preventDefault();
    root.classList.add('leaving');
    setTimeout(function () { location.href = href; }, 260);
  });
  window.addEventListener('pageshow', function (e) { if (e.persisted) root.classList.remove('leaving'); });

  // ---- scroll progress: a small sun ring in the corner that also takes you back up ----
  var ring = document.createElement('button');
  ring.type = 'button';
  ring.className = 'sun-ring';
  ring.setAttribute('aria-label', 'Наверх');
  ring.innerHTML = '<svg viewBox="0 0 48 48" aria-hidden="true"><defs><linearGradient id="sr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffd166"/><stop offset=".55" stop-color="#ff8a3d"/><stop offset="1" stop-color="#ff4d6d"/></linearGradient></defs><circle class="sr-track" cx="24" cy="24" r="20"/><circle class="sr-fill" cx="24" cy="24" r="20" pathLength="100"/></svg><span class="sr-core"></span><span class="sr-arrow">↑</span>';
  document.body.appendChild(ring);
  var fill = ring.querySelector('.sr-fill');
  ring.addEventListener('click', function () { scrollTo({ top: 0, behavior: 'smooth' }); });
  var head = document.querySelector('.site-head');
  function onScroll() {
    var h = document.documentElement.scrollHeight - innerHeight;
    var p = h > 0 ? Math.min(scrollY / h, 1) : 0;
    fill.style.strokeDashoffset = (100 - p * 100).toFixed(1);
    ring.classList.toggle('show', scrollY > 240);
    if (head) head.classList.toggle('scrolled', scrollY > 8);
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---- headline: split into words that rise in turn ----
  document.querySelectorAll('h1').forEach(function (h) {
    if (h.closest('.legal')) return;
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function (w) {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(w)); return; }
            var o = document.createElement('span'); o.className = 'w';
            var s = document.createElement('span'); s.className = 'wi'; s.textContent = w;
            s.style.animationDelay = (0.08 + i++ * 0.07) + 's';
            o.appendChild(s); frag.appendChild(o);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) { walk(n); }
      });
    })(h);
    h.classList.add('split');
  });

  // ---- scroll reveal with stagger ----
  var sel = '.card, .section-head, .section > h2, .feature-row > *, .steps > li, details, .table-wrap, .release, .cta-strip, .platform, .note, .faq-group > h2, .facts, .page-hero p, .eyebrow, .marquee';
  var items = document.querySelectorAll(sel);
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      io.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  items.forEach(function (el) {
    if (el.closest('.legal')) return;
    var sib = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
    el.style.setProperty('--d', Math.min(sib, 6) * 70 + 'ms');
    el.classList.add('rv');
    io.observe(el);
  });

  // ---- 3D tilt for cards and phones ----
  if (fine) {
    document.querySelectorAll('.card, .phone, .cta-strip, .steps > li').forEach(function (el) {
      el.classList.add('tilt');
      var glare = document.createElement('span');
      glare.className = 'glare';
      el.appendChild(glare);
      var max = el.classList.contains('phone') ? 14 : 8;
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        el.style.setProperty('--rx', ((0.5 - y) * max).toFixed(2) + 'deg');
        el.style.setProperty('--ry', ((x - 0.5) * max).toFixed(2) + 'deg');
        el.style.setProperty('--gx', (x * 100).toFixed(1) + '%');
        el.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
        el.classList.add('tilting');
      });
      el.addEventListener('pointerleave', function () {
        el.style.setProperty('--rx', '0deg');
        el.style.setProperty('--ry', '0deg');
        el.classList.remove('tilting');
      });
    });

  }

  // ---- phones float and turn in 3D with scroll ----
  var phones = document.querySelectorAll('.feature-media .phone');
  if (phones.length) {
    var ticking = false;
    function turn() {
      phones.forEach(function (p, i) {
        var r = p.getBoundingClientRect();
        var k = (r.top + r.height / 2 - innerHeight / 2) / innerHeight; // -1..1
        p.style.setProperty('--sy', (k * (i % 2 ? -22 : 22)).toFixed(2) + 'deg');
        p.style.setProperty('--sx', (k * 10).toFixed(2) + 'deg');
      });
      ticking = false;
    }
    addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(turn); } }, { passive: true });
    turn();
  }

  // ---- 3D orbit decoration on inner page headers ----
  document.querySelectorAll('.page-hero').forEach(function (h) {
    var o = document.createElement('div');
    o.className = 'orbit3d';
    o.setAttribute('aria-hidden', 'true');
    o.innerHTML = '<div class="o-core"></div><div class="o-ring r1"><i></i></div><div class="o-ring r2"><i></i></div><div class="o-ring r3"><i></i></div>';
    h.appendChild(o);
  });

  // ---- number counters ----
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var end = parseFloat(el.getAttribute('data-count'));
    var cio = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      cio.disconnect();
      var t0 = performance.now();
      (function step(t) {
        var p = Math.min((t - t0) / 1400, 1);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    });
    cio.observe(el);
  });
})();
