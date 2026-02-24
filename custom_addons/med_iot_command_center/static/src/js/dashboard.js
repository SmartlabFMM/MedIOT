/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class MedDashboard extends Component {
    static template = "med_iot_command_center.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            kpis: { total: 0, critical: 0, pending_alerts: 0 },
            live: [],
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;

        const total = await this.orm.searchCount("med.patient", [["active", "=", true]]);
        const critical = await this.orm.searchCount("med.patient", [["status", "=", "critical"], ["active", "=", true]]);
        const pending_alerts = await this.orm.searchCount("med.alert", [["state", "=", "new"]]);

        const live = await this.orm.searchRead(
            "med.patient",
            [["active", "=", true]],
            ["name", "ref", "room", "status", "latest_temp", "latest_spo2", "latest_ecg_bpm", "latest_reading_at"],
            { limit: 8, order: "latest_reading_at desc" }
        );

        this.state.kpis = { total, critical, pending_alerts };
        this.state.live = live;
        this.state.loading = false;
    }

    openPatients() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Patients",
            res_model: "med.patient",
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    openAlerts() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Real-time Alerts",
            res_model: "med.alert",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "!=", "resolved"]],
            target: "current",
        });
    }

    openPatient(patientId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "med.patient",
            res_id: patientId,
            views: [[false, "form"]],
        });
    }
}

registry.category("actions").add("med_iot_command_center.dashboard", MedDashboard);
