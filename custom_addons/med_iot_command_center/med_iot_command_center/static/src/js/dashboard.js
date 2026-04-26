/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";

function todayLabel() {
    return new Date().toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}

class MedDashboard extends Component {
    static template = "med_iot_command_center.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");

        this.state = useState({
            loading: true,
            lastRefresh: "",
            todayDate: todayLabel(),
            deviceCount: 0,
            searchQuery: "",
            statusFilter: "all",
            kpis: {
                total: 0,
                critical: 0,
                warning: 0,
                stable: 0,
                pending_alerts: 0,
            },
            live: [],
        });

        onMounted(() => {
            this._load();
            this._timer = setInterval(() => this._load(), 15000);
        });

        onWillUnmount(() => {
            if (this._timer) {
                clearInterval(this._timer);
            }
        });
    }

    get filteredLive() {
        let rows = this.state.live || [];
        const q = (this.state.searchQuery || "").trim().toLowerCase();
        const status = this.state.statusFilter || "all";

        if (q) {
            rows = rows.filter((p) => {
                const name = (p.name || "").toLowerCase();
                const ref = (p.ref || "").toLowerCase();
                const room = (p.room || "").toLowerCase();

                return name.includes(q) || ref.includes(q) || room.includes(q);
            });
        }

        if (status !== "all") {
            rows = rows.filter((p) => (p.status || "").toLowerCase() === status);
        }

        return rows;
    }

    onSearchInput(ev) {
        this.state.searchQuery = ev.target.value || "";
    }

    onStatusChange(ev) {
        this.state.statusFilter = ev.target.value || "all";
    }

    async _load() {
        try {
            const patients = await this.orm.searchRead(
                "med.patient",
                [],
                [
                    "name",
                    "ref",
                    "age",
                    "room",
                    "status",
                    "latest_temp",
                    "latest_spo2",
                    "latest_ecg_bpm",
                    "latest_reading_at",
                    "pending_alert_count",
                    "image_128",
                ],
                { order: "status desc, latest_reading_at desc, id desc" }
            );

            const alerts = await this.orm.searchCount("med.alert", [
                ["state", "!=", "resolved"],
            ]);

            const devices = await this.orm.searchCount("med.device", []);

            const total = patients.length;
            const critical = patients.filter((p) => p.status === "critical").length;
            const warning = patients.filter((p) => p.status === "warning").length;
            const stable = patients.filter((p) => p.status === "stable").length;

            this.state.kpis = {
                total,
                critical,
                warning,
                stable,
                pending_alerts: alerts,
            };

            this.state.deviceCount = devices;
            this.state.live = patients;
            this.state.lastRefresh = new Date().toLocaleTimeString();
            this.state.loading = false;
        } catch (e) {
            console.error("MedIoT dashboard error:", e);
            this.state.loading = false;
        }
    }

    openPatients() {
        this.actionService.doAction("med_iot_command_center.action_med_patient");
    }

    openAlerts() {
        this.actionService.doAction("med_iot_command_center.action_med_alerts");
    }

    openDevices() {
        this.actionService.doAction("med_iot_command_center.action_med_devices");
    }

    openCriticalPatients() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "med.patient",
            views: [[false, "list"], [false, "form"]],
            domain: [["status", "=", "critical"]],
            name: "Critical Patients",
        });
    }

    openWarningPatients() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "med.patient",
            views: [[false, "list"], [false, "form"]],
            domain: [["status", "=", "warning"]],
            name: "Warning Patients",
        });
    }

    openPatient(id) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "med.patient",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openPatientAlerts(id) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "med.alert",
            views: [[false, "list"], [false, "form"]],
            domain: [
                ["patient_id", "=", id],
                ["state", "!=", "resolved"],
            ],
            name: "Patient Alerts",
        });
    }

    async downloadPatientReport(patientId) {
        const patient = await this.orm.read("med.patient", [patientId], [
            "name",
            "ref",
            "age",
            "gender",
            "latest_spo2",
            "latest_ecg_bpm",
            "latest_temp",
        ]);

        if (patient && patient[0]) {
            const p = patient[0];
            const filename = `Patient_Report_${p.ref}_${new Date()
                .toISOString()
                .split("T")[0]}.pdf`;

            const url = `/report/pdf/med_iot_command_center.patient_medical_report/${patientId}`;

            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

registry.category("actions").add("med_iot_command_center.dashboard", MedDashboard);