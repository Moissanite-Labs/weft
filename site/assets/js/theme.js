// Apply a saved theme choice before first paint. Without one, CSS follows the OS.
(function () {
  try {
    var t = localStorage.getItem("weft-theme");
    if (t === "light" || t === "dark") document.documentElement.setAttribute("data-theme", t);
  } catch (e) { /* storage unavailable: follow the OS */ }
})();
