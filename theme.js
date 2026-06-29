/* Light/dark theme: remembers your choice, defaults to your system setting,
   and injects a floating toggle on every page. */
(function () {
  var KEY = "theme";
  var root = document.documentElement;

  function preferred() {
    try { var s = localStorage.getItem(KEY); if (s === "dark" || s === "light") return s; } catch (e) {}
    return (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
  }
  function apply(t) {
    if (t === "dark") root.setAttribute("data-theme", "dark");
    else root.removeAttribute("data-theme");
  }

  // run immediately (this script is in <head>) so there's no flash of the wrong theme
  apply(preferred());

  var SUN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17a5 5 0 100-10 5 5 0 000 10zm0-15a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm0 17a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM2 12a1 1 0 011-1h1a1 1 0 110 2H3a1 1 0 01-1-1zm17 0a1 1 0 011-1h1a1 1 0 110 2h-1a1 1 0 01-1-1zM4.93 4.93a1 1 0 011.41 0l.71.71A1 1 0 115.64 7.05l-.71-.71a1 1 0 010-1.41zm11.31 11.31a1 1 0 011.41 0l.71.71a1 1 0 11-1.41 1.41l-.71-.71a1 1 0 010-1.41zM19.07 4.93a1 1 0 010 1.41l-.71.71a1 1 0 11-1.41-1.41l.71-.71a1 1 0 011.41 0zM7.05 16.95a1 1 0 010 1.41l-.71.71A1 1 0 014.93 17.66l.71-.71a1 1 0 011.41 0z"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.79A9 9 0 1111.21 3a7 7 0 009.79 9.79z"/></svg>';

  function setIcon(btn) {
    var dark = root.getAttribute("data-theme") === "dark";
    btn.innerHTML = dark ? SUN : MOON; // icon shows what clicking will switch TO
    btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    btn.setAttribute("title", dark ? "Light mode" : "Dark mode");
  }

  function init() {
    var btn = document.createElement("button");
    btn.className = "theme-toggle";
    btn.type = "button";
    setIcon(btn);
    btn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      apply(next);
      try { localStorage.setItem(KEY, next); } catch (e) {}
      setIcon(btn);
    });
    document.body.appendChild(btn);
    requestAnimationFrame(function () { root.classList.add("theme-ready"); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
