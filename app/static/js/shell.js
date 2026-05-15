export function initShellLoading() {
    window.requestAnimationFrame(() => {
        document.getElementById("app-shell")?.classList.remove("shell-loading");
    });
}

export function initSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");
    const openButtons = document.querySelectorAll("[data-sidebar-open]");

    if (!sidebar || !overlay) return;

    const openSidebar = () => {
        sidebar.classList.add("open");
        overlay.classList.add("open");
        document.body.style.overflow = "hidden";
    };

    const closeSidebar = () => {
        sidebar.classList.remove("open");
        overlay.classList.remove("open");
        document.body.style.overflow = "";
    };

    openButtons.forEach((button) => button.addEventListener("click", openSidebar));
    overlay.addEventListener("click", closeSidebar);
}
