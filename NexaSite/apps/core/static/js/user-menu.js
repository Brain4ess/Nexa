const userMenu = document.getElementById("userMenu");
const userTrigger = document.getElementById("userTrigger");

if (userTrigger && userMenu) {
    userTrigger.addEventListener("click", () => {
        userMenu.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
        if (!userMenu.contains(e.target)) {
            userMenu.classList.remove("open");
        }
    });
}