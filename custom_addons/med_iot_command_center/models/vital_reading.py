# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MedVitalReading(models.Model):
    _name = "med.vital.reading"
    _description = "Vital Reading"
    _order = "reading_at desc"

    patient_id = fields.Many2one("med.patient", required=True, ondelete="cascade", index=True)
    device_id = fields.Many2one("med.device", index=True)

    reading_at = fields.Datetime(default=fields.Datetime.now, required=True, index=True)

    temp_c = fields.Float(string="Temp (°C)")
    spo2 = fields.Float(string="SpO2 (%)")
    ecg_bpm = fields.Integer(string="ECG (BPM)")

    raw_payload = fields.Text(help="Optional: store raw MQTT/JSON payload")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        # Update patient latest values
        for r in records:
            r.patient_id.sudo().write({
                "latest_temp": r.temp_c,
                "latest_spo2": r.spo2,
                "latest_ecg_bpm": r.ecg_bpm,
                "latest_reading_at": r.reading_at,
            })

        # Placeholder: Evaluate thresholds and create alerts
        records._evaluate_thresholds_and_create_alerts()

        return records

    def _evaluate_thresholds_and_create_alerts(self):
        """Minimal placeholder. You’ll implement real logic here."""
        settings = self.env["med.settings"].sudo().get_settings()
        Alert = self.env["med.alert"].sudo()

        for r in self:
            severity = False
            alert_type = False
            msg = False

            # Example: SpO2
            if r.spo2 and r.spo2 <= settings.spo2_critical_min:
                severity, alert_type = "critical", "spo2"
                msg = f"Critical SpO2 {r.spo2}%"
            elif r.spo2 and r.spo2 <= settings.spo2_warning_min:
                severity, alert_type = "warning", "spo2"
                msg = f"Low SpO2 {r.spo2}%"

            if severity:
                Alert.create({
                    "patient_id": r.patient_id.id,
                    "reading_id": r.id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "message": msg,
                })
