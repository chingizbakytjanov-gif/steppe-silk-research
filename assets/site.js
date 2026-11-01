// Steppe & Silk Research: header shadow, reading progress on reports, research filters. Content is never hidden.
(function () {
  var root = document.documentElement;
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

  var buttons = document.querySelectorAll('.filters button');
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-f');
      buttons.forEach(function (x) { x.classList.toggle('on', x === b); });
      document.querySelectorAll('#rows .row').forEach(function (r) {
        r.hidden = !(f === 'all' || r.getAttribute('data-type') === f);
      });
      document.querySelectorAll('[data-photo]').forEach(function (el) {
        el.hidden = el.getAttribute('data-photo') !== f;
      });
    });
  });
  // research.html#trade and #companies (the labels on each report) open with that filter on
  var start = document.querySelector('.filters button[data-f="' + location.hash.slice(1) + '"]');
  if (start) start.click();
})();
// Learn: diagrams start their animation when they scroll into view
(function () {
  var els = document.querySelectorAll('.learn-anim');
  if (!els.length) return;
  if (!('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('play'); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('play'); io.unobserve(en.target); } });
  }, { threshold: 0.35 });
  els.forEach(function (e) { io.observe(e); });
})();
