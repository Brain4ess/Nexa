function normalize(s) {
    if (!s) return "";
    return s.toLowerCase().replace(/ё/g, "е").trim();
}

function damerauLevenshtein(a, b) {
    const m = a.length, n = b.length;
    const d = Array.from({ length: m + 1 }, () => new Array(n + 1));

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
    return 1 - damerauLevenshtein(na, nb) / maxLen;
}

const input = document.getElementById("categorySearch");
const cards = input
    ? Array.from(document.querySelectorAll(".category-card")).filter(c => c.dataset.name)
    : [];
const noResultsMessage = document.getElementById("noResultsMessage");

if (input) {
    let debounceTimer;
    input.addEventListener("input", function () {
        const value = input.value.trim();
        if (!value) {
            clearTimeout(debounceTimer);
            cards.forEach(c => { c.style.display = ""; });
            if (noResultsMessage) noResultsMessage.style.display = "none";
            return;
        }

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const normValue = normalize(value);
            const scored = cards.map(card => {
                const name = card.dataset.name;
                return {
                    card,
                    score: similarity(normValue, name),
                    normName: normalize(name)
                };
            });

            const matched = scored.filter(s => s.score > 0.4 || s.normName.includes(normValue));
            matched.sort((a, b) => b.score - a.score);

            cards.forEach(c => { c.style.display = "none"; });
            matched.forEach(s => { s.card.style.display = ""; });

            const byParent = new Map();
            matched.forEach(s => {
                const p = s.card.parentNode;
                if (!byParent.has(p)) byParent.set(p, []);
                byParent.get(p).push(s.card);
            });

            byParent.forEach((children, parent) => {
                children.forEach((card, i) => {
                    const ref = parent.children[i];
                    if (ref !== card) {
                        parent.insertBefore(card, ref);
                    }
                });
            });

            if (noResultsMessage) noResultsMessage.style.display = matched.length === 0 ? "block" : "none";
        }, 150);
    });
}
