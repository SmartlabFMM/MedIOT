from pathlib import Path
import xml.etree.ElementTree as ET
import re

src = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")
tmp = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard_FIXED_TEST.xml")

xml = src.read_text(encoding="utf-8")

# Rebuild the corrupted search input completely
ph = 'placeholder="Search patient..."'
idx = xml.find(ph)
if idx == -1:
    raise SystemExit("Search input placeholder not found")

start = xml.rfind("<input", 0, idx)
end = xml.find('<i class="fa fa-search"', idx)

if start == -1 or end == -1:
    raise SystemExit("Could not locate full search input block")

clean_input = '''<input type="text"
                               placeholder="Search patient..."
                               style="width:210px; height:42px; border:1px solid #dde0f5; border-radius:10px; padding:0 38px 0 16px; background:white;"
                               t-att-value="state.searchQuery"
                               t-on-input="(ev) => this.onSearchPatient(ev)"/>
                        '''

xml = xml[:start] + clean_input + xml[end:]

# Rebuild the status select opening tag completely
sel_start = xml.find("<select", xml.find("All Status") - 500)
if sel_start == -1:
    raise SystemExit("Select tag not found")

sel_end = xml.find(">", sel_start)
if sel_end == -1:
    raise SystemExit("Select closing > not found")

clean_select = '''<select t-on-change="(ev) => this.onStatusFilter(ev)"
                            t-att-value="state.statusFilter"
                            style="width:210px; height:42px; border:1px solid #dde0f5; border-radius:10px; padding:0 14px; background:white;">'''

xml = xml[:sel_start] + clean_select + xml[sel_end + 1:]

tmp.write_text(xml, encoding="utf-8")

try:
    ET.parse(tmp)
    print("XML PARSE TEST: OK")
except Exception as e:
    print("XML PARSE TEST: FAILED")
    print(e)
    raise SystemExit(1)

test = tmp.read_text(encoding="utf-8")

search_block = test[test.find('placeholder="Search patient..."') - 200:test.find('placeholder="Search patient..."') + 500]
select_block = test[test.find("<select"):test.find("<select") + 500]

print("Search t-on-input count:", search_block.count("t-on-input="))
print("Select t-on-change count:", select_block.count("t-on-change="))

if search_block.count("t-on-input=") != 1:
    raise SystemExit("FAILED: search input handler count wrong")

if select_block.count("t-on-change=") != 1:
    raise SystemExit("FAILED: select handler count wrong")

print("SAFE TO APPLY")
