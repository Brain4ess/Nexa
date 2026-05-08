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

    const setRating = (value) => {
        if (!ratingInput) return;

        ratingInput.value = String(value);

        starButtons.forEach((button) => {
            button.classList.toggle("is-active", Number(button.dataset.value) <= Number(value));
        });

        if (ratingHint) {
            ratingHint.textContent = `Выбрано: ${value} из 5`;
        }
    };

    starButtons.forEach((button) => {
        button.addEventListener("click", () => {
            setRating(button.dataset.value);
        });
    });

    const reviewForm = document.getElementById("reviewForm");
    const reviewError = document.getElementById("reviewFormError");
    const reviewTitleInput = document.getElementById("reviewTitleInput");
    const reviewTextInput = document.getElementById("reviewTextInput");
    const reviewTitleCounter = document.getElementById("reviewTitleCounter");
    const reviewTextCounter = document.getElementById("reviewTextCounter");
    const reviewsList = document.getElementById("reviewsList");
    const reviewsEmpty = document.querySelector("[data-reviews-empty]");
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

    const updateRatingWidgets = (averageRating, reviewsCount) => {
        if (productAverageRating) {
            productAverageRating.textContent = averageRating;
        }

        if (productReviewsCount) {
            productReviewsCount.textContent = `(${reviewsCount})`;
        }

        if (reviewsTotalCount) {
            reviewsTotalCount.textContent = reviewsCount;
        }
    };

    if (reviewForm) {
        reviewForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (reviewError) {
                reviewError.hidden = true;
                reviewError.textContent = "";
            }

            if (!ratingInput || Number(ratingInput.value) < 1) {
                if (reviewError) {
                    reviewError.hidden = false;
                    reviewError.textContent = "Выберите оценку от 1 до 5";
                }
                return;
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
                    const errors = data.errors ? Object.values(data.errors).join("\n") : (data.error || "Ошибка");
                    if (reviewError) {
                        reviewError.hidden = false;
                        reviewError.textContent = errors;
                    }
                    return;
                }

                if (reviewsEmpty) {
                    reviewsEmpty.remove();
                }

                if (reviewsList && data.review_html) {
                    reviewsList.insertAdjacentHTML("afterbegin", data.review_html);
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
            const currentOffset = Number(moreButton.dataset.offset || reviewsList.querySelectorAll(".review-card").length || 0);
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