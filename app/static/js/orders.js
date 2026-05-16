import { openModalById } from "./modals.js";

export function initClientModalFromUrl() {
    const meta = document.getElementById("clients-page-meta");
    if (meta && meta.dataset.openClientModal === "1") {
        openModalById("client-modal");
        return;
    }

    if (window.location.search.includes("phone=")) {
        const button = document.querySelector('[data-open-modal="client-modal"]');
        button?.click();
    }
}

export function initBuildModalState() {
    const meta = document.getElementById("builds-page-meta");
    if (meta?.dataset.openBuildModal === "1") {
        openModalById("build-modal");
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

export function initComponentModalState() {
    const meta = document.getElementById("components-page-meta");
    if (meta?.dataset.openComponentModal === "1") {
        openModalById("component-modal");
    }
}
