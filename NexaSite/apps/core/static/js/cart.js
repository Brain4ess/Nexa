document.addEventListener("DOMContentLoaded", () => {
    const getCSRFToken = () => {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return cookie.substring(name.length + 1);
            }
        }
        return "";
    };

    const updateCartBadge = (count) => {
        const badges = document.querySelectorAll(".cart-badge");

        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = "inline-block";
            } else {
                badge.style.display = "none";
            }
        });
    };

    const updateCartTotal = (total) => {
        const totalElements = document.querySelectorAll("[data-cart-total]");
        totalElements.forEach(el => {
            el.textContent = total + " ₽";
        });
    };

    const buttons = document.querySelectorAll(".add-to-cart");

    buttons.forEach(button => {
        button.addEventListener("click", async (e) => {
            e.preventDefault();

            if (button.disabled) return;

            const productId = button.dataset.product;

            try {
                const response = await fetch("/cart/add/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: `product_id=${productId}&quantity=1`
                });

                const data = await response.json();

                if (!data.ok) {
                    alert(data.error || "Ошибка");
                    return;
                }

                updateCartBadge(data.items_count);
                updateCartTotal(data.total_price);
                showCartPopup();

                button.classList.add("added");
                setTimeout(() => button.classList.remove("added"), 600);

            } catch (error) {
                console.error("Cart error:", error);
            }
        });
    });
});

const showCartPopup = () => {
    const popup = document.getElementById("cart-popup");
    if (!popup) return;

    popup.classList.add("show");

    clearTimeout(popup.hideTimeout);

    popup.hideTimeout = setTimeout(() => {
        popup.classList.remove("show");
    }, 2500);
};
