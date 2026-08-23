document.documentElement.classList.add("js");

const header = document.querySelector("[data-header]");
const menu = document.querySelector("[data-menu]");
const menuToggle = document.querySelector("[data-menu-toggle]");

const updateHeader = () => {
  header?.classList.toggle("scrolled", window.scrollY > 24);
};

const closeMenu = () => {
  if (!menu || !menuToggle) return;
  menu.classList.remove("open");
  menuToggle.setAttribute("aria-expanded", "false");
  header?.classList.remove("menu-active");
  document.body.classList.remove("menu-open");
};

menuToggle?.addEventListener("click", () => {
  if (!menu) return;
  const isOpen = menu.classList.toggle("open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
  header?.classList.toggle("menu-active", isOpen);
  document.body.classList.toggle("menu-open", isOpen);
});

menu?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", closeMenu);
});

window.addEventListener("scroll", updateHeader, { passive: true });
window.addEventListener("resize", () => {
  if (window.innerWidth > 820) closeMenu();
});
updateHeader();

const reveals = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 },
  );

  reveals.forEach((item) => observer.observe(item));
} else {
  reveals.forEach((item) => item.classList.add("is-visible"));
}
