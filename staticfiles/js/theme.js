const themeToggle = document.querySelector("[data-theme-toggle]");

if (themeToggle) {
  const themeLabel = themeToggle.querySelector("[data-theme-label]");

  const updateThemeControl = () => {
    const isDark = document.documentElement.dataset.theme === "dark";
    themeLabel.textContent = isDark ? "Light mode" : "Dark mode";
    themeToggle.setAttribute("aria-pressed", String(isDark));
    themeToggle.setAttribute(
      "aria-label",
      isDark ? "Switch to light mode" : "Switch to dark mode",
    );
  };

  updateThemeControl();

  themeToggle.addEventListener("click", () => {
    const nextTheme =
      document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    updateThemeControl();
    try {
      localStorage.setItem("task-manager-theme", nextTheme);
    } catch (error) {
      console.error("Could not save the color theme preference.", error);
    }
  });
}
