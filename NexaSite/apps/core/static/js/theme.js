const THEME_KEY = 'nexa-theme';
const LIGHT = 'light-theme';
const DARK = 'dark-theme';

const body = document.body;

function applyTheme(theme) {
    if (theme === DARK) {
        body.classList.add(DARK);
        body.classList.remove(LIGHT);
    } else {
        body.classList.add(LIGHT);
        body.classList.remove(DARK);
    }
}

let currentTheme = localStorage.getItem(THEME_KEY) || LIGHT;
applyTheme(currentTheme);

// Get the theme toggle button
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        // Change the theme and save it to localStorage
        currentTheme = currentTheme === LIGHT ? DARK : LIGHT;
        applyTheme(currentTheme);
        localStorage.setItem(THEME_KEY, currentTheme);
    });
}
