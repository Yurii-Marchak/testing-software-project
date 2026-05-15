export function parseJsonScript(id) {
    const node = document.getElementById(id);
    if (!node) return null;
    try {
        return JSON.parse(node.textContent);
    } catch {
        return null;
    }
}

export function normalizePhone(value) {
    return String(value || "").replace(/\D/g, "");
}

export function findById(items, id) {
    return items.find((item) => String(item.id) === String(id));
}

export function announce(text) {
    const region = document.getElementById("aria-live-region");
    if (region) {
        region.textContent = text;
    }
}
