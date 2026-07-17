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

    const parsePrice = (text) => {
        const cleaned = String(text).replace(/[^\d.,\-]/g, "").replace(",", ".");
        return Number(cleaned) || 0;
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
        if (totalEl) totalEl.textContent = formatPrice(total);
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

    const restoreGlobals = (state) => {
        if (state.badgeCount !== undefined) updateCartBadge(state.badgeCount);
        document.querySelectorAll("[data-cart-items-count]").forEach((el) => {
            el.textContent = state.itemsCountText || "0 шт.";
        });
        document.querySelectorAll("[data-cart-total]").forEach((el) => {
            el.textContent = state.cartTotalText || "0 ₽";
        });
    };

    const _lastConfirmed = {
        badgeCount: Number(document.querySelector(".cart-badge")?.textContent || 0),
        itemsCountText: document.querySelector("[data-cart-items-count]")?.textContent || "0 шт.",
        cartTotalText: document.querySelector("[data-cart-total]")?.textContent || "0 ₽"
    };

    const _snapshots = {};
    const _controllers = {};

    const saveSnapshot = (productId, state) => { _snapshots[productId] = state; };
    const getSnapshot = (productId) => _snapshots[productId];
    const deleteSnapshot = (productId) => { delete _snapshots[productId]; };
    const deleteController = (productId) => { delete _controllers[productId]; };

    const abortProduct = (productId) => {
        if (_controllers[productId]) {
            _controllers[productId].abort();
            delete _controllers[productId];
        }
    };

    const sendCartRequest = async (url, formData, signal) => {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: formData,
            signal
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

    const confirmModal = document.getElementById("confirmModal");
    const modalConfirmButton = document.getElementById("confirmModalConfirm");
    const modalCancelButton = document.getElementById("confirmModalCancel");

    let pendingRemoveRow = null;
    let pendingRemoveForm = null;
    let pendingRemoveProductId = null;

    const openConfirmModal = (row, form = null) => {
        pendingRemoveRow = row;
        pendingRemoveForm = form;
        const productInput = form
            ? form.querySelector('input[name="product_id"]')
            : (row ? row.querySelector('input[name="product_id"]') : null);
        pendingRemoveProductId = productInput ? productInput.value : null;
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
        pendingRemoveProductId = null;
    };

    if (confirmModal) {
        confirmModal.addEventListener("click", (e) => {
            if (e.target.matches("[data-modal-close]")) closeConfirmModal();
        });
    }
    if (modalCancelButton) {
        modalCancelButton.addEventListener("click", closeConfirmModal);
    }
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeConfirmModal();
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
                        Toast.show("error", "Недостаточно товара");
                        return;
                    }
                    Toast.show("error", data.error || "Ошибка");
                    return;
                }

                refreshCartUI(data);
                _lastConfirmed.badgeCount = Number(data.items_count);
                _lastConfirmed.itemsCountText = `${data.items_count} шт.`;
                _lastConfirmed.cartTotalText = formatPrice(data.total_price);
                Toast.show("success", "Товар добавлен в корзину", { link: "/cart/", linkText: "Перейти" });

                if (button) {
                    button.classList.add("added");
                    setTimeout(() => button.classList.remove("added"), 600);
                }
            } catch (error) {
                if (error.name === "AbortError") return;
                console.error("Cart add error:", error);
                Toast.show("error", "Ошибка сети");
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
        let lastSyncedQuantity = qtyInput.value;

        const clampQuantity = (value) => {
            let num = Number(value);
            if (!Number.isFinite(num) || num < 1) num = 1;
            const max = Number(qtyInput.max || 0);
            if (max > 0) num = Math.min(num, max);
            return num;
        };

        const rollbackQuantity = (productId) => {
            const snap = getSnapshot(productId);
            if (!snap) return;

            _lastConfirmed.badgeCount = snap.badgeCount;
            _lastConfirmed.itemsCountText = snap.itemsCountText;
            _lastConfirmed.cartTotalText = snap.cartTotalText;

            const productRow = document.querySelector(`.cart-item[data-product-id="${productId}"]`);
            if (productRow) {
                const inputEl = productRow.querySelector('input[name="quantity"]');
                const totalEl = productRow.querySelector("[data-cart-item-total]");
                if (inputEl) {
                    inputEl.value = snap.quantity;
                    lastSyncedQuantity = snap.quantity;
                }
                if (totalEl && snap.itemTotalText) totalEl.textContent = snap.itemTotalText;
                console.error("Cart rollback: product", productId, "restored to qty", snap.quantity);
            }

            restoreGlobals(snap);
            deleteSnapshot(productId);
        };

        const syncQuantity = async (quantity) => {
            const productId = productInput.value;
            const confirmedQty = lastSyncedQuantity;
            const itemTotalEl = row.querySelector("[data-cart-item-total]");

            abortProduct(productId);

            saveSnapshot(productId, {
                badgeCount: _lastConfirmed.badgeCount,
                itemsCountText: _lastConfirmed.itemsCountText,
                cartTotalText: _lastConfirmed.cartTotalText,
                quantity: confirmedQty,
                itemTotalText: itemTotalEl ? itemTotalEl.textContent : ""
            });

            qtyInput.value = quantity;
            updateItemTotal(row, quantity);

            const unitPrice = parseFloat(String(row.dataset.unitPrice || "0").replace(",", ".")) || 0;
            const delta = Number(quantity) - Number(confirmedQty);
            if (delta && unitPrice > 0) {
                const confirmedTotal = parsePrice(_lastConfirmed.cartTotalText);
                updateCartTotal(Math.max(0, confirmedTotal + delta * unitPrice));
            }

            const controller = new AbortController();
            _controllers[productId] = controller;

            const formData = new FormData();
            formData.append("product_id", productId);
            formData.append("quantity", String(quantity));

            try {
                const { data } = await sendCartRequest(form.action, formData, controller.signal);

                if (!data.ok) {
                    rollbackQuantity(productId);
                    Toast.show("error", data.error || "Ошибка обновления");
                    deleteController(productId);
                    return;
                }

                qtyInput.value = quantity;
                updateItemTotal(row, quantity);
                refreshCartUI(data);
                _lastConfirmed.badgeCount = Number(data.items_count);
                _lastConfirmed.itemsCountText = `${data.items_count} шт.`;
                _lastConfirmed.cartTotalText = formatPrice(data.total_price);
                lastSyncedQuantity = String(quantity);
                deleteSnapshot(productId);
                deleteController(productId);

            } catch (error) {
                if (error.name === "AbortError") {
                    deleteController(productId);
                    return;
                }
                rollbackQuantity(productId);
                Toast.show("error", "Ошибка сети. Изменения не сохранены.");
                deleteController(productId);
            }
        };

        const handleQuantityInput = () => {
            const raw = qtyInput.value;
            const quantity = clampQuantity(raw);
            if (String(raw) !== String(quantity)) {
                qtyInput.value = quantity;
            }

            updateItemTotal(row, quantity);

            clearTimeout(typingTimer);
            typingTimer = setTimeout(() => {
                const q = clampQuantity(qtyInput.value);
                if (String(q) === String(lastSyncedQuantity)) return;
                syncQuantity(q).catch((err) => {
                    if (err.name !== "AbortError") console.error("Cart input sync error:", err);
                });
            }, 300);
        };

        qtyInput.addEventListener("input", handleQuantityInput);

        qtyInput.addEventListener("blur", () => {
            const quantity = clampQuantity(qtyInput.value);
            qtyInput.value = quantity;
            if (String(quantity) === String(lastSyncedQuantity)) return;
            clearTimeout(typingTimer);
            syncQuantity(quantity).catch((err) => {
                if (err.name !== "AbortError") console.error("Cart blur sync error:", err);
            });
        });

        form.querySelectorAll(".qty-btn").forEach((button) => {
            button.addEventListener("click", (e) => {
                e.preventDefault();

                const currentQuantity = clampQuantity(qtyInput.value);
                const delta = Number(button.dataset.delta || 0);
                const nextQuantity = clampQuantity(currentQuantity + delta);

                if (delta < 0 && currentQuantity === 1) {
                    const removeForm = row.querySelector(".cart-remove-form");
                    openConfirmModal(row, removeForm);
                    return;
                }

                if (nextQuantity === currentQuantity) return;

                clearTimeout(typingTimer);
                syncQuantity(nextQuantity).catch((err) => {
                    if (err.name !== "AbortError") console.error("Cart update error:", err);
                });
            });
        });

        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const quantity = clampQuantity(qtyInput.value);
            qtyInput.value = quantity;
            if (String(quantity) === String(lastSyncedQuantity)) return;
            clearTimeout(typingTimer);
            syncQuantity(quantity).catch((err) => {
                if (err.name !== "AbortError") console.error("Cart submit sync error:", err);
            });
        });
    });

    document.querySelectorAll(".cart-remove-form").forEach((form) => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const row = form.closest(".cart-item");
            openConfirmModal(row, form);
        });
    });

    if (modalConfirmButton) {
        modalConfirmButton.addEventListener("click", async () => {
            const removeForm = pendingRemoveForm || pendingRemoveRow?.querySelector(".cart-remove-form");
            if (!removeForm) return;

            const row = pendingRemoveRow || removeForm.closest(".cart-item");
            const productInput = removeForm.querySelector('input[name="product_id"]');
            const productId = productInput ? productInput.value : null;
            if (!productId) return;

            abortProduct(productId);

            const itemTotalEl = row ? row.querySelector("[data-cart-item-total]") : null;
            saveSnapshot(productId, {
                badgeCount: _lastConfirmed.badgeCount,
                itemsCountText: _lastConfirmed.itemsCountText,
                cartTotalText: _lastConfirmed.cartTotalText,
                itemTotalText: itemTotalEl ? itemTotalEl.textContent : ""
            });

            if (row) row.style.display = "none";

            const currentBadgeEl = document.querySelector(".cart-badge");
            const currentBadge = currentBadgeEl ? Number(currentBadgeEl.textContent) : _lastConfirmed.badgeCount;
            const newCount = Math.max(0, currentBadge - 1);
            updateCartBadge(newCount);
            updateCartItemsCount(newCount);

            if (itemTotalEl) {
                const itemPrice = parsePrice(itemTotalEl.textContent);
                const currentTotalEl = document.querySelector("[data-cart-total]");
                const currentCartPrice = currentTotalEl ? parsePrice(currentTotalEl.textContent) : parsePrice(_lastConfirmed.cartTotalText);
                updateCartTotal(Math.max(0, currentCartPrice - itemPrice));
            }

            closeConfirmModal();

            const controller = new AbortController();
            _controllers[productId] = controller;

            const formData = new FormData(removeForm);

            try {
                const { data } = await sendCartRequest(removeForm.action, formData, controller.signal);

                if (!data.ok) {
                    throw new Error(data.error || "Ошибка удаления");
                }

                if (row) row.remove();
                refreshCartUI(data);
                _lastConfirmed.badgeCount = Number(data.items_count);
                _lastConfirmed.itemsCountText = `${data.items_count} шт.`;
                _lastConfirmed.cartTotalText = formatPrice(data.total_price);
                deleteSnapshot(productId);
                deleteController(productId);

                if (Number(data.items_count) === 0) {
                    renderEmptyCart();
                }

            } catch (error) {
                if (error.name === "AbortError") return;

                const snap = getSnapshot(productId);
                if (snap) {
                    if (row) row.style.display = "";
                    _lastConfirmed.badgeCount = snap.badgeCount;
                    _lastConfirmed.itemsCountText = snap.itemsCountText;
                    _lastConfirmed.cartTotalText = snap.cartTotalText;
                    restoreGlobals(snap);
                }
                deleteSnapshot(productId);
                deleteController(productId);
                Toast.show("error", "Ошибка при удалении товара");
            }
        });
    }

});
