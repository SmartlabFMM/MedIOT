
/** @odoo-module **/

function normalizeAlertPills(root) {
    // Top severity badge
    root.querySelectorAll(".o_med_alert_card").forEach((card) => {
        const badge = card.querySelector(".o_med_alert_badge");
        if (badge) {
            const txt = (badge.textContent || "").trim().toLowerCase();
            if (txt.includes("warning")) {
                badge.classList.add("badge-warning", "med_force_warning_badge");
            } else if (txt.includes("critical")) {
                badge.classList.add("badge-critical", "med_force_critical_badge");
            }
        }

        // Footer "new" pill
        const state = card.querySelector(".o_med_alert_state");
        if (state) {
            const txt = (state.textContent || "").trim().toLowerCase();
            if (txt.includes("new")) {
                state.classList.add("state-new", "med_force_state_new");
                if (!state.querySelector(".o_med_alert_dot")) {
                    const dot = document.createElement("span");
                    dot.className = "o_med_alert_dot";
                    state.prepend(dot);
                }
            }
        }
    });
}

function setupAlertGroupToggles(root) {
    const groups = root.querySelectorAll(".o_med_alert_kanban .o_kanban_group");

    groups.forEach((group) => {
        const header = group.querySelector(".o_kanban_group_header, .o_kanban_header");
        if (!header) return;

        const records = Array.from(group.querySelectorAll(":scope .o_kanban_record"));
        if (!records.length) return;

        // keep only direct-ish visible records inside this group
        const cards = records.filter(r => r.querySelector(".o_med_alert_card"));
        if (!cards.length) return;

        const extraCards = cards.slice(1);

        // remove old toggle if any
        const oldBtn = header.querySelector(".med_alert_group_toggle");
        if (oldBtn) oldBtn.remove();

        // if only 1 alert, no toggle needed
        if (extraCards.length === 0) {
            return;
        }

        // default state = collapsed
        let expanded = false;
        extraCards.forEach((rec) => rec.classList.add("med_alert_extra_hidden"));

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "med_alert_group_toggle";
        btn.setAttribute("title", "Show more alerts");
        btn.textContent = "+";

        btn.addEventListener("click", () => {
            expanded = !expanded;
            extraCards.forEach((rec) => {
                rec.classList.toggle("med_alert_extra_hidden", !expanded);
            });
            btn.textContent = expanded ? "?" : "+";
            btn.setAttribute("title", expanded ? "Hide extra alerts" : "Show more alerts");
        });

        header.appendChild(btn);
    });
}

function applyAlertEnhancements() {
    const root = document;
    normalizeAlertPills(root);
    setupAlertGroupToggles(root);
}

function boot() {
    applyAlertEnhancements();

    const observer = new MutationObserver(() => {
        applyAlertEnhancements();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
} else {
    boot();
}
