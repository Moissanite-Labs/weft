// Paper pages: highlight the current section in the contents list.
// Theme, menu and copy buttons come from site.js.
import "./site.js";

const links = new Map();
document.querySelectorAll(".paper-toc a[href^='#']").forEach((a) => {
  const id = decodeURIComponent(a.getAttribute("href").slice(1));
  const target = document.getElementById(id);
  if (target) links.set(target, a);
});

if (links.size && "IntersectionObserver" in window) {
  let current = null;
  const visible = new Set();
  const update = () => {
    const first = [...links.keys()].find((el) => visible.has(el));
    if (!first || first === current) return;
    links.get(current)?.classList.remove("active");
    links.get(first).classList.add("active");
    current = first;
  };
  const io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) (e.isIntersecting ? visible.add(e.target) : visible.delete(e.target));
      update();
    },
    { rootMargin: "-80px 0px -65% 0px" },
  );
  links.forEach((_, el) => io.observe(el));
}

// On narrow screens, collapse the contents list after choosing a section.
const toc = document.querySelector(".paper-toc details");
if (toc) {
  const narrow = window.matchMedia("(max-width: 980px)");
  if (narrow.matches) toc.open = false;
  toc.addEventListener("click", (ev) => {
    if (narrow.matches && ev.target.closest("a")) toc.open = false;
  });
}
