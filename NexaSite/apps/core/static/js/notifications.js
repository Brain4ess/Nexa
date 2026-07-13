(function () {
    var maxVisible = 3;
    var queue = [];
    var active = [];

    var timeouts = {
        success: 2500,
        error: 3500,
        warning: 3000,
        info: 2500
    };

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

    function createToastElement(type, message, options) {
        options = options || {};

        var el = document.createElement("div");
        el.className = "toast toast--" + type;
        el.setAttribute("role", "alert");

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

        return el;
    }

    function removeToast(el) {
        if (el.classList.contains("removing")) return;
        clearTimeout(el.hideTimeout);
        el.classList.add("removing");
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
            var el = createToastElement(item.type, item.message, item.options);
            container.appendChild(el);
            active.push(el);

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
        queue.push({ type: type, message: message, options: options || {} });
        processQueue();
    }

    window.Toast = {
        show: show
    };
})();
