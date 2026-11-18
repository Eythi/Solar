// Extra motion layer: icon stroke drawing, heading underline sweeps, click ripples,
// spotlight across card grids, parallax floaters, scroll-spy for the legal table of contents,
// timeline progress on the changelog and steps, live visualizer.
(function () {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var fine = matchMedia('(pointer: fine)').matches;
  var raf = window.requestAnimationFrame;

  function onView(els, cb, opts) {
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (e) { if (e.isIntersecting) { cb(e.target); io.unobserve(e.target); } });
    }, opts || { threshold: 0.2 });
    els.forEach(function (el) { io.observe(el); });
  }

  // ---- 1. icons draw themselves ----
  var icons = document.querySelectorAll('.ico svg');
  icons.forEach(function (svg) {
    svg.querySelectorAll('path, circle, rect').forEach(function (s) {
      var len = 120;
      try { len = Math.ceil(s.getTotalLength()) + 2; } catch (e) {}
      s.style.strokeDasharray = len;
      s.style.strokeDashoffset = len;
    });
  });
  onView(icons, function (svg) { svg.classList.add('drawn'); });

  // ---- 2. section headings get an underline sweep + letter wave ----
  var heads = document.querySelectorAll('.section-head h2, .section > h2, .feature-row h2, .faq-group > h2, .release-title h2, .cta-strip h2');
  heads.forEach(function (h) {
    h.classList.add('sweep');
    var text = h.textContent;
    h.setAttribute('aria-label', text);
    h.innerHTML = '';
    var i = 0;
    text.split(/(\s+)/).forEach(function (word) {
      if (/^\s+$/.test(word)) { h.appendChild(document.createTextNode(' ')); return; }
      var w = document.createElement('span');
      w.className = 'lw';
      w.setAttribute('aria-hidden', 'true');
      Array.from(word).forEach(function (ch) {
        var c = document.createElement('span');
        c.className = 'lc';
        c.textContent = ch;
        c.style.setProperty('--i', i++);
        w.appendChild(c);
      });
      h.appendChild(w);
    });
  });
  onView(heads, function (h) { h.classList.add('lit'); });

  // ---- 4. click ripple on buttons, cards, nav ----
  document.addEventListener('pointerdown', function (e) {
    var t = e.target.closest && e.target.closest('.btn, .card, .nav a, summary, .release-nav a, .toc a');
    if (!t) return;
    var r = t.getBoundingClientRect();
    var d = Math.max(r.width, r.height) * 2.2;
    var rip = document.createElement('span');
    rip.className = 'ripple';
    rip.style.cssText = 'width:' + d + 'px;height:' + d + 'px;left:' + (e.clientX - r.left - d / 2) + 'px;top:' + (e.clientY - r.top - d / 2) + 'px';
    if (getComputedStyle(t).position === 'static') t.style.position = 'relative';
    t.style.overflow = 'hidden';
    t.appendChild(rip);
    setTimeout(function () { rip.remove(); }, 800);
  });

  if (fine) {
    // ---- 6. spotlight follows the cursor across card grids ----
    document.querySelectorAll('.grid').forEach(function (g) {
      g.classList.add('spot');
      g.addEventListener('pointermove', function (e) {
        g.querySelectorAll(':scope > .card').forEach(function (c) {
          var r = c.getBoundingClientRect();
          c.style.setProperty('--sx', (e.clientX - r.left) + 'px');
          c.style.setProperty('--sy', (e.clientY - r.top) + 'px');
        });
      });
    });

  }

  // ---- 8. floating glass shapes with parallax on every page ----
  var layer = document.createElement('div');
  layer.className = 'floaters';
  layer.setAttribute('aria-hidden', 'true');
  var shapes = [
    ['ring', 6, 20, 0.25], ['cube', 90, 34, 0.45], ['ring sm', 92, 95, 0.5], ['cube sm', 8, 130, 0.35],
  ];
  shapes.forEach(function (s) {
    var d = document.createElement('div');
    d.className = 'fl ' + s[0];
    d.style.left = s[1] + '%';
    d.style.top = s[2] + 'vh';
    d.dataset.speed = s[3];
    var faces = s[0].indexOf('cube') === 0 ? '<b></b><b></b><b></b><b></b><b></b><b></b>' : '';
    d.innerHTML = '<div class="in" style="animation-delay:' + (-Math.random() * 20).toFixed(1) + 's">' + faces + '</div>';
    layer.appendChild(d);
  });
  document.body.appendChild(layer);
  var fls = layer.querySelectorAll('.fl');
  var pt = false;
  function para() {
    var y = scrollY;
    fls.forEach(function (f) { f.style.transform = 'translateY(' + (-y * f.dataset.speed).toFixed(1) + 'px)'; });
    layer.style.setProperty('--hue', (y / 12 % 360).toFixed(0) + 'deg');
    pt = false;
  }
  addEventListener('scroll', function () { if (!pt) { pt = true; raf(para); } }, { passive: true });
  para();

  // ---- 9. scroll-spy for the legal table of contents ----
  var toc = document.querySelector('.toc');
  if (toc) {
    var links = toc.querySelectorAll('a');
    var map = {};
    links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var spy = new IntersectionObserver(function (en) {
      en.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('on'); });
        var a = map[e.target.id];
        if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest' }); }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    document.querySelectorAll('.legal h2[id]').forEach(function (h) { spy.observe(h); });
  }

  // ---- 10. progress line along steps and the changelog ----
  document.querySelectorAll('.steps, .release-layout > div').forEach(function (list) {
    list.classList.add('track');
    var line = document.createElement('span');
    line.className = 'track-line';
    list.appendChild(line);
    var t = false;
    function upd() {
      var r = list.getBoundingClientRect();
      var p = Math.min(Math.max((innerHeight * 0.6 - r.top) / r.height, 0), 1);
      line.style.transform = 'scaleY(' + p.toFixed(3) + ')';
      t = false;
    }
    addEventListener('scroll', function () { if (!t) { t = true; raf(upd); } }, { passive: true });
    upd();
  });

  // ---- 11. hero visualizer dances like a spectrum ----
  var viz = document.querySelector('.viz');
  if (viz) {
    var bars = viz.querySelectorAll('i');
    var vis = true;
    new IntersectionObserver(function (e) { vis = e[0].isIntersecting; if (vis) raf(dance); }).observe(viz);
    var t0 = performance.now();
    function dance(now) {
      if (!vis) return;
      var t = (now - t0) / 1000;
      bars.forEach(function (b, i) {
        var x = i / bars.length;
        var v = 0.25 + 0.35 * Math.abs(Math.sin(t * 2.1 + i * 0.35)) * (1 - x * 0.5)
              + 0.25 * Math.abs(Math.sin(t * 3.7 + i * 0.9)) + 0.15 * Math.sin(t * 1.3 + x * 6);
        b.style.transform = 'scaleY(' + Math.max(0.08, Math.min(1, v)).toFixed(3) + ')';
      });
      raf(dance);
    }
    raf(dance);
  }

  // ---- 12. table rows and list items slide in one by one ----
  var rows = document.querySelectorAll('tbody tr, .feature-row li, .platform li, .release li');
  rows.forEach(function (r) {
    if (r.closest('.legal')) return;
    r.classList.add('slide');
    var idx = Array.prototype.indexOf.call(r.parentElement.children, r);
    r.style.setProperty('--k', Math.min(idx, 10));
  });
  onView(Array.prototype.filter.call(rows, function (r) { return r.classList.contains('slide'); }), function (r) { r.classList.add('in2'); }, { threshold: 0.1 });

  // ---- 13. phones wipe in ----
  var phs = document.querySelectorAll('.feature-media .phone');
  phs.forEach(function (p) { p.classList.add('wipe'); });
  onView(phs, function (p) { p.classList.add('wiped'); });
})();
