from pathlib import Path
import xml.etree.ElementTree as ET

src = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard.xml")
tmp = Path(r"D:\odoo-19\custom_addons\med_iot_command_center\static\src\xml\dashboard_FIXED_TEST.xml")

xml = src.read_text(encoding="utf-8")

ph = 'placeholder="Search patient..."'
ph_idx = xml.find(ph)
if ph_idx == -1:
    raise SystemExit("Search placeholder not found")

start = xml.rfind("<input", 0, ph_idx)

opt = '<option value="">All Status</option>'
opt_idx = xml.find(opt, ph_idx)
if opt_idx == -1:
    raise SystemExit("All Status option not found")

end = xml.find("</select>", opt_idx)
if end == -1:
    raise SystemExit("Closing select not found")
end += len("</select>")

clean_block = '''<input type="text"
                               placeholder="Search patient..."
                               style="width:210px; height:42px; border:1px solid #dde0f5; border-radius:10px; padding:0 38px 0 16px; background:white;"
                               t-att-value="state.searchQuery"
                               t-on-input="(ev) => this.onSearchPatient(ev)"/>
                        <i class="fa fa-search" style="position:absolute; right:14px; top:13px; color:#94a3b8;"/>
                    </div>

                    <select t-on-change="(ev) => this.onStatusFilter(ev)"
                            t-att-value="state.statusFilter"
                            style="width:210px; height:42px; border:1px solid #dde0f5; border-radius:10px; padding:0 14px; background:white;">
                        <option value="">All Status</option>
                        <option value="stable">Stable</option>
                        <option value="warning">Warning</option>
                        <option value="critical">Critical</option>
                    </select>'''

xml = xml[:start] + clean_block + xml[end:]

tmp.write_text(xml, encoding="utf-8")

ET.parse(tmp)

text = tmp.read_text(encoding="utf-8")
bad = [
    't-on-input="(ev) =',
    'this.onStatusFilter(ev)"\n                            t-att-value',
    't-on-change="(ev) => this.onStatusFilter(ev)"\n                            t-on-change',
]

for b in bad:
    if b in text:
        raise SystemExit("BAD CORRUPTED TEXT STILL FOUND")

print("XML PARSE TEST: OK")
print("input handler count:", text.count('t-on-input="(ev) => this.onSearchPatient(ev)"'))
print("select handler count:", text.count('t-on-change="(ev) => this.onStatusFilter(ev)"'))
print("SAFE TO APPLY")
