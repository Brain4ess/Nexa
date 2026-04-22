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
        const number = Number(String(value).replace(",", ".")) || 0;
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
        unitPrice = parseFloat(String(unitPrice).replace(",", "."));
        if (Number.isNaN(unitPrice)) unitPrice = 0;

        const total = unitPrice * Number(quantity || 0);

        const totalEl = row.querySelector("[data-cart-item-total]");
        if (totalEl) {
            totalEl.textContent = formatPrice(total);
        }
    };

    const showCartPopup = () => {
        const popup = document.getElementById("cart-popup");
        if (!popup) return;

        popup.classList.add("show");
        clearTimeout(popup.hideTimeout);

        popup.hideTimeout = setTimeout(() => {
            popup.classList.remove("show");
        }, 2500);
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

    const renderEmptyCart = () => {
        const page = document.querySelector(".cart-page");
        if (!page) return;

        page.innerHTML = `
            <h1 class="title">Корзина</h1>
            <div class="cart-empty">
                <p>Ваша корзина пуста.</p>
                <a href="/catalog/" class="empty-link">Перейти в каталог</a>
            </div>
        `;
    };

    const confirmModal = document.getElementById("confirmModal");
    const modalConfirmButton = document.getElementById("confirmModalConfirm");
    const modalCancelButton = document.getElementById("confirmModalCancel");

    let pendingRemoveRow = null;
    let pendingRemoveForm = null;

    const openConfirmModal = (row, form = null) => {
        pendingRemoveRow = row;
        pendingRemoveForm = form;
        if (!confirmModal) return;

        confirmModal.classList.add("is-open");
        document.body.classList.add("cart-lock");
    };

    const closeConfirmModal = () => {
        if (!confirmModal) return;

        confirmModal.classList.remove("is-open");
        document.body.classList.remove("cart-lock");
        pendingRemoveRow = null;
        pendingRemoveForm = null;
    };

    if (confirmModal) {
        confirmModal.addEventListener("click", (e) => {
            if (e.target.matches("[data-modal-close]")) {
                closeConfirmModal();
            }
        });
    }

    if (modalCancelButton) {
        modalCancelButton.addEventListener("click", closeConfirmModal);
    }

    if (modalConfirmButton) {
        modalConfirmButton.addEventListener("click", async () => {
            const removeForm = pendingRemoveForm || pendingRemoveRow?.querySelector(".cart-remove-form");
            if (!removeForm) return;

            const row = pendingRemoveRow || removeForm.closest(".cart-item");

            try {
                const formData = new FormData(removeForm);
                const { data } = await sendCartRequest(removeForm.action, formData);

                if (!data.ok) {
                    alert(data.error || "Ошибка");
                    return;
                }

                if (row) {
                    row.remove();
                }
                refreshCartUI(data);

                if (Number(data.items_count) === 0) {
                    renderEmptyCart();
                }
                closeConfirmModal();

            } catch (error) {
                console.error("Cart remove error:", error);
                closeConfirmModal();
            }
        });
    }

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeConfirmModal();
        }
    });

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
                    if (data.error === "Not enough stock" || data.error === "Недостаточно товара") {
                        showNotEnoughStockPopup();
                        return;
                    }

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

        if (!qtyInput || !productInput || !row) return;

        let typingTimer = null;

        const clampQuantity = (value) => {
            let num = Number(value);

            if (!Number.isFinite(num) || num < 1) {
                num = 1;
            }

            const max = Number(qtyInput.max || 0);
            if (max > 0) {
                num = Math.min(num, max);
            }

            return num;
        };

        const syncQuantity = async (quantity) => {
            const formData = new FormData();
            formData.append("product_id", productInput.value);
            formData.append("quantity", String(quantity));

            const { data } = await sendCartRequest(form.action, formData);

            if (!data.ok) {
                alert(data.error || "Ошибка");
                return false;
            }

            qtyInput.value = quantity;
            updateItemTotal(row, quantity);
            refreshCartUI(data);

            return true;
        };

        const handleQuantityInput = () => {
            const quantity = clampQuantity(qtyInput.value);

            if (String(qtyInput.value) !== String(quantity)) {
                qtyInput.value = quantity;
            }

            updateItemTotal(row, quantity);

            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                syncQuantity(quantity).catch((error) => {
                    console.error("Cart input sync error:", error);
                });
            }, 250);
        };

        qtyInput.addEventListener("input", handleQuantityInput);

        qtyInput.addEventListener("blur", () => {
            const quantity = clampQuantity(qtyInput.value);
            qtyInput.value = quantity;
            updateItemTotal(row, quantity);

            clearTimeout(typingTimer);
            syncQuantity(quantity).catch((error) => {
                console.error("Cart blur sync error:", error);
            });
        });

        form.querySelectorAll(".qty-btn").forEach((button) => {
            button.addEventListener("click", async (e) => {
                e.preventDefault();

                const currentQuantity = clampQuantity(qtyInput.value);
                const delta = Number(button.dataset.delta || 0);
                const nextQuantity = clampQuantity(currentQuantity + delta);

                if (delta < 0 && currentQuantity === 1) {
                    openConfirmModal(row);
                    return;
                }

                if (nextQuantity === currentQuantity) {
                    return;
                }

                try {
                    const success = await syncQuantity(nextQuantity);
                    if (!success) return;
                } catch (error) {
                    console.error("Cart update error:", error);
                }
            });
        });

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const quantity = clampQuantity(qtyInput.value);
            qtyInput.value = quantity;

            try {
                await syncQuantity(quantity);
            } catch (error) {
                console.error("Cart submit error:", error);
            }
        });
    });

    document.querySelectorAll(".cart-remove-form").forEach((form) => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();

            const row = form.closest(".cart-item");
            pendingRemoveRow = row;
            pendingRemoveForm = form;
            openConfirmModal(row, form);
        });
    });

    const showNotEnoughStockPopup = () => {
        const popup = document.getElementById("not-enough-stock-popup");
        if (!popup) return;

        popup.classList.add("show");
        clearTimeout(popup.hideTimeout);

        popup.hideTimeout = setTimeout(() => {
            popup.classList.remove("show");
        }, 2500);
    };
});
