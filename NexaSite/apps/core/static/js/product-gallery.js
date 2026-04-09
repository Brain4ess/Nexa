document.addEventListener("DOMContentLoaded", function () {
    const mainImage = document.getElementById("productMainImage");
    const thumbnails = Array.from(document.querySelectorAll(".thumbnail"));

    if (!mainImage || thumbnails.length === 0) return;

    const mainWrapper = mainImage.closest(".main-image");
    const galleryWrapper = mainImage.closest(".gallery-wrapper");

    const placeholderSrc = "/static/images/placeholder.png";
    const images = thumbnails.map((thumb) => thumb.dataset.fullSrc || placeholderSrc);

    let currentIndex = Math.max(
        0,
        thumbnails.findIndex((thumb) => thumb.classList.contains("active"))
    );

    if (currentIndex < 0) currentIndex = 0;

    function setActive(index, animate = true) {
        if (images.length === 0) return;

        if (index < 0) index = images.length - 1;
        if (index >= images.length) index = 0;

        currentIndex = index;
        const newSrc = images[currentIndex];

        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle("active", i === currentIndex);
        });

        if (animate) {
            mainImage.style.opacity = "0";
            setTimeout(() => {
                mainImage.src = newSrc;
                mainImage.style.opacity = "1";
            }, 120);
        } else {
            mainImage.src = newSrc;
            mainImage.style.opacity = "1";
        }
    }

    mainImage.style.transition = "opacity 0.12s ease";

    thumbnails.forEach((thumb, index) => {
        thumb.addEventListener("click", function () {
            setActive(index, true);
        });
    });

    function createArrowButton(direction) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `gallery-arrow gallery-arrow-${direction}`;
        button.setAttribute("aria-label", direction === "prev" ? "Previous image" : "Next image");
        button.textContent = direction === "prev" ? "←" : "→";

        button.style.position = "absolute";
        button.style.top = "50%";
        button.style.transform = "translateY(-50%)";
        button.style.zIndex = "3";
        button.style.width = "40px";
        button.style.height = "40px";
        button.style.border = "none";
        button.style.borderRadius = "50%";
        button.style.background = "rgba(15, 23, 42, 0.58)";
        button.style.color = "#fff";
        button.style.fontSize = "20px";
        button.style.fontWeight = "600";
        button.style.display = "flex";
        button.style.alignItems = "center";
        button.style.justifyContent = "center";
        button.style.cursor = "pointer";
        button.style.userSelect = "none";
        button.style.backdropFilter = "blur(6px)";
        button.style.boxShadow = "0 8px 18px rgba(0, 0, 0, 0.18)";
        button.style.transition = "transform 0.15s ease, opacity 0.15s ease";

        button.addEventListener("mouseenter", () => {
            button.style.transform = "translateY(-50%) scale(1.06)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.transform = "translateY(-50%) scale(1)";
        });

        button.addEventListener("mousedown", () => {
            button.style.transform = "translateY(-50%) scale(0.96)";
        });

        button.addEventListener("mouseup", () => {
            button.style.transform = "translateY(-50%) scale(1.06)";
        });

        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            if (direction === "prev") {
                setActive(currentIndex - 1, true);
            } else {
                setActive(currentIndex + 1, true);
            }
        });

        return button;
    }

    if (mainWrapper) {
        mainWrapper.style.position = "relative";

        if (images.length > 1) {
            const prevButton = createArrowButton("prev");
            const nextButton = createArrowButton("next");

            prevButton.style.left = "12px";
            nextButton.style.right = "12px";

            mainWrapper.appendChild(prevButton);
            mainWrapper.appendChild(nextButton);
        }
    }

    let touchStartX = 0;
    let touchEndX = 0;
    let isTouching = false;

    function handleSwipe() {
        const deltaX = touchEndX - touchStartX;

        if (Math.abs(deltaX) < 50) return;

        if (deltaX > 0) {
            setActive(currentIndex - 1, true);
        } else {
            setActive(currentIndex + 1, true);
        }
    }

    if (mainWrapper && images.length > 1) {
        mainWrapper.addEventListener("touchstart", function (event) {
            touchStartX = event.changedTouches[0].screenX;
            isTouching = true;
        }, { passive: true });

        mainWrapper.addEventListener("touchend", function (event) {
            if (!isTouching) return;
            touchEndX = event.changedTouches[0].screenX;
            isTouching = false;
            handleSwipe();
        }, { passive: true });
    }

    setActive(currentIndex, false);
});