/** @odoo-module **/

import { registry }   from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { session } from "@web/session";

const CIRC = 282.74;
function donutSegments(stable, warning, critical) {
    const total = stable + warning + critical || 1;
    const sFrac = stable / total, wFrac = warning / total, cFrac = critical / total;
    return {
        stableOffset:   CIRC * (1 - sFrac),
        warningOffset:  CIRC * (1 - wFrac),
        warningRotate:  -90 + sFrac * 360,
        criticalOffset: CIRC * (1 - cFrac),
        criticalRotate: -90 + (sFrac + wFrac) * 360,
    };
}

const MONTHS = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"];

function buildCalendar(year, month) {
    const today = new Date();
    const firstDay = new Date(year, month, 1);
    let startDow = firstDay.getDay();
    startDow = startDow === 0 ? 6 : startDow - 1;
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < startDow; i++) cells.push({ label: "", empty: true });
    for (let d = 1; d <= daysInMonth; d++) {
        const isToday = d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
        cells.push({ label: d, today: isToday });
    }
    while (cells.length % 7 !== 0) cells.push({ label: "", empty: true });
    return { label: MONTHS[month] + " " + year, cells, year, month };
}

function todayLabel() {
    return new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

// Build smooth SVG path using Catmull-Rom → Cubic Bezier conversion
function buildSmoothPath(points, w, h, minV, maxV) {
    if (points.length < 2) return "";
    const range = maxV - minV || 1;
    const pad = h * 0.08;
    const coords = points.map((v, i) => ({
        x: (i / (points.length - 1)) * w,
        y: (h - pad) - ((v - minV) / range) * (h - 2 * pad) + pad,
    }));
    let d = `M ${coords[0].x.toFixed(1)},${coords[0].y.toFixed(1)}`;
    for (let i = 0; i < coords.length - 1; i++) {
        const p0 = coords[Math.max(0, i - 1)];
        const p1 = coords[i];
        const p2 = coords[i + 1];
        const p3 = coords[Math.min(coords.length - 1, i + 2)];
        const cp1x = p1.x + (p2.x - p0.x) / 6;
        const cp1y = p1.y + (p2.y - p0.y) / 6;
        const cp2x = p2.x - (p3.x - p1.x) / 6;
        const cp2y = p2.y - (p3.y - p1.y) / 6;
        d += ` C ${cp1x.toFixed(1)},${cp1y.toFixed(1)} ${cp2x.toFixed(1)},${cp2y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`;
    }
    return d;
}

// Build area fill path (smooth curve closed to the bottom)
function buildSmoothAreaPath(points, w, h, minV, maxV) {
    const line = buildSmoothPath(points, w, h, minV, maxV);
    if (!line) return "";
    return `${line} L ${w},${h} L 0,${h} Z`;
}

class MedDashboard extends Component {
    static template = "med_iot_command_center.Dashboard";

    setup() {
        this.orm           = useService("orm");
        this.actionService = useService("action");

        const now = new Date();
        this.state = useState({
            loading:     true,
            userName:    session.name || "",
            lastRefresh: "",
            todayDate:   todayLabel(),
            deviceCount: 0,
            kpis:  { total: 0, critical: 0, warning: 0, stable: 0, pending_alerts: 0 },
            donut: { stableOffset: CIRC, warningOffset: CIRC, warningRotate: -90, criticalOffset: CIRC, criticalRotate: -90 },
            live:  [],
            cal:   buildCalendar(now.getFullYear(), now.getMonth()),
            chart: { spo2: [], ecg: [], temp: [], labels: [],
                     spo2Path: "", ecgPath: "", tempPath: "",
                     spo2Last: null, ecgLast: null, tempLast: null },
        });

        onMounted(() => { this._load(); this._timer = setInterval(() => this._load(), 15000); });
        onWillUnmount(() => clearInterval(this._timer));
    }

    async _load() {
        try {
            // WELCOME USER NAME PATCH
            if (!this.state.userName && session.uid) {
                try {
                    const users = await this.orm.read("res.users", [session.uid], ["name"]);
                    if (users && users[0] && users[0].name) {
                        this.state.userName = users[0].name;
                    }
                } catch (e) {}
            }
            const patients = await this.orm.searchRead(
                "med.patient", [],
                ["name", "ref", "age", "room", "status",
                 "latest_spo2", "latest_ecg_bpm", "latest_reading_at", "pending_alert_count", "image_128"],
                { order: "status desc, latest_reading_at desc" }
            );
            const alerts  = await this.orm.searchCount("med.alert", [["state", "=", "new"]]);
            const devices = await this.orm.searchCount("med.device", [["status", "=", "online"]]);

            // Fetch last 20 vital readings for the line chart (with fallback)
            let readings = [];
            try {
                readings = await this.orm.searchRead(
                    "med.vital.reading", [],
                    ["reading_at", "spo2", "ecg_bpm", "temp_c"],
                    { order: "reading_at asc", limit: 20 }
                );
            } catch(e) { readings = []; }

            const total    = patients.length;
            const critical = patients.filter(p => p.status === "critical").length;
            const warning  = patients.filter(p => p.status === "warning").length;
            const stable   = patients.filter(p => p.status === "stable").length;

            // Build chart data
            const W = 560, H = 100;
            const spo2Vals  = readings.map(r => r.spo2    || 0).filter(v => v > 0);
            const ecgVals   = readings.map(r => r.ecg_bpm || 0).filter(v => v > 0);
            const tempVals  = readings.map(r => r.temp_c || 0).filter(v => v > 0);
            const labels    = readings.map(r => r.reading_at ? r.reading_at.substring(11,16) : "");

            const spo2Min = Math.min(...spo2Vals) - 2, spo2Max = Math.max(...spo2Vals) + 2;
            const ecgMin  = Math.min(...ecgVals)  - 5, ecgMax  = Math.max(...ecgVals)  + 5;
            const tempMin = Math.min(...tempVals) - 1, tempMax = Math.max(...tempVals) + 1;

            const spo2Path     = spo2Vals.length > 1 ? buildSmoothPath(spo2Vals, W, H, spo2Min, spo2Max) : "";
            const ecgPath      = ecgVals.length  > 1 ? buildSmoothPath(ecgVals,  W, H, ecgMin,  ecgMax)  : "";
            const tempPath     = tempVals.length > 1 ? buildSmoothPath(tempVals, W, H, tempMin, tempMax) : "";
            const spo2AreaPath = spo2Vals.length > 1 ? buildSmoothAreaPath(spo2Vals, W, H, spo2Min, spo2Max) : "";
            const ecgAreaPath  = ecgVals.length  > 1 ? buildSmoothAreaPath(ecgVals,  W, H, ecgMin,  ecgMax)  : "";
            const tempAreaPath = tempVals.length > 1 ? buildSmoothAreaPath(tempVals, W, H, tempMin, tempMax) : "";

            this.state.kpis        = { total, critical, warning, stable, pending_alerts: alerts };
            this.state.donut       = donutSegments(stable, warning, critical);
            this.state.deviceCount = devices;
            this.state.live        = patients;
            this.state.lastRefresh = new Date().toLocaleTimeString();
            this.state.loading     = false;
            this.state.chart       = {
                spo2: spo2Vals, ecg: ecgVals, temp: tempVals, labels,
                spo2Path, ecgPath, tempPath,
                spo2AreaPath, ecgAreaPath, tempAreaPath,
                spo2Last:  spo2Vals.length ? spo2Vals[spo2Vals.length - 1] : null,
                ecgLast:   ecgVals.length  ? ecgVals[ecgVals.length - 1]   : null,
                tempLast:  tempVals.length ? tempVals[tempVals.length - 1] : null,
            };
        } catch (e) {
            console.error("MedIoT dashboard error:", e);
            this.state.loading = false;
        }
    }

    calPrev() {
        let { year, month } = this.state.cal;
        month--; if (month < 0) { month = 11; year--; }
        this.state.cal = buildCalendar(year, month);
    }
    calNext() {
        let { year, month } = this.state.cal;
        month++; if (month > 11) { month = 0; year++; }
        this.state.cal = buildCalendar(year, month);
    }

    openPatients()  { this.actionService.doAction("med_iot_command_center.action_med_patient"); }
    openAlerts()    { this.actionService.doAction("med_iot_command_center.action_med_alerts"); }
    openDevices()   { this.actionService.doAction("med_iot_command_center.action_med_devices"); }
    openCriticalPatients() {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.patient",
            views: [[false,"list"],[false,"form"]], domain: [["status","=","critical"]], name: "Critical Patients" });
    }
    openWarningPatients() {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.patient",
            views: [[false,"list"],[false,"form"]], domain: [["status","=","warning"]], name: "Warning Patients" });
    }
    openPatient(id) {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.patient",
            res_id: id, views: [[false,"form"]], target: "current" });
    }
    openPatientAlerts(id) {
        this.actionService.doAction({ type: "ir.actions.act_window", res_model: "med.alert",
            views: [[false,"list"],[false,"form"]], domain: [["patient_id","=",id],["state","=","new"]], name: "Patient Alerts" });
    }

    async downloadPatientReport(patientId) {
        const ctx = this.env.services.orm;
        const patient = await ctx.read("med.patient", [patientId], ["name", "ref", "age", "gender", "latest_spo2", "latest_ecg_bpm", "latest_temp"]);
        if (patient && patient[0]) {
            const p = patient[0];
            const filename = `Patient_Report_${p.ref}_${new Date().toISOString().split('T')[0]}.pdf`;
            const url = `/report/pdf/med_iot_command_center.patient_medical_report/${patientId}`;
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

registry.category("actions").add("med_iot_command_center.dashboard", MedDashboard);
