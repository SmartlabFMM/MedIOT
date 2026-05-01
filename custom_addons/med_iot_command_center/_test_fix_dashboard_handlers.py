from pathlib import Path
import re
import xml.etree.ElementTree as ET

src = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")
tmp = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard_FIXED_TEST.xml")

xml = src.read_text(encoding="utf-8")

# Clean search input tag safely
def fix_search_input(match):
    tag = match.group(0)

    # remove all existing t-on-input duplicates
    tag = re.sub(r'\s+t-on-input="[^"]*"', '', tag)

    # ensure not malformed self-closing
    tag = tag.replace('/>', '>')
    tag = tag.rstrip('>')

    # add one correct handler
    tag += ' t-on-input="(ev) => this.onSearchPatient(ev)"/>'
    return tag

xml = re.sub(
    r'<input\b(?=[^>]*placeholder="Search patient\.\.\.")[^>]*>',
    fix_search_input,
    xml,
    count=1,
    flags=re.S
)

# Clean status select tag safely
def fix_select(match):
    tag = match.group(0)

    # remove all existing t-on-change duplicates
    tag = re.sub(r'\s+t-on-change="[^"]*"', '', tag)

    # add one correct handler
    tag = tag.replace('<select', '<select t-on-change="(ev) => this.onStatusFilter(ev)"', 1)
    return tag

xml = re.sub(
    r'<select\b[^>]*>',
    fix_select,
    xml,
    count=1,
    flags=re.S
)

tmp.write_text(xml, encoding="utf-8")

print("Temp file created:")
print(tmp)

# XML parse test
try:
    ET.parse(tmp)
    print("XML PARSE TEST: OK")
except Exception as e:
    print("XML PARSE TEST: FAILED")
    print(e)
    raise SystemExit(1)

# Handler count tests
test = tmp.read_text(encoding="utf-8")

search_match = re.search(r'<input\b(?=[^>]*placeholder="Search patient\.\.\.")[^>]*>', test, re.S)
select_match = re.search(r'<select\b[^>]*>', test, re.S)

if not search_match:
    raise SystemExit("FAILED: Search input not found")

if not select_match:
    raise SystemExit("FAILED: Select tag not found")

search_tag = search_match.group(0)
select_tag = select_match.group(0)

print("Search input t-on-input count:", search_tag.count("t-on-input="))
print("Select t-on-change count:", select_tag.count("t-on-change="))

if search_tag.count("t-on-input=") != 1:
    raise SystemExit("FAILED: Search input still has wrong handler count")

if select_tag.count("t-on-change=") != 1:
    raise SystemExit("FAILED: Select still has wrong handler count")

print("HANDLER TEST: OK")
print("SAFE TO APPLY")
