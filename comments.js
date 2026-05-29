(function () {
  var repo = "elhyc/qcfieldscourse";
  var preferredCategory = "General";
  var disabledPages = {
    "404.html": true,
    "grover-reflections.html": true,
    "index.html": true,
    "print.html": true,
    "toc.html": true
  };
  var localHosts = {
    "127.0.0.1": true,
    "::1": true,
    "localhost": true
  };

  function pageName() {
    var parts = window.location.pathname.split("/");
    return parts[parts.length - 1] || "index.html";
  }

  function shouldSkipPage() {
    return disabledPages[pageName()];
  }

  function isLocalPreview() {
    return Boolean(localHosts[window.location.hostname]);
  }

  function currentGiscusTheme() {
    var classList = document.documentElement.classList;
    if (classList.contains("light") || classList.contains("rust")) {
      return "light";
    }
    return "dark";
  }

  function sendThemeToGiscus() {
    var iframe = document.querySelector("iframe.giscus-frame");
    if (!iframe || !iframe.contentWindow) {
      return;
    }
    iframe.contentWindow.postMessage(
      { giscus: { setConfig: { theme: currentGiscusTheme() } } },
      "https://giscus.app"
    );
  }

  function makeSection() {
    var main = document.querySelector("#mdbook-content main");
    if (!main || document.querySelector(".qc-discussions")) {
      return null;
    }

    var section = document.createElement("section");
    section.className = "qc-discussions";
    section.setAttribute("aria-labelledby", "qc-discussions-title");
    section.innerHTML =
      '<hr class="qc-discussions-rule">' +
      '<h2 id="qc-discussions-title">Discussion</h2>' +
      '<div class="giscus"></div>';

    var style = document.createElement("style");
    style.textContent =
      ".qc-discussions{margin-top:3.5rem;padding-top:1rem;}" +
      ".qc-discussions-rule{margin:0 0 1.5rem;border:0;border-top:1px solid var(--table-border-color);}" +
      ".qc-discussions h2{margin:0 0 1rem;font-size:1.35em;}" +
      ".qc-discussions-note{color:var(--fg);opacity:.78;font-size:.95em;}";
    document.head.appendChild(style);

    main.appendChild(section);
    return section;
  }

  function showLocalSetupNote(message) {
    if (!isLocalPreview()) {
      return;
    }
    var section = makeSection();
    if (!section) {
      return;
    }
    var target = section.querySelector(".giscus");
    target.className = "qc-discussions-note";
    target.textContent = message;
  }

  function chooseCategory(categories) {
    if (!categories || categories.length === 0) {
      return null;
    }
    for (var i = 0; i < categories.length; i += 1) {
      if (categories[i].name === preferredCategory) {
        return categories[i];
      }
    }
    return categories[0];
  }

  function addGiscus(config) {
    var section = makeSection();
    if (!section) {
      return;
    }

    var target = section.querySelector(".giscus");
    var script = document.createElement("script");
    var attributes = {
      src: "https://giscus.app/client.js",
      "data-repo": repo,
      "data-repo-id": config.repositoryId,
      "data-category": config.category.name,
      "data-category-id": config.category.id,
      "data-mapping": "pathname",
      "data-strict": "1",
      "data-reactions-enabled": "1",
      "data-emit-metadata": "0",
      "data-input-position": "bottom",
      "data-theme": currentGiscusTheme(),
      "data-lang": "en",
      "data-loading": "lazy",
      crossorigin: "anonymous",
      async: ""
    };

    Object.keys(attributes).forEach(function (name) {
      script.setAttribute(name, attributes[name]);
    });
    target.appendChild(script);

    var observer = new MutationObserver(sendThemeToGiscus);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
  }

  async function init() {
    if (shouldSkipPage()) {
      return;
    }

    var endpoint = "https://giscus.app/api/discussions/categories?repo=" + encodeURIComponent(repo);
    var controller = new AbortController();
    var timeout = window.setTimeout(function () {
      controller.abort();
    }, 4000);

    try {
      var response = await fetch(endpoint, {
        headers: { Accept: "application/json" },
        signal: controller.signal
      });
      if (!response.ok) {
        throw new Error("giscus setup is incomplete");
      }
      var data = await response.json();
      var category = chooseCategory(data.categories);
      if (!data.repositoryId || !category) {
        throw new Error("no discussion categories are available");
      }
      addGiscus({ repositoryId: data.repositoryId, category: category });
    } catch (error) {
      showLocalSetupNote(
        "GitHub Discussions and the giscus app need to be enabled before comments can appear here."
      );
    } finally {
      window.clearTimeout(timeout);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
