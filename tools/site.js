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
    });
  });
})();
