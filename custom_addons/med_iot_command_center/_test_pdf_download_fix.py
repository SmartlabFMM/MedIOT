from pathlib import Path
import re
import xml.etree.ElementTree as ET

base = Path(r"D:\odoo-19\custom_addons\med_iot_command_center")

report_real = base / "reports" / "patient_medical_report.xml"
js_real = base / "static" / "src" / "js" / "dashboard.js"

report_test = base / "reports" / "patient_medical_report_TEST.xml"
js_test = base / "static" / "src" / "js" / "dashboard_TEST.js"

report_xml = report_real.read_text(encoding="utf-8")
js = js_real.read_text(encoding="utf-8")

print("=== CURRENT CHECK ===")
print("Has action_report_patient_medical:", "action_report_patient_medical" in report_xml)
print("Has report_patient_medical_document:", "report_patient_medical_document" in report_xml)
print("Current JS report URL lines:")
for line in js.splitlines():
    if "/report/pdf/" in line:
        print(line.strip())

# Create TEST JS only
js_fixed = re.sub(
    r'const url = `/report/pdf/[^`]+/\$\{patientId\}[^`]*`;',
    'const url = `/report/pdf/med_iot_command_center.report_patient_medical_document/${patientId}?download=1`;',
    js,
    count=1
)

js_test.write_text(js_fixed, encoding="utf-8")

# Validate current report XML parses
try:
    ET.parse(report_real)
    print("Current report XML parse: OK")
except Exception as e:
    print("Current report XML parse: FAILED")
    print(e)
    raise SystemExit(1)

# Validate TEST JS URL
test_js_text = js_test.read_text(encoding="utf-8")
if "med_iot_command_center.report_patient_medical_document" not in test_js_text:
    raise SystemExit("FAILED: TEST JS does not contain correct report name")

if "?download=1" not in test_js_text:
    raise SystemExit("FAILED: TEST JS does not contain download=1")

print("TEST JS URL: OK")

# Copy current report as test file for safe inspection
report_test.write_text(report_xml, encoding="utf-8")

print("Temp files created:")
print(report_test)
print(js_test)
print("SAFE TEST DONE - REAL FILES NOT CHANGED")
