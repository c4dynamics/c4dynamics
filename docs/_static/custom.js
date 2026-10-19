document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });

  // Links in the page content open in a new tab. Anchors within the same
  // page (headings, equations, footnotes) and the sidebar navigation keep
  // the current tab.
  document.querySelectorAll(".bd-article a[href]").forEach(link => {
    const href = link.getAttribute("href");
    if (href.startsWith("#") || link.classList.contains("headerlink")) return;
    const url = new URL(link.href, window.location.href);
    if (url.pathname === window.location.pathname && url.hash) return;
    link.target = "_blank";
    link.rel = "noopener";
  });

  // Use Cases sidebar: close the section with a "More…" entry that opens
  // the overview page, like its "Introduction" entry. Added here rather
  // than in the toctree, which doesn't allow the same page twice.
  // On the overview page itself Sphinx renders its link as href="#", so
  // the check is on the resolved path, not on the raw href.
  document.querySelectorAll(".bd-sidebar-primary li.toctree-l1 > a").forEach(intro => {
    const path = new URL(intro.href).pathname;
    if (!path.endsWith("/programs/index.html") && !path.endsWith("/programs/")) return;
    const more = document.createElement("li");
    more.className = "toctree-l1";
    const a = document.createElement("a");
    a.className = "reference internal";
    a.href = intro.href;
    a.textContent = "More…";
    more.appendChild(a);
    intro.parentElement.parentElement.appendChild(more);
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
