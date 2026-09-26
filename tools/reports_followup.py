"""Correct a browser-test selector; no application or user-data changes."""
from pathlib import Path
p=Path('tools/test_reports.py');s=p.read_text()
old="p.locator('h1').inner_text()"
new="p.locator('#main h1').inner_text()"
assert s.count(old)==1 or old not in s, 'Unexpected test selector'
s=s.replace(old,new)
p.write_text(s)
print('Daily report heading check scoped to active main view.')
