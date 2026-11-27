const mobileMenuToggle = document.querySelector("[data-mobile-menu-toggle]");

if (mobileMenuToggle) {
  const navContainer = mobileMenuToggle.closest(".nav-container");
  const primaryNavigation = document.querySelector("#primary-navigation");

  if (navContainer && primaryNavigation) {
    const setMenuOpen = (isOpen) => {
      if (isOpen) {
        navContainer.setAttribute("data-menu-open", "true");
      } else {
        navContainer.removeAttribute("data-menu-open");
      }

      mobileMenuToggle.setAttribute("aria-expanded", String(isOpen));
      mobileMenuToggle.setAttribute(
        "aria-label",
        isOpen ? "Close navigation menu" : "Open navigation menu",
      );
    };

    mobileMenuToggle.addEventListener("click", () => {
      const isOpen = mobileMenuToggle.getAttribute("aria-expanded") === "true";
      setMenuOpen(!isOpen);
    });

    primaryNavigation.addEventListener("click", () => setMenuOpen(false));

    document.addEventListener("click", (event) => {
      const isOpen = mobileMenuToggle.getAttribute("aria-expanded") === "true";
      if (isOpen && !navContainer.contains(event.target)) {
        setMenuOpen(false);
      }
    });

    document.addEventListener("keydown", (event) => {
      const isOpen = mobileMenuToggle.getAttribute("aria-expanded") === "true";
      if (event.key === "Escape" && isOpen) {
        setMenuOpen(false);
        mobileMenuToggle.focus();
      }
    });
  }
}
