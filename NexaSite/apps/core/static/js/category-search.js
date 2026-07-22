function normalize(s) {
    return s.toLowerCase().replace(/ё/g, "е").trim();
}

function damerauLevenshtein(a, b) {
    const m = a.length, n = b.length;
    const d = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));

    for (let i = 0; i <= m; i++) d[i][0] = i;
    for (let j = 0; j <= n; j++) d[0][j] = j;

    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            const cost = a[i - 1] === b[j - 1] ? 0 : 1;

            d[i][j] = Math.min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost
            );

            if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
                d[i][j] = Math.min(d[i][j], d[i - 2][j - 2] + cost);
            }
        }
    }
    return d[m][n];
}

function similarity(a, b) {
    const na = normalize(a), nb = normalize(b);
    if (na.length === 0 && nb.length === 0) return 1;

    const maxLen = Math.max(na.length, nb.length);
    if (maxLen === 0) return 1;

    return 1 - damerauLevenshtein(na, nb) / maxLen;
}

const input = document.getElementById("categorySearch");
const cards = Array.from(document.querySelectorAll(".category-card"));
const noResultsMessage = document.getElementById("noResultsMessage");

input.addEventListener("input", function () {
    const value = input.value.trim();
    if (!value) {
        cards.forEach(c => { c.style.display = ""; });
        noResultsMessage.style.display = "none";
        return;
    }

    const scored = cards.map(card => ({
        card,
        name: card.dataset.name,
        score: similarity(value, card.dataset.name)
    }));

    const matched = scored.filter(s => s.score > 0.4 || s.name.includes(value));
    matched.sort((a, b) => b.score - a.score);

    cards.forEach(c => { c.style.display = "none"; });
    matched.forEach(s => { s.card.style.display = ""; });

    matched.forEach((s, i) => {
        const parent = s.card.parentNode;
        const ref = parent.children[i];

        if (ref !== s.card) {
            parent.insertBefore(s.card, ref);
        }
    });

    noResultsMessage.style.display = matched.length === 0 ? "block" : "none";
});
