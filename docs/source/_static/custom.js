document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });
});

// Google Analytics (GA4) events for use-case buttons.
// gtag is injected by sphinx_book_theme (analytics.google_analytics_id in conf.py).
(function () {
  function track(eventName, params) {
    try {
      if (typeof window.gtag !== "function") return;
      window.gtag("event", eventName, Object.assign({
        page_path: window.location.pathname,
        page_title: document.title,
        transport_type: "beacon"
      }, params));
    } catch (error) {
      // analytics must never break the page
    }
  }

  // Delegated listener so it works regardless of when the buttons are rendered
  document.addEventListener("click", function (e) {
    const el = e.target.closest("a, button");
    if (!el) return;

    if (el.classList.contains("btn-download-pdf-button")) {
      track("download_pdf", { button: "pdf" });
    } else if (el.classList.contains("btn-download-source-button")) {
      const href = el.getAttribute("href") || "";
      const ext = (href.split("?")[0].split(".").pop() || "").toLowerCase();
      track(ext === "ipynb" ? "download_ipynb" : "download_source", {
        button: ext,
        file_name: href.split("/").pop()
      });
    } else if (el.tagName === "A" && (el.href || "").includes("colab.research.google.com")) {
      track("open_in_colab", { link_url: el.href });
    }
  }, true);
})();
