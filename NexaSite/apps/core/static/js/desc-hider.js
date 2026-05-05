document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.getElementById("descWrapper");
    const content = document.getElementById("productDesc");
    const controls = document.getElementById("descControls");
    const btn = document.getElementById("descToggle");

    if (!wrapper || !content || !controls || !btn) return;

    const text = content.textContent.trim();

    if (text.length <= 100) {
        controls.remove();
        return;
    }

    let isOpen = false;

    content.classList.add("is-collapsed");
    btn.hidden = false;

    btn.addEventListener("click", () => {
        isOpen = !isOpen;
        content.classList.toggle("is-collapsed", !isOpen);
        btn.textContent = isOpen ? "Скрыть" : "Развернуть";
    });
});
