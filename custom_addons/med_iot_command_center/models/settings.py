# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MedSettings(models.Model):
    _name = "med.settings"
    _description = "Monitoring Settings (Singleton)"

    # Heart rate
    hr_critical_min = fields.Integer(default=40)
    hr_critical_max = fields.Integer(default=130)
    hr_warning_min = fields.Integer(default=50)
    hr_warning_max = fields.Integer(default=110)

    # SpO2
    spo2_critical_min = fields.Float(default=85.0)
    spo2_warning_min = fields.Float(default=90.0)

    # Temperature
    temp_critical_min = fields.Float(default=35.0)
    temp_critical_max = fields.Float(default=39.0)
    temp_warning_min = fields.Float(default=36.0)
    temp_warning_max = fields.Float(default=37.8)

    check_interval_seconds = fields.Integer(default=30)

    @api.model
    def get_settings(self):
        rec = self.search([], limit=1)
        if not rec:
            rec = self.create({})
        return rec
