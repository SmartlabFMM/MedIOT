# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.home import Home


class MedIoTHome(Home):
    def _login_redirect(self, uid, redirect=None):
        """Redirect doctor/junior-staff users straight to the MedIoT dashboard."""
        if redirect:
            return redirect

        env = http.request.env(user=uid)
        doctor_groups = (
            "med_iot_command_center.group_med_senior_doctor",
            "med_iot_command_center.group_med_junior_staff",
        )
        if any(env.user.has_group(g) for g in doctor_groups):
            return "/odoo/action-med_iot_command_center.action_med_dashboard"

        return super()._login_redirect(uid, redirect=redirect)
