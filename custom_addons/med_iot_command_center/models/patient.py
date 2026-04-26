# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedPatient(models.Model):
    _name = "med.patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    

    smoker = fields.Boolean(string="Smoker", default=False)
    sporty = fields.Boolean(string="Sporty", default=False)
    image_128 = fields.Image(string="Photo", max_width=128, max_height=128)

    name = fields.Char(required=True, tracking=True)
    ref = fields.Char(string="Patient ID", readonly=True, copy=False, default="New", index=True)

    age = fields.Integer()
    gender = fields.Selection([("male", "Male"), ("female", "Female"), ("other", "Other")], default="other")
    room = fields.Char(help="Room/Bed e.g. ICU-01", tracking=True)

    assigned_doctor_id = fields.Many2one("res.users", string="Assigned Doctor", tracking=True)
    department = fields.Char()

    status = fields.Selection(
        [("stable", "Stable"), ("warning", "Warning"), ("critical", "Critical")],
        default="stable",
        tracking=True,
        index=True,
    )
    active = fields.Boolean(default=True)

    latest_temp = fields.Float(string="Temp (°C)", readonly=True)
    latest_spo2 = fields.Float(string="SpO2 (%)", readonly=True)
    latest_ecg_bpm = fields.Integer(string="ECG (BPM)", readonly=True)
    latest_reading_at = fields.Datetime(readonly=True)

    alert_ids = fields.One2many("med.alert", "patient_id", string="Alerts")
    pending_alert_count = fields.Integer(compute="_compute_pending_alert_count")

    @api.depends("alert_ids.state", "alert_ids.severity")
    def _compute_pending_alert_count(self):
        for rec in self:
            rec.pending_alert_count = len(rec.alert_ids.filtered(lambda a: a.state == "new"))

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("ref", "New") == "New":
                vals["ref"] = seq.next_by_code("med.patient") or _("New")
        return super().create(vals_list)

    @api.constrains("room", "active")
    def _check_unique_active_room(self):
        for rec in self.filtered(lambda r: r.room and r.active):
            dup = self.search_count([("id", "!=", rec.id), ("room", "=", rec.room), ("active", "=", True)])
            if dup:
                raise ValidationError(_("There is already an active patient assigned to room/bed: %s") % rec.room)








