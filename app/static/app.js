function parseJsonScript(id) {
    const node = document.getElementById(id);
    if (!node) return null;
    try {
        return JSON.parse(node.textContent);
    } catch {
        return null;
    }
}

function normalizePhone(value) {
    return String(value || "").replace(/\D/g, "");
}

function initShellLoading() {
    window.requestAnimationFrame(() => {
        document.getElementById("app-shell")?.classList.remove("shell-loading");
    });
}

function announce(text) {
    const region = document.getElementById("aria-live-region");
    if (region) {
        region.textContent = text;
    }
}

function initToasts() {
    const stack = document.querySelector(".js-flash-stack");
    if (!stack) return;
    const flashes = Array.from(stack.querySelectorAll(".flash"));
    flashes.forEach((flash) => {
        showToast(flash.textContent.trim(), flash.dataset.flashCategory || "info");
    });
}

function showToast(message, category = "info") {
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

function closeModalById(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
}

function openModalById(id) {
    const modal = document.getElementById(id);
    if (!modal) return;
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    const focusTarget = modal.querySelector("input, select, button, textarea");
    focusTarget?.focus();
}

function initModals() {
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

function initSortableTables() {
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

function initTableFilters() {
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

function initTablePagination() {
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

function renderPaginatedTable(table) {
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

function initPhoneAutoSearch() {
    const input = document.querySelector("[data-phone-autosearch]");
    const table = document.getElementById("order-clients-table");
    if (!input || !table) return;

    const rows = Array.from(table.querySelectorAll("tbody tr")).filter((row) => !row.querySelector(".empty-state"));

    const applyFilter = () => {
        const normalizedQuery = normalizePhone(input.value.trim());

        rows.forEach((row) => {
            const phoneCell = row.querySelector('td[data-label="Телефон"]');
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

function findById(items, id) {
    return items.find((item) => String(item.id) === String(id));
}

function initBuildPreview() {
    const catalog = parseJsonScript("build-catalog-json");
    const preview = document.getElementById("build-preview");
    if (!catalog || !preview) return;

    const controls = document.querySelectorAll("[data-build-control]");
    const render = () => {
        const gpu = findById(catalog.gpu || [], document.getElementById("gpu_id")?.value);
        const cpu = findById(catalog.cpu || [], document.getElementById("cpu_id")?.value);
        const motherboard = findById(catalog.motherboard || [], document.getElementById("motherboard_id")?.value);
        const ram = findById(catalog.ram || [], document.getElementById("ram_id")?.value);
        const psu = findById(catalog.psu || [], document.getElementById("psu_id")?.value);
        const pcCase = findById(catalog.pc_case || [], document.getElementById("pc_case_id")?.value);
        const buildType = document.getElementById("build_type")?.value.trim() || "Нова збірка";

        const parts = [gpu, cpu, motherboard, ram, psu, pcCase];
        if (parts.some((part) => !part)) {
            preview.innerHTML = `
                <div class="preview-title">Попередній перегляд збірки</div>
                <div class="preview-empty">Оберіть комплектуючі, щоб побачити ціну, склад і перевірки сумісності.</div>
            `;
            return;
        }

        const total = parts.reduce((sum, part) => sum + Number(part.price || 0), 0);
        const warnings = [];
        if (motherboard.ram_type !== ram.ram_type) {
            warnings.push("Тип RAM не збігається з підтримкою материнської плати.");
        }
        if (gpu.recommended_psu_power > psu.power) {
            warnings.push("Потужність блока живлення нижча за рекомендовану для вибраної відеокарти.");
        }

        preview.innerHTML = `
            <div class="preview-title">${buildType}</div>
            <div class="preview-list">
                <div class="preview-row"><span>GPU</span><span>${gpu.model_name}</span></div>
                <div class="preview-row"><span>CPU</span><span>${cpu.model_name}</span></div>
                <div class="preview-row"><span>Материнська плата</span><span>${motherboard.model_name}</span></div>
                <div class="preview-row"><span>RAM</span><span>${ram.model_name}</span></div>
                <div class="preview-row"><span>PSU</span><span>${psu.model_name}</span></div>
                <div class="preview-row"><span>Корпус</span><span>${pcCase.model_name}</span></div>
                <div class="preview-row total"><span>Орієнтовна ціна</span><span>${total.toFixed(2)} грн</span></div>
            </div>
            ${
                warnings.length
                    ? warnings.map((warning) => `<div class="preview-alert">${warning}</div>`).join("")
                    : `<div class="preview-alert success">Сумісність виглядає коректною для базового сценарію.</div>`
            }
        `;
    };

    controls.forEach((control) => control.addEventListener("input", render));
    controls.forEach((control) => control.addEventListener("change", render));
}

function initOrderPreview() {
    const builds = parseJsonScript("builds-json");
    const clients = parseJsonScript("clients-json");
    const preview = document.getElementById("order-preview");
    if (!builds || !clients || !preview) return;

    const controls = document.querySelectorAll("[data-order-control]");
    const render = () => {
        const client = findById(clients, document.getElementById("order-client-id")?.value);
        const build = findById(builds, document.getElementById("order-build-id")?.value);
        const productionTime = document.getElementById("production_time")?.value;
        const paymentStatus = document.getElementById("payment_status")?.value;
        const orderStatus = document.getElementById("order_status")?.value;

        if (!client || !build) {
            preview.innerHTML = `
                <div class="preview-title">Попередній перегляд замовлення</div>
                <div class="preview-empty">Оберіть клієнта, збірку та статус оплати, щоб побачити підсумок і суму до сплати.</div>
            `;
            return;
        }

        const dueAmount = paymentStatus === "Не сплачено" ? Number(build.price || 0) : 0;
        preview.innerHTML = `
            <div class="preview-title">Замовлення для ${client.full_name}</div>
            <div class="preview-list">
                <div class="preview-row"><span>Телефон</span><span>${client.phone}</span></div>
                <div class="preview-row"><span>Збірка</span><span>${build.build_type} · ${build.gpu_name}</span></div>
                <div class="preview-row"><span>Орієнтовна ціна</span><span>${Number(build.price || 0).toFixed(2)} грн</span></div>
                <div class="preview-row"><span>Час зборки</span><span>${productionTime || "—"} дн.</span></div>
                <div class="preview-row"><span>Статус оплати</span><span>${paymentStatus || "—"}</span></div>
                <div class="preview-row"><span>Статус замовлення</span><span>${orderStatus || "—"}</span></div>
                <div class="preview-row total"><span>Сума до сплати</span><span>${dueAmount.toFixed(2)} грн</span></div>
            </div>
        `;
    };

    controls.forEach((control) => control.addEventListener("input", render));
    controls.forEach((control) => control.addEventListener("change", render));
}

function initClientModalFromUrl() {
    if (window.location.search.includes("phone=")) {
        const button = document.querySelector('[data-open-modal="client-modal"]');
        button?.click();
    }
}

function initOrderModalState() {
    const meta = document.getElementById("orders-page-meta");
    if (!meta || meta.dataset.openOrderModal !== "1") return;

    openModalById("order-modal");

    const clientSelect = document.getElementById("order-client-id");
    if (clientSelect && meta.dataset.createdClientId) {
        clientSelect.value = meta.dataset.createdClientId;
        clientSelect.dispatchEvent(new Event("change", { bubbles: true }));
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initShellLoading();
    initToasts();
    initModals();
    initSortableTables();
    initTableFilters();
    initTablePagination();
    initPhoneAutoSearch();
    initBuildPreview();
    initOrderPreview();
    initClientModalFromUrl();
    initOrderModalState();
});
