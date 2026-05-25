(function () {
  function loadFallback() {
    if (window.MathJax) {
      return;
    }

    if (document.querySelector('script[data-qc-mathjax-fallback="true"]')) {
      return;
    }

    var script = document.createElement("script");
    script.async = true;
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS-MML_HTMLorMML";
    script.setAttribute("data-qc-mathjax-fallback", "true");
    document.head.appendChild(script);
  }

  window.setTimeout(loadFallback, 2000);
})();
