import { initModals } from "./modals.js";
import { initBuildModalState, initClientModalFromUrl, initComponentModalState, initOrderModalState } from "./orders.js";
import { initBuildPreview, initOrderPreview } from "./previews.js";
import { initShellLoading, initSidebar } from "./shell.js";
import { initPhoneAutoSearch, initSortableTables, initTableFilters, initTablePagination } from "./tables.js";
import { initToasts } from "./toasts.js";

document.addEventListener("DOMContentLoaded", () => {
    initShellLoading();
    initSidebar();
    initToasts();
    initModals();
    initSortableTables();
    initTableFilters();
    initTablePagination();
    initPhoneAutoSearch();
    initBuildPreview();
    initOrderPreview();
    initClientModalFromUrl();
    initBuildModalState();
    initOrderModalState();
    initComponentModalState();
});
