import { normalizePhone } from "./utils.js";

export function initSortableTables() {
    document.querySelectorAll(".sortable-table").forEach((table) => {
        const headers = table.querySelectorAll("th[data-sort]");
        headers.forEach((header, index) => {
            header.addEventListener("click", () => sortTable(table, index, header.dataset.sort || "text", header));
        });
    });
}

function sortTable(table, columnIndex, type, activeHeader) {
    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll("tr")).filter((row) => row.querySelector("td"));
    const currentDirection = activeHeader.dataset.direction === "asc" ? "desc" : "asc";

    table.querySelectorAll("th").forEach((th) => {
        th.classList.remove("is-sorted-asc", "is-sorted-desc");
        delete th.dataset.direction;
    });

    rows.sort((left, right) => {
        const leftCell = left.children[columnIndex];
        const rightCell = right.children[columnIndex];
        const leftValue = leftCell?.dataset.sortValue || leftCell?.textContent.trim() || "";
        const rightValue = rightCell?.dataset.sortValue || rightCell?.textContent.trim() || "";

        if (type === "number") {
            const diff = Number(leftValue) - Number(rightValue);
            return currentDirection === "asc" ? diff : -diff;
        }

        return currentDirection === "asc"
            ? leftValue.localeCompare(rightValue, "uk")
            : rightValue.localeCompare(leftValue, "uk");
    });

    rows.forEach((row) => tbody.appendChild(row));
    activeHeader.dataset.direction = currentDirection;
    activeHeader.classList.add(currentDirection === "asc" ? "is-sorted-asc" : "is-sorted-desc");
    renderPaginatedTable(table);
}

export function initTableFilters() {
    document.querySelectorAll("[data-table-filter]").forEach((input) => {
        input.addEventListener("input", () => {
            const table = document.getElementById(input.dataset.tableFilter);
            if (!table) return;
            const term = input.value.trim().toLowerCase();
            table.querySelectorAll("tbody tr").forEach((row) => {
                if (row.querySelector(".empty-state")) return;
                const content = row.textContent.toLowerCase();
                row.dataset.filteredOut = !term || content.includes(term) ? "false" : "true";
            });
            table.dataset.currentPage = "1";
            renderPaginatedTable(table);
        });
    });
}

export function initTablePagination() {
    document.querySelectorAll(".sortable-table[data-page-size]").forEach((table) => {
        const pageSize = Number.parseInt(table.dataset.pageSize || "", 10);
        if (!pageSize || pageSize < 1) return;

        const wrapper = table.closest(".table-wrap");
        if (!wrapper) return;

        let pagination = wrapper.nextElementSibling;
        if (!pagination || !pagination.classList.contains("table-pagination")) {
            pagination = document.createElement("div");
            pagination.className = "table-pagination";
            pagination.innerHTML = `
                <div class="pagination-meta" aria-live="polite"></div>
                <div class="pagination-actions">
                    <button class="btn btn-ghost btn-sm" type="button" data-pagination-action="prev">Назад</button>
                    <button class="btn btn-ghost btn-sm" type="button" data-pagination-action="next">Далі</button>
                </div>
            `;
            wrapper.insertAdjacentElement("afterend", pagination);
        }

        pagination.querySelector('[data-pagination-action="prev"]')?.addEventListener("click", () => {
            const currentPage = Number.parseInt(table.dataset.currentPage || "1", 10);
            table.dataset.currentPage = String(Math.max(1, currentPage - 1));
            renderPaginatedTable(table);
        });

        pagination.querySelector('[data-pagination-action="next"]')?.addEventListener("click", () => {
            const currentPage = Number.parseInt(table.dataset.currentPage || "1", 10);
            table.dataset.currentPage = String(currentPage + 1);
            renderPaginatedTable(table);
        });

        renderPaginatedTable(table);
    });
}

export function renderPaginatedTable(table) {
    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    const pageSize = Number.parseInt(table.dataset.pageSize || "", 10);
    if (!pageSize || pageSize < 1) return;

    const pagination = table.closest(".table-wrap")?.nextElementSibling;
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const dataRows = rows.filter((row) => row.querySelector("td") && !row.querySelector(".empty-state"));
    const emptyRow = rows.find((row) => row.querySelector(".empty-state"));
    const visibleRows = dataRows.filter((row) => row.dataset.filteredOut !== "true");

    if (!visibleRows.length) {
        dataRows.forEach((row) => {
            row.style.display = "none";
        });
        if (emptyRow) {
            emptyRow.style.display = "";
        }
        if (pagination) pagination.hidden = true;
        return;
    }

    if (emptyRow) {
        emptyRow.style.display = "none";
    }

    const totalPages = Math.max(1, Math.ceil(visibleRows.length / pageSize));
    const currentPage = Math.min(
        totalPages,
        Math.max(1, Number.parseInt(table.dataset.currentPage || "1", 10)),
    );
    table.dataset.currentPage = String(currentPage);

    dataRows.forEach((row) => {
        row.style.display = row.dataset.filteredOut === "true" ? "none" : "";
    });

    visibleRows.forEach((row, index) => {
        const page = Math.floor(index / pageSize) + 1;
        row.style.display = page === currentPage ? "" : "none";
    });

    if (!pagination) return;

    const meta = pagination.querySelector(".pagination-meta");
    const prevButton = pagination.querySelector('[data-pagination-action="prev"]');
    const nextButton = pagination.querySelector('[data-pagination-action="next"]');

    pagination.hidden = visibleRows.length <= pageSize;
    if (meta) {
        const start = (currentPage - 1) * pageSize + 1;
        const end = Math.min(currentPage * pageSize, visibleRows.length);
        meta.textContent = `Показано ${start}-${end} з ${visibleRows.length}`;
    }
    if (prevButton) prevButton.disabled = currentPage <= 1;
    if (nextButton) nextButton.disabled = currentPage >= totalPages;
}

export function initPhoneAutoSearch() {
    const input = document.querySelector("[data-phone-autosearch]");
    const table = document.getElementById("order-clients-table");
    if (!input || !table) return;

    const rows = Array.from(table.querySelectorAll("tbody tr")).filter((row) => !row.querySelector(".empty-state"));

    const applyFilter = () => {
        const normalizedQuery = normalizePhone(input.value.trim());

        rows.forEach((row) => {
            const phoneCell = row.querySelector('[data-phone-cell="true"]');
            const normalizedPhone = normalizePhone(phoneCell?.textContent || "");
            const matches = !normalizedQuery || normalizedPhone.includes(normalizedQuery);
            row.dataset.filteredOut = matches ? "false" : "true";
        });

        table.dataset.currentPage = "1";
        renderPaginatedTable(table);
    };

    input.addEventListener("input", applyFilter);
    applyFilter();
}
