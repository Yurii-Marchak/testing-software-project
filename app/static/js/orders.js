import { openModalById } from "./modals.js";

export function initClientModalFromUrl() {
    if (window.location.search.includes("phone=")) {
        const button = document.querySelector('[data-open-modal="client-modal"]');
        button?.click();
    }
}

export function initOrderModalState() {
    const meta = document.getElementById("orders-page-meta");
    if (!meta || meta.dataset.openOrderModal !== "1") return;

    openModalById("order-modal");

    const clientSelect = document.getElementById("order-client-id");
    if (clientSelect && meta.dataset.createdClientId) {
        clientSelect.value = meta.dataset.createdClientId;
        clientSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }
}
