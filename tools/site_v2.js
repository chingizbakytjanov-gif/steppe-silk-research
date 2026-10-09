// Motion for Steppe & Silk Research: reveal on scroll, growing charts, counting numbers, reading progress.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;

  // Headings appear word by word.
  document.querySelectorAll('h1.split').forEach(function (h) {
    var words = h.textContent.trim().split(/\s+/);
    h.innerHTML = words.map(function (w, i) {
      return '<span class="w"><span style="--d:' + (i * 45) + 'ms">' + w + '</span></span>';
    }).join(' ');
  });

  // Elements that slide in when they reach the screen.
  var targets = '.intro-text, .intro-more, .block-head, .row, .figure, .fact, .filters, .page-head p,' +
                ' .report-body > h2, .report-body > p, .report-body > ol, .view, .sources, .pdf-frame,' +
                ' .prose > p, .prose > h2, .contact-list, .byline, .report-head .label';
  var items = document.querySelectorAll(targets);
  items.forEach(function (el, i) { el.classList.add('reveal'); });

  function countUp(el) {
    var m = el.textContent.match(/^([^\d]*)([\d.]+)(.*)$/);
    if (!m || reduce) return;
    var pre = m[1], end = parseFloat(m[2]), post = m[3], dec = (m[2].split('.')[1] || '').length;
    var t0 = null, dur = 900;
    function step(t) {
      if (!t0) t0 = t;
      var k = Math.min((t - t0) / dur, 1), e = 1 - Math.pow(1 - k, 3);
      el.textContent = pre + (end * e).toFixed(dec) + post;
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  if (!('IntersectionObserver' in window) || reduce) {
    items.forEach(function (el) { el.classList.add('in'); });
    document.querySelectorAll('.chart').forEach(function (c) { c.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target;
        el.classList.add('in');
        if (el.classList.contains('fact')) countUp(el.querySelector('.fact-num'));
        el.querySelectorAll && el.querySelectorAll('.chart').forEach(function (c) { c.classList.add('in'); });
        io.unobserve(el);
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    // Stagger neighbours that enter together.
    var groupIndex = new Map();
    items.forEach(function (el) {
      var p = el.parentNode, n = groupIndex.get(p) || 0;
      el.style.setProperty('--stagger', Math.min(n, 6) * 70 + 'ms');
      groupIndex.set(p, n + 1);
      io.observe(el);
    });
  }

  // Header shadow and reading progress.
  var bar = document.getElementById('progress');
  var isReport = !!document.querySelector('.report');
  function onScroll() {
    root.classList.toggle('scrolled', window.scrollY > 8);
    if (isReport && bar) {
      var max = document.body.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (max > 0 ? window.scrollY / max : 0) + ')';
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
