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

    const formatPrice = (value) => {
        const number = Number(value) || 0;
        return `${number.toLocaleString("ru-RU", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        })} ₽`;
    };

    const updateCartBadge = (count) => {
        document.querySelectorAll(".cart-badge").forEach((badge) => {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = "inline-block";
            } else {
                badge.style.display = "none";
            }
        });
    };

    const updateCartTotal = (total) => {
        document.querySelectorAll("[data-cart-total]").forEach((el) => {
            el.textContent = formatPrice(total);
        });
    };

    const updateCartItemsCount = (count) => {
        document.querySelectorAll("[data-cart-items-count]").forEach((el) => {
            el.textContent = `${count} шт.`;
        });
    };

    const updateItemTotal = (row, quantity) => {
        if (!row) return;

        let unitPrice = row.dataset.unitPrice || "0";
        unitPrice = parseFloat(unitPrice.replace(",", "."));

        if (isNaN(unitPrice)) unitPrice = 0;

        const total = unitPrice * Number(quantity || 0);

        const totalEl = row.querySelector("[data-cart-item-total]");
        if (totalEl) {
            totalEl.textContent = formatPrice(total);
        }
    };

    const sendCartRequest = async (url, formData) => {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: formData
        });

        const data = await response.json();
        return { response, data };
    };

    const refreshCartUI = (data) => {
        if (typeof data.items_count !== "undefined") {
            updateCartBadge(data.items_count);
            updateCartItemsCount(data.items_count);
        }

        if (typeof data.total_price !== "undefined") {
            updateCartTotal(data.total_price);
        }
    };

    document.querySelectorAll(".add-to-cart-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const button = form.querySelector("button");
            if (button && button.disabled) return;

            try {
                if (button) button.classList.add("loading");

                const formData = new FormData(form);
                const { data } = await sendCartRequest(form.action, formData);

                if (!data.ok) {
                    alert(data.error || "Ошибка");
                    return;
                }

                refreshCartUI(data);
                showCartPopup();

                if (button) {
                    button.classList.add("added");
                    setTimeout(() => button.classList.remove("added"), 600);
                }
            } catch (error) {
                console.error("Cart error:", error);
            } finally {
                if (button) button.classList.remove("loading");
            }
        });
    });

    document.querySelectorAll(".cart-quantity-form").forEach((form) => {
        const qtyInput = form.querySelector('input[name="quantity"]');
        const productInput = form.querySelector('input[name="product_id"]');
        const row = form.closest(".cart-item");

        form.querySelectorAll(".qty-btn").forEach((button) => {
            button.addEventListener("click", async (e) => {
                e.preventDefault();

                if (!qtyInput || !productInput) return;

                const delta = Number(button.dataset.delta || 0);
                const currentQuantity = Number(qtyInput.value || 1);
                const maxQuantity = Number(qtyInput.max || 0);

                let newQuantity = currentQuantity + delta;

                if (newQuantity < 1) {
                    return;
                }

                if (maxQuantity > 0) {
                    newQuantity = Math.min(newQuantity, maxQuantity);
                }

                if (newQuantity === currentQuantity) {
                    return;
                }

                const formData = new FormData();
                formData.append("product_id", productInput.value);
                formData.append("quantity", String(newQuantity));

                try {
                    const { data } = await sendCartRequest(form.action, formData);

                    if (!data.ok) {
                        alert(data.error || "Ошибка");
                        return;
                    }

                    qtyInput.value = newQuantity;
                    updateItemTotal(row, newQuantity);
                    refreshCartUI(data);

                } catch (error) {
                    console.error("Cart update error:", error);
                }
            });
        });

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!qtyInput || !productInput) return;

            const currentQuantity = Number(qtyInput.value || 1);
            const maxQuantity = Number(qtyInput.max || 0);

            let newQuantity = currentQuantity;

            if (newQuantity < 1) newQuantity = 1;
            if (maxQuantity > 0) newQuantity = Math.min(newQuantity, maxQuantity);

            const formData = new FormData();
            formData.append("product_id", productInput.value);
            formData.append("quantity", String(newQuantity));

            try {
                const { data } = await sendCartRequest(form.action, formData);

                if (!data.ok) {
                    alert(data.error || "Ошибка");
                    return;
                }

                qtyInput.value = newQuantity;
                updateItemTotal(row, newQuantity);
                refreshCartUI(data);

            } catch (error) {
                console.error("Cart submit error:", error);
            }
        });
    });

    document.querySelectorAll('form[action*="cart_remove"]').forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            try {
                const formData = new FormData(form);
                const { data } = await sendCartRequest(form.action, formData);

                if (!data.ok) {
                    alert(data.error || "Ошибка");
                    return;
                }

                const row = form.closest(".cart-item");
                if (row) row.remove();

                refreshCartUI(data);

                if (Number(data.items_count) === 0) {
                    window.location.reload();
                }
            } catch (error) {
                console.error("Cart remove error:", error);
            }
        });
    });
});
