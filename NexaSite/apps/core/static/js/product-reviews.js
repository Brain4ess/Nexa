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

    const formatReviewDateTime = (value) => {
        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return "";
        }

        const format = (useUTC = false) => {
            const options = {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
                hour12: false,
                ...(useUTC ? { timeZone: "UTC" } : {}),
            };

            return date.toLocaleString("ru-RU", options).replace(",", "");
        };

        try {
            return format(false);
        } catch {
            try {
                return format(true);
            } catch {
                return "";
            }
        }
    };

    const decorateReviewTimes = (root = document) => {
        root.querySelectorAll("[data-review-datetime]").forEach((el) => {
            el.textContent = formatReviewDateTime(el.dataset.reviewDatetime);
        });
    };

    decorateReviewTimes();

    const tabs = Array.from(document.querySelectorAll("[data-product-tab]"));
    const panels = Array.from(document.querySelectorAll("[data-product-panel]"));
    const indicator = document.getElementById("productTabsIndicator");

    const activateTab = (tabName) => {
        tabs.forEach((button) => {
            const isActive = button.dataset.productTab === tabName;
            button.classList.toggle("is-active", isActive);
            button.setAttribute("aria-selected", String(isActive));
        });

        panels.forEach((panel) => {
            panel.classList.toggle("is-active", panel.dataset.productPanel === tabName);
        });

        if (indicator) {
            indicator.classList.toggle("is-reviews", tabName === "reviews");
        }
    };

    tabs.forEach((button) => {
        button.addEventListener("click", () => {
            activateTab(button.dataset.productTab);
        });
    });

    activateTab("specs");

    const ratingInput = document.getElementById("reviewRatingInput");
    const ratingHint = document.getElementById("reviewRatingHint");
    const starButtons = Array.from(document.querySelectorAll("[data-review-stars] .review-star"));
    const starsWrapper = document.querySelector("[data-review-stars]");

    const renderStarState = (selectedValue = 0, hoverValue = null) => {
        starButtons.forEach((button) => {
            const value = Number(button.dataset.value || 0);
            button.classList.toggle("is-active", value <= selectedValue);
            button.classList.toggle("is-hovered", hoverValue !== null && value <= hoverValue);
        });
    };

    const setRating = (value) => {
        if (!ratingInput) return;

        ratingInput.value = String(value);
        renderStarState(Number(value), null);

        if (ratingHint) {
            ratingHint.textContent = `Выбрано: ${value} из 5`;
        }
    };

    starButtons.forEach((button) => {
        button.addEventListener("mouseenter", () => {
            renderStarState(Number(ratingInput?.value || 0), Number(button.dataset.value || 0));
        });

        button.addEventListener("click", () => {
            setRating(Number(button.dataset.value || 0));
        });
    });

    if (starsWrapper) {
        starsWrapper.addEventListener("mouseleave", () => {
            renderStarState(Number(ratingInput?.value || 0), null);
        });
    }

    const reviewForm = document.getElementById("reviewForm");
    const reviewError = document.getElementById("reviewFormError");
    const reviewTitleInput = document.getElementById("reviewTitleInput");
    const reviewTextInput = document.getElementById("reviewTextInput");
    const reviewTitleCounter = document.getElementById("reviewTitleCounter");
    const reviewTextCounter = document.getElementById("reviewTextCounter");
    const reviewsList = document.getElementById("reviewsList");
    const reviewsEmpty = document.querySelector("[data-reviews-empty]");
    const clearEmptyState = () => {
        document.querySelectorAll("[data-reviews-empty]").forEach((el) => el.remove());
    };
    const moreButton = document.getElementById("reviewsMoreButton");
    const reviewsTotalCount = document.getElementById("reviewsTotalCount");
    const productAverageRating = document.getElementById("productAverageRating");
    const productReviewsCount = document.getElementById("productReviewsCount");

    const updateCounter = (input, counter, max) => {
        if (!input || !counter) return;
        counter.textContent = `${input.value.length}/${max}`;
    };

    const updateFormCounters = () => {
        updateCounter(reviewTitleInput, reviewTitleCounter, 50);
        updateCounter(reviewTextInput, reviewTextCounter, 3000);
    };

    if (reviewTitleInput) {
        reviewTitleInput.addEventListener("input", updateFormCounters);
    }

    if (reviewTextInput) {
        reviewTextInput.addEventListener("input", updateFormCounters);
    }

    updateFormCounters();

    const clampLines = (value, maxLines) => {
        const lines = value.split(/\r?\n/);
        return lines.length > maxLines ? lines.slice(0, maxLines).join("\n") : value;
    };

    const clampReviewTextLines = () => {
        if (!reviewTextInput) return;

        const clamped = clampLines(reviewTextInput.value, 15);

        if (clamped !== reviewTextInput.value) {
            reviewTextInput.value = clamped;
        }

        updateFormCounters();
    };

    if (reviewTextInput) {
        reviewTextInput.addEventListener("input", clampReviewTextLines);
        reviewTextInput.addEventListener("paste", () => {
            setTimeout(clampReviewTextLines, 0);
        });
    }

    const clampReviewUpdateText = (textarea) => {
        if (!textarea) return;

        const lines = textarea.value.split(/\r?\n/);
        const limited = lines.slice(0, 10).join("\n").slice(0, 1000);

        if (textarea.value !== limited) {
            textarea.value = limited;
        }
    };

    document.addEventListener("input", (e) => {
        const textarea = e.target.closest(".review-edit-form textarea");
        if (!textarea) return;

        clampReviewUpdateText(textarea);
    });

    const updateRatingWidgets = (averageRating, reviewsCount) => {
        const count = Number(reviewsCount || 0);
        const avg = Number(averageRating || 0);

        if (productAverageRating) {
            productAverageRating.textContent = count > 0 ? avg.toFixed(1) : "0";
        }

        if (productReviewsCount) {
            productReviewsCount.textContent = `(${count})`;
        }

        if (reviewsTotalCount) {
            reviewsTotalCount.textContent = String(count);
        }
    };

    const showEmptyReviewsState = () => {
        if (!reviewsList) return;

        reviewsList.innerHTML = `
            <div class="reviews-empty" data-reviews-empty>Пока нет отзывов. Будьте первым.</div>
        `;
    };

    const initReviewCard = (card) => {
        if (!card) return;

        const text = card.querySelector("[data-review-text]");
        const textToggle = card.querySelector("[data-review-text-toggle]");
        const updatesWrap = card.querySelector("[data-review-updates]");
        const updatesToggle = card.querySelector("[data-review-updates-toggle]");

        if (text && textToggle) {
            const rawText = (text.textContent || "").trim();
            const lineCount = rawText ? rawText.split(/\r?\n/).length : 0;
            const shouldCollapse = rawText.length > 260 || lineCount > 4;

            text.classList.toggle("is-collapsed", shouldCollapse);
            textToggle.hidden = !shouldCollapse;
            textToggle.textContent = "Развернуть";
        }

        if (updatesWrap && updatesToggle) {
            updatesWrap.classList.add("is-hidden");
            updatesToggle.textContent = "Показать дополнения";
            updatesToggle.setAttribute("aria-expanded", "false");
        }

        const editToggle = card.querySelector("[data-review-edit-toggle]");
        const editPanel = card.querySelector("[data-review-edit-panel]");

        if (editToggle && editPanel && editPanel.hasAttribute("hidden")) {
            editToggle.textContent = "Дополнить отзыв";
            editToggle.setAttribute("aria-expanded", "false");
        }
    };

    const initReviewCards = (root = document) => {
        root.querySelectorAll(".review-card").forEach(initReviewCard);
    };

    initReviewCards();

    const replaceReviewCard = (reviewId, html) => {
        const oldCard = document.querySelector(`[data-review-id="${reviewId}"]`);
        if (!oldCard) return;

        oldCard.insertAdjacentHTML("beforebegin", html);
        const newCard = oldCard.previousElementSibling;
        oldCard.remove();

        initReviewCard(newCard);
        decorateReviewTimes(newCard);
    };

    const removeReviewCard = (reviewId) => {
        const card = document.querySelector(`[data-review-id="${reviewId}"]`);
        if (card) {
            card.remove();
        }

        if (reviewsList) {
            const cardsLeft = reviewsList.querySelectorAll(".review-card").length;
            if (cardsLeft === 0) {
                showEmptyReviewsState();
            }
        }
    };

    document.addEventListener("click", (e) => {
        const textToggle = e.target.closest("[data-review-text-toggle]");
        if (textToggle) {
            const card = textToggle.closest(".review-card");
            const text = card?.querySelector("[data-review-text]");
            if (!text) return;

            const collapsed = text.classList.toggle("is-collapsed");
            textToggle.textContent = collapsed ? "Развернуть" : "Скрыть";
            return;
        }

        const updatesToggle = e.target.closest("[data-review-updates-toggle]");
        if (updatesToggle) {
            const card = updatesToggle.closest(".review-card");
            const updates = card?.querySelector("[data-review-updates]");
            if (!updates) return;

            const isHidden = updates.classList.toggle("is-hidden");

            updatesToggle.textContent = isHidden ? "Показать дополнения" : "Скрыть дополнения";
            updatesToggle.setAttribute("aria-expanded", String(!isHidden));

            return;
        }

        const editToggle = e.target.closest("[data-review-edit-toggle]");
        if (editToggle) {
            const card = editToggle.closest(".review-card");
            const panel = card?.querySelector("[data-review-edit-panel]");
            if (!panel) return;

            const isHidden = panel.hasAttribute("hidden");

            if (isHidden) {
                panel.removeAttribute("hidden");
                editToggle.textContent = "Скрыть";
                editToggle.setAttribute("aria-expanded", "true");
            } else {
                panel.setAttribute("hidden", "");
                editToggle.textContent = "Дополнить отзыв";
                editToggle.setAttribute("aria-expanded", "false");
            }

            return;
        }
    });

    document.addEventListener("submit", async (e) => {
        const deleteForm = e.target.closest(".review-delete-form");
        if (deleteForm) {
            e.preventDefault();

            try {
                const response = await fetch(deleteForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: new FormData(deleteForm)
                });

                const data = await response.json();

                if (!data.ok) {
                    return;
                }

                const card = deleteForm.closest(".review-card");
                const reviewId = card?.dataset.reviewId;

                if (reviewId) {
                    removeReviewCard(reviewId);
                }

                updateRatingWidgets(data.average_rating, data.reviews_count);

                if (moreButton) {
                    moreButton.dataset.offset = String(document.querySelectorAll(".review-card").length);
                    if (Number(data.reviews_count) === 0) {
                        moreButton.remove();
                    }
                }

                decorateReviewTimes(document);
            } catch (error) {
                console.error("Review delete error:", error);
            }

            return;
        }

        const editForm = e.target.closest(".review-edit-form");
        if (editForm) {
            e.preventDefault();

            const errorBox = editForm.querySelector(".review-form__error");
            if (errorBox) {
                errorBox.hidden = true;
                errorBox.textContent = "";
            }

            try {
                const response = await fetch(editForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: new FormData(editForm)
                });

                const data = await response.json();

                if (!data.ok) {
                    if (errorBox) {
                        errorBox.hidden = false;
                        errorBox.textContent = data.errors ? Object.values(data.errors).join("\n") : "Ошибка";
                    }
                    return;
                }

                const card = editForm.closest(".review-card");
                const reviewId = card?.dataset.reviewId;

                if (reviewId && data.review_html) {
                    replaceReviewCard(reviewId, data.review_html);
                }

                const panel = card?.querySelector("[data-review-edit-panel]");
                const toggle = card?.querySelector("[data-review-edit-toggle]");

                if (panel) {
                    panel.setAttribute("hidden", "");
                }

                if (toggle) {
                    toggle.textContent = "Дополнить отзыв";
                    toggle.setAttribute("aria-expanded", "false");
                }
            } catch (error) {
                console.error("Review update error:", error);
                if (errorBox) {
                    errorBox.hidden = false;
                    errorBox.textContent = "Не удалось сохранить дополнение";
                }
            }

            return;
        }
    });

    if (reviewForm) {
        reviewForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (reviewError) {
                reviewError.hidden = true;
                reviewError.textContent = "";
            }

            const formData = new FormData(reviewForm);

            try {
                const response = await fetch(reviewForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: formData
                });

                const data = await response.json();

                if (!data.ok) {
                    const errors = data.errors || {};

                    const errorMessage =
                        errors.non_field ||
                        errors.rating ||
                        errors.title ||
                        errors.text ||
                        errors.usage_period ||
                        data.error ||
                        "Ошибка";

                    if (reviewError) {
                        reviewError.hidden = false;
                        reviewError.textContent = errorMessage;
                    }

                    return;
                }

                clearEmptyState();

                if (reviewsList && data.review_html) {
                    reviewsList.insertAdjacentHTML("afterbegin", data.review_html);
                    initReviewCard(reviewsList.firstElementChild);
                    decorateReviewTimes(reviewsList.firstElementChild);
                }

                if (moreButton) {
                    moreButton.dataset.offset = String(reviewsList.querySelectorAll(".review-card").length);
                }

                updateRatingWidgets(data.average_rating, data.reviews_count);

                reviewForm.reset();
                setRating(0);

                if (ratingHint) {
                    ratingHint.textContent = "Нажмите на звёзды, чтобы поставить оценку";
                }

                updateFormCounters();
                decorateReviewTimes(document);
            } catch (error) {
                console.error("Review submit error:", error);
                if (reviewError) {
                    reviewError.hidden = false;
                    reviewError.textContent = "Не удалось отправить отзыв";
                }
            }
        });
    }

    if (moreButton && reviewsList) {
        moreButton.addEventListener("click", async () => {
            const currentOffset = Number(
                moreButton.dataset.offset || reviewsList.querySelectorAll(".review-card").length || 0
            );

            const url = new URL(moreButton.dataset.url, window.location.origin);
            url.searchParams.set("offset", String(currentOffset));

            try {
                const response = await fetch(url.toString(), {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                const data = await response.json();

                if (!data.ok) return;

                if (data.html) {
                    reviewsList.insertAdjacentHTML("beforeend", data.html);

                    const newCards = reviewsList.querySelectorAll(".review-card");
                    const lastCard = newCards[newCards.length - 1];
                    initReviewCard(lastCard);
                    decorateReviewTimes(reviewsList);
                }

                if (data.has_more) {
                    moreButton.dataset.offset = String(data.next_offset);
                } else {
                    moreButton.remove();
                }
            } catch (error) {
                console.error("Load more reviews error:", error);
            }
        });
    }
});
