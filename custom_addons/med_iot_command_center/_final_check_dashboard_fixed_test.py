from pathlib import Path
import re
import xml.etree.ElementTree as ET

tmp = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard_FIXED_TEST.xml")
xml = tmp.read_text(encoding="utf-8")

ET.parse(tmp)

input_tag = re.search(r'<input\b(?=[^>]*placeholder="Search patient\.\.\.")[^>]*/>', xml, re.S).group(0)
select_tag = re.search(r'<select\b[^>]*>', xml, re.S).group(0)

print("input t-on-input count:", input_tag.count("t-on-input="))
print("select t-on-change count:", select_tag.count("t-on-change="))

if input_tag.count("t-on-input=") != 1:
    raise SystemExit("BAD INPUT HANDLER COUNT")

if select_tag.count("t-on-change=") != 1:
    raise SystemExit("BAD SELECT HANDLER COUNT")

if 't-on-input="(ev) =' in xml:
    raise SystemExit("BAD CORRUPTED INPUT TEXT FOUND")

print("FINAL CHECK OK - SAFE TO APPLY")
