"""Compare numerical goal text across ICU versions; no application or user-data change."""
from pathlib import Path
p=Path('kompass/tests/macros-browser.py')
s=p.read_text()
old="'2’400' in preview(p,'energy')"
new="'2400' in preview(p,'energy').replace(chr(39),'').replace('’','')"
assert s.count(old)==1 or new in s, 'Unexpected browser fixture'
s=s.replace(old,new)
p.write_text(s)
print('Browser goal assertion accepts both Swiss thousands-separator variants.')
