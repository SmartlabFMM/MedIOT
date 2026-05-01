from pathlib import Path
import xml.etree.ElementTree as ET

src = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")
tmp = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard_FIXED_TEST.xml")

xml = src.read_text(encoding="utf-8")

# Replace full search input block
idx = xml.find('placeholder="Search patient..."')
start = xml.rfind("<input", 0, idx)
end = xml.find('<i class="fa fa-search"', idx)

clean_input = '''<input type="text"
                               placeholder="Search patient..."
                               style="width:210px; height:42px; border:1px solid #dde0f5; border-radius:10px; padding:0 38px 0 16px; background:white;"
                               t-att-value="state.searchQuery"
                               t-on-input="(ev) => this.onSearchPatient(ev)"/>
                        '''

xml = xml[:start] + clean_input + xml[end:]

# Replace select start through All Status option
opt = '<option value="">All Status</option>'
opt_idx = xml.find(opt)
sel_start = xml.rfind("<select", 0, opt_idx)
opt_end = opt_idx + len(opt)

clean_select_start = '''<select t-on-change="(ev) => this.onStatusFilter(ev)"
                            t-att-value="state.statusFilter"
                            style="width:210px; height:42px; border:1px solid #dde0f5; border-radius:10px; padding:0 14px; background:white;">
                        <option value="">All Status</option>'''

xml = xml[:sel_start] + clean_select_start + xml[opt_end:]

tmp.write_text(xml, encoding="utf-8")

ET.parse(tmp)
print("XML PARSE TEST: OK")

test = tmp.read_text(encoding="utf-8")

bad = [
    'this.onStatusFilter(ev)"\n                            t-att-value',
    't-on-change="(ev) => this.onStatusFilter(ev)"\n                            t-on-change',
    't-on-input="(ev) =',
]

for b in bad:
    if b in test:
        raise SystemExit("FAILED: leftover corrupted text found")

print("CLEAN TEST: OK")
print("SAFE TO APPLY")
