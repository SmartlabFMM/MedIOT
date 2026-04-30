# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MedAdminDashboard(models.Model):
    _name = "med.admin.dashboard"
    _description = "MedIoT Admin Dashboard"

    name = fields.Char(default="Admin Dashboard")

    doctor_count = fields.Integer(compute="_compute_dashboard")
    patient_count = fields.Integer(compute="_compute_dashboard")
    critical_patient_count = fields.Integer(compute="_compute_dashboard")
    pending_alert_count = fields.Integer(compute="_compute_dashboard")
    online_device_count = fields.Integer(compute="_compute_dashboard")

    doctor_ids = fields.Many2many(
        "res.users",
        compute="_compute_dashboard",
        string="Doctors / Staff",
    )

    critical_patient_ids = fields.Many2many(
        "med.patient",
        compute="_compute_dashboard",
        string="Critical Patients",
    )

    recent_alert_ids = fields.Many2many(
        "med.alert",
        compute="_compute_dashboard",
        string="Recent Alerts",
    )

    @api.depends()
    def _compute_dashboard(self):
        Patient = self.env["med.patient"].sudo()
        Alert = self.env["med.alert"].sudo()
        Device = self.env["med.device"].sudo()
        Users = self.env["res.users"].sudo()

        staff_group_xmlids = [
            "med_iot_command_center.group_med_admin",
            "med_iot_command_center.group_med_senior_doctor",
            "med_iot_command_center.group_med_junior_staff",
        ]

        doctors = Users.browse()
        internal_users = Users.search([("share", "=", False)])

        for user in internal_users:
            for xmlid in staff_group_xmlids:
                try:
                    if user.has_group(xmlid):
                        doctors |= user
                        break
                except Exception:
                    continue

        critical_patients = Patient.search([("status", "=", "critical")], limit=10)
        recent_alerts = Alert.search([], order="create_date desc", limit=10)

        device_status_field = Device._fields.get("status")
        if device_status_field:
            online_device_count = Device.search_count([("status", "=", "online")])
        else:
            online_device_count = Device.search_count([])

        for rec in self:
            rec.doctor_count = len(doctors)
            rec.patient_count = Patient.search_count([])
            rec.critical_patient_count = Patient.search_count([("status", "=", "critical")])
            rec.pending_alert_count = Alert.search_count([])
            rec.online_device_count = online_device_count
            rec.doctor_ids = doctors
            rec.critical_patient_ids = critical_patients
            rec.recent_alert_ids = recent_alerts

    def action_open_doctors(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Doctors / Staff",
            "res_model": "res.users",
            "view_mode": "list,form",
            "target": "current",
        }

    def action_open_patients(self):
        return self.env.ref("med_iot_command_center.action_med_patient").read()[0]

    def action_open_alerts(self):
        return self.env.ref("med_iot_command_center.action_med_alerts").read()[0]

    def action_open_devices(self):
        return self.env.ref("med_iot_command_center.action_med_devices").read()[0]

class ResUsers(models.Model):
    _inherit = "res.users"

    mediot_role_label = fields.Char(
        string="Role",
        compute="_compute_mediot_role_label",
    )

    @api.depends("group_ids")
    def _compute_mediot_role_label(self):
        admin_group = self.env.ref("med_iot_command_center.group_med_admin", raise_if_not_found=False)
        senior_group = self.env.ref("med_iot_command_center.group_med_senior_doctor", raise_if_not_found=False)
        junior_group = self.env.ref("med_iot_command_center.group_med_junior_staff", raise_if_not_found=False)

        for user in self:
            roles = []
            if admin_group and admin_group in user.group_ids:
                roles.append("Admin")
            if senior_group and senior_group in user.group_ids:
                roles.append("Doctor")
            if junior_group and junior_group in user.group_ids:
                roles.append("Junior Staff")

            user.mediot_role_label = ", ".join(roles) if roles else "User"