(function () {
    var maxVisible = 3;
    var queue = [];
    var active = [];
    var activeMap = {};

    var timeouts = {
        success: 3000,
        error: 3500,
        warning: 3000,
        info: 3000
    };

    function getGroupKey(type, message, options) {
        return type + "|" + message + "|" + (options && options.link || "");
    }

    function getContainer() {
        var el = document.getElementById("toast-container");
        if (!el) {
            el = document.createElement("div");
            el.id = "toast-container";
            el.className = "toast-container";

            document.body.appendChild(el);
        }

        return el;
    }

    function createToastElement(type, message, options, key) {
        options = options || {};

        var el = document.createElement("div");
        el.className = "toast toast--" + type;
        el.setAttribute("role", "alert");
        if (key) el.dataset.toastKey = key;

        var msgSpan = document.createElement("span");
        msgSpan.className = "toast-message";
        msgSpan.textContent = message;
        el.appendChild(msgSpan);

        if (options.link) {
            var link = document.createElement("a");
            link.className = "toast-link";
            link.href = options.link;
            link.textContent = options.linkText || "Перейти";

            el.appendChild(link);
        }

        var countSpan = document.createElement("span");
        countSpan.className = "toast-count";
        el.appendChild(countSpan);

        return el;
    }

    function updateCount(el, message, count) {
        var msgSpan = el.querySelector(".toast-message");
        var countSpan = el.querySelector(".toast-count");
        if (!msgSpan || !countSpan) return;

        msgSpan.textContent = message;

        if (count <= 1) {
            countSpan.classList.remove("visible");
            countSpan.textContent = "";
            return;
        }

        countSpan.classList.add("visible");
        countSpan.textContent = "\u00D7" + count;
    }

    function removeToast(el) {
        if (el.classList.contains("removing")) return;

        clearTimeout(el.hideTimeout);
        el.classList.add("removing");

        if (el.dataset.toastKey && activeMap[el.dataset.toastKey] === el) {
            delete activeMap[el.dataset.toastKey];
        }

        el.addEventListener("transitionend", function handler() {
            el.removeEventListener("transitionend", handler);

            if (el.parentNode) {
                el.parentNode.removeChild(el);
            }

            var idx = active.indexOf(el);
            if (idx !== -1) {
                active.splice(idx, 1);
            }

            processQueue();
        });
    }

    function processQueue() {
        while (queue.length > 0 && active.length < maxVisible) {
            var item = queue.shift();
            var container = getContainer();
            var el = createToastElement(item.type, item.message, item.options, item.key);
            el._toastCount = item.count || 1;

            updateCount(el, item.message, el._toastCount);

            container.appendChild(el);
            el.style.maxHeight = el.offsetHeight + "px";
            active.push(el);

            if (item.key) {
                activeMap[item.key] = el;
            }

            requestAnimationFrame(function () {
                requestAnimationFrame(function () {
                    el.classList.add("show");
                });
            });

            var duration = item.options && item.options.timeout != null
                ? item.options.timeout
                : timeouts[item.type] || 3000;

            el.hideTimeout = setTimeout(function () {
                removeToast(el);
            }, duration);
        }
    }

    function show(type, message, options) {
        options = options || {};
        var key = getGroupKey(type, message, options);

        if (key) {
            var existing = activeMap[key];
            if (existing) {
                clearTimeout(existing.hideTimeout);
                existing._toastCount = (existing._toastCount || 1) + 1;
                updateCount(existing, message, existing._toastCount);

                var duration = options.timeout != null
                    ? options.timeout
                    : timeouts[type] || 3000;

                existing.hideTimeout = setTimeout(function () {
                    removeToast(existing);
                }, duration);
                return;
            }

            for (var i = 0; i < queue.length; i++) {
                if (queue[i].key === key) {
                    queue[i].count = (queue[i].count || 1) + 1;
                    return;
                }
            }
        }

        queue.push({
            type: type,
            message: message,
            options: options,
            key: key,
            count: 1
        });
        processQueue();
    }

    window.Toast = {
        show: show
    };
})();
