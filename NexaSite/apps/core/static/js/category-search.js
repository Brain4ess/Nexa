const input = document.getElementById("categorySearch");
const cards = document.querySelectorAll(".category-card");
const noResultsMessage = document.getElementById("noResultsMessage");

function similarity(a, b) {
    a = a.toLowerCase();
    b = b.toLowerCase();
    if (a.length === 0) return 1;
    let matches = 0;
    for (let i = 0; i < a.length; i++) {
        if (b.includes(a[i])) matches++;
    }
    return matches / Math.max(a.length, b.length);
}

input.addEventListener("input", function () {
    const value = input.value.toLowerCase().trim();
    let found = 0;
    cards.forEach(card => {
        const name = card.dataset.name;
        if (name.includes(value) || similarity(value, name) > 0.5) {
            card.style.display = "";
            found++;
        } else {
            card.style.display = "none";
        }
    });
    if (found === 0 && value !== "") {
        noResultsMessage.style.display = "block";
    } else {
        noResultsMessage.style.display = "none";
    }
});