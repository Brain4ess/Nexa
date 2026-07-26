const THEME_KEY = "theme";

function updateIcon(theme) {
    const icon = document.getElementById("themeIcon");
    if (!icon) return;

    if (theme === "dark") {
        icon.src = "/static/images/dark_theme_icon.png";
    } else {
        icon.src = "/static/images/white_theme_icon.png";
    }
}

function updateLogo(theme) {
    const logo = document.getElementById("logoImg");
    if (!logo) return;

    logo.src = theme === "dark"
        ? "/static/images/logo/nexa-logo-white.svg"
        : "/static/images/logo/nexa-logo-blue.svg";
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    updateIcon(theme);
    updateLogo(theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const newTheme = current === "dark" ? "light" : "dark";
    setTheme(newTheme);
}

document.getElementById("themeToggle")?.addEventListener("click", toggleTheme);
