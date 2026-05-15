export function closeModalById(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
}

export function openModalById(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const focusTarget = modal.querySelector("input, select, button, textarea");
    focusTarget?.focus();
}

export function initModals() {
    document.querySelectorAll("[data-open-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            openModalById(button.dataset.openModal);
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            const overlay = button.closest(".modal-overlay");
            if (overlay?.id) closeModalById(overlay.id);
        });
    });

    document.querySelectorAll(".modal-overlay").forEach((overlay) => {
        overlay.addEventListener("click", (event) => {
            if (event.target === overlay) {
                closeModalById(overlay.id);
            }
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        document.querySelectorAll(".modal-overlay.open").forEach((overlay) => {
            closeModalById(overlay.id);
        });
    });
}
