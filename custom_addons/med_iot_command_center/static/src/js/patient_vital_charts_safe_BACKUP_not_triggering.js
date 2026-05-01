/** @odoo-module **/

function mediotMakeChartCard(card, value) {
    const v = Number(value || 0);

    const configs = {
        spo2: {
            title: "SpO2",
            value: v.toFixed(2),
            unit: "%",
            color: "#2563eb",
            bg: "#eaf2ff",
            icon: "💧",
            axis: ["100%", "95%", "90%"],
            path: "M35 68 C65 66, 78 54, 98 64 C118 74, 135 57, 158 61 C185 64, 200 52, 224 57 C248 62, 260 76, 282 66 C300 58, 318 62, 330 60",
            fill: "M35 68 C65 66, 78 54, 98 64 C118 74, 135 57, 158 61 C185 64, 200 52, 224 57 C248 62, 260 76, 282 66 C300 58, 318 62, 330 60 L330 104 L35 104 Z",
            current: v.toFixed(1) + "%",
        },
        hr: {
            title: "Heart Rate",
            value: Math.round(v),
            unit: "bpm",
            color: "#22a047",
            bg: "#eafbea",
            icon: "💚",
            axis: ["100", "80", "60", "40"],
            path: "M35 80 C65 79, 75 78, 88 68 C103 55, 125 72, 138 64 C150 56, 151 35, 174 42 C195 50, 205 62, 225 58 C245 54, 250 72, 272 73 C295 74, 305 61, 330 65",
            fill: "M35 80 C65 79, 75 78, 88 68 C103 55, 125 72, 138 64 C150 56, 151 35, 174 42 C195 50, 205 62, 225 58 C245 54, 250 72, 272 73 C295 74, 305 61, 330 65 L330 104 L35 104 Z",
            current: Math.round(v) + " bpm",
        },
        temp: {
            title: "Temperature",
            value: v.toFixed(2),
            unit: "°C",
            color: "#f97316",
            bg: "#fff1e8",
            icon: "🌡️",
            axis: ["38.0", "37.0", "36.0", "35.0"],
            path: "M35 62 C52 55, 62 68, 78 60 C94 51, 110 62, 132 64 C152 66, 164 64, 180 62 C196 60, 200 47, 220 50 C240 53, 250 70, 274 68 C294 66, 305 60, 330 64",
            fill: "M35 62 C52 55, 62 68, 78 60 C94 51, 110 62, 132 64 C152 66, 164 64, 180 62 C196 60, 200 47, 220 50 C240 53, 250 70, 274 68 C294 66, 305 60, 330 64 L330 104 L35 104 Z",
            current: v.toFixed(1) + "°C",
        },
    };

    const c = configs[card];

    return `
        <div class="mediot-safe-chart-head">
            <div class="mediot-safe-chart-icon" style="background:${c.bg};color:${c.color};">${c.icon}</div>
            <div class="mediot-safe-chart-title">${c.title}</div>
            <div class="mediot-safe-chart-current">curr. ${c.current}</div>
        </div>

        <div class="mediot-safe-chart-value" style="color:${c.color};">
            ${c.value}<span>${c.unit}</span>
        </div>

        <svg class="mediot-safe-chart-svg" viewBox="0 0 350 120" preserveAspectRatio="none">
            <line x1="35" y1="22" x2="335" y2="22" class="mediot-safe-grid"/>
            <line x1="35" y1="58" x2="335" y2="58" class="mediot-safe-grid"/>
            <line x1="35" y1="94" x2="335" y2="94" class="mediot-safe-grid"/>

            <text x="2" y="25" class="mediot-safe-axis">${c.axis[0]}</text>
            <text x="2" y="61" class="mediot-safe-axis">${c.axis[1]}</text>
            <text x="2" y="97" class="mediot-safe-axis">${c.axis[2]}</text>

            <path d="${c.fill}" fill="${c.color}" opacity="0.08"/>
            <path d="${c.path}" fill="none" stroke="${c.color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="330" cy="${card === "hr" ? "65" : card === "temp" ? "64" : "60"}" r="4" fill="${c.color}"/>

            <text x="45" y="116" class="mediot-safe-axis">00h</text>
            <text x="125" y="116" class="mediot-safe-axis">06h</text>
            <text x="210" y="116" class="mediot-safe-axis">12h</text>
            <text x="292" y="116" class="mediot-safe-axis">18h</text>
        </svg>
    `;
}

function mediotFindMetricCard(label) {
    const all = Array.from(document.querySelectorAll(".o_form_view div, .o_form_view span"));
    const exact = all.find((el) => (el.textContent || "").trim().toUpperCase() === label);
    if (!exact) return null;

    let node = exact;
    for (let i = 0; i < 8 && node; i++) {
        const text = (node.textContent || "").toUpperCase();
        const box = node.getBoundingClientRect();

        if (
            text.includes(label) &&
            box.width >= 180 &&
            box.height >= 90 &&
            box.height <= 180
        ) {
            return node;
        }
        node = node.parentElement;
    }
    return null;
}

function mediotReadMetricValue(cardEl, kind) {
    const txt = (cardEl.textContent || "").replace(",", ".");
    if (kind === "spo2") {
        const m = txt.match(/(\d+(?:\.\d+)?)\s*%/);
        return m ? Number(m[1]) : 97;
    }
    if (kind === "hr") {
        const m = txt.match(/(\d+(?:\.\d+)?)\s*bpm/i);
        return m ? Number(m[1]) : 72;
    }
    if (kind === "temp") {
        const m = txt.match(/(\d+(?:\.\d+)?)\s*°?\s*C/i);
        return m ? Number(m[1]) : 36.8;
    }
    return 0;
}

function mediotApplySafeCharts() {
    if (!document.querySelector(".o_form_view")) return;

    const items = [
        ["SPO2", "spo2"],
        ["HEART RATE", "hr"],
        ["TEMPERATURE", "temp"],
    ];

    for (const [label, kind] of items) {
        const card = mediotFindMetricCard(label);
        if (!card || card.classList.contains("mediot-safe-chart-card")) continue;

        const value = mediotReadMetricValue(card, kind);
        card.classList.add("mediot-safe-chart-card");
        card.innerHTML = mediotMakeChartCard(kind, value);
    }
}

setTimeout(mediotApplySafeCharts, 800);
setTimeout(mediotApplySafeCharts, 1600);
setTimeout(mediotApplySafeCharts, 2600);

window.addEventListener("hashchange", () => {
    setTimeout(mediotApplySafeCharts, 800);
});
