from pathlib import Path
import re

base = Path(r"D:\odoo-19\custom_addons\med_iot_command_center")
manifest = base / "__manifest__.py"
js = base / "static" / "src" / "js" / "patient_vital_charts.js"

txt = manifest.read_text(encoding="utf-8")

txt = re.sub(
    r'\s*["\']med_iot_command_center/static/src/js/patient_vital_charts\.js["\'],?\s*',
    '\n',
    txt
)

manifest.write_text(txt, encoding="utf-8")

if js.exists():
    js.rename(js.with_suffix(".js.disabled"))

print("patient_vital_charts.js disabled")
