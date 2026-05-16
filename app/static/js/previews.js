import { findById, parseJsonScript } from "./utils.js";

const paymentStatusLabels = {
    paid: "Сплачено",
    unpaid: "Не сплачено",
};

const orderStatusLabels = {
    ready: "Готово",
    not_ready: "Не готово",
};

export function initBuildPreview() {
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

export function initOrderPreview() {
    const builds = parseJsonScript("builds-json");
    const clients = parseJsonScript("clients-json");
    const preview = document.getElementById("order-preview");
    if (!builds || !clients || !preview) return;

    const controls = document.querySelectorAll("[data-order-control]");
    const render = () => {
        const client = findById(clients, document.getElementById("order-client-id")?.value);
        const build = findById(builds, document.getElementById("order-build-id")?.value);
        const productionDeadline = document.getElementById("production_deadline")?.value;
        const paymentStatus = document.getElementById("payment_status")?.value;
        const orderStatus = document.getElementById("order_status")?.value;

        if (!client || !build) {
            preview.innerHTML = `
                <div class="preview-title">Попередній перегляд замовлення</div>
                <div class="preview-empty">Оберіть клієнта, збірку та статус оплати, щоб побачити підсумок і суму до сплати.</div>
            `;
            return;
        }

        const dueAmount = paymentStatus === "unpaid" ? Number(build.price || 0) : 0;
        const estimatedDays = calculateEstimatedDays(productionDeadline);
        preview.innerHTML = `
            <div class="preview-title">Замовлення для ${client.full_name}</div>
            <div class="preview-list">
                <div class="preview-row"><span>Телефон</span><span>${client.phone}</span></div>
                <div class="preview-row"><span>Збірка</span><span>${build.build_type} · ${build.gpu_name}</span></div>
                <div class="preview-row"><span>Орієнтовна ціна</span><span>${Number(build.price || 0).toFixed(2)} грн</span></div>
                <div class="preview-row"><span>Завершення</span><span>${formatDeadline(productionDeadline)}</span></div>
                <div class="preview-row"><span>Оцінка тривалості</span><span>${estimatedDays}</span></div>
                <div class="preview-row"><span>Статус оплати</span><span>${paymentStatusLabels[paymentStatus] || "—"}</span></div>
                <div class="preview-row"><span>Статус замовлення</span><span>${orderStatusLabels[orderStatus] || "—"}</span></div>
                <div class="preview-row total"><span>Сума до сплати</span><span>${dueAmount.toFixed(2)} грн</span></div>
            </div>
        `;
    };

    controls.forEach((control) => control.addEventListener("input", render));
    controls.forEach((control) => control.addEventListener("change", render));
}

function calculateEstimatedDays(deadlineValue) {
    if (!deadlineValue) return "—";

    const deadline = new Date(deadlineValue);
    const now = new Date();
    const diffMs = deadline.getTime() - now.getTime();
    if (Number.isNaN(deadline.getTime()) || diffMs <= 0) {
        return "—";
    }

    const days = Math.max(1, Math.ceil(diffMs / 86400000));
    return `${days} дн.`;
}

function formatDeadline(deadlineValue) {
    if (!deadlineValue) return "—";

    const deadline = new Date(deadlineValue);
    if (Number.isNaN(deadline.getTime())) {
        return "—";
    }

    return deadline.toLocaleString("uk-UA", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
    });
}
