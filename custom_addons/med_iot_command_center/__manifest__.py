# -*- coding: utf-8 -*-
{
    "name": "MedIoT Command Center",
    "version": "19.0.1.0.0",
    "category": "Healthcare",
    "summary": "Doctor dashboard for real-time patient monitoring + alerts + history",
    "depends": [
        "base",
        "web",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/record_rules.xml",
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "views/patient_views.xml",
        "views/vital_reading_views.xml",
        "views/alert_views.xml",
        "views/device_views.xml",
        "views/settings_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "med_iot_command_center/static/src/js/dashboard.js",
            "med_iot_command_center/static/src/xml/dashboard.xml",
            "med_iot_command_center/static/src/scss/dashboard.scss",
        ],
    },
    "application": True,
    "images": ["static/description/icon.png"],
    "license": "LGPL-3",
}
