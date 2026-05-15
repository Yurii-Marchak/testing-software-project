import { announce } from "./utils.js";

export function initToasts() {
    const stack = document.querySelector(".js-flash-stack");
    if (!stack) return;
    const flashes = Array.from(stack.querySelectorAll(".flash"));
    flashes.forEach((flash) => {
        showToast(flash.textContent.trim(), flash.dataset.flashCategory || "info");
    });
}

export function showToast(message, category = "info") {
    const container = document.getElementById("toast-container");
    if (!container || !message) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${category}`;
    toast.innerHTML = `<span class="toast-dot"></span><div class="toast-text">${message}</div>`;
    container.appendChild(toast);
    announce(message);

    setTimeout(() => {
        toast.classList.add("leaving");
        setTimeout(() => toast.remove(), 220);
    }, 3200);
}
