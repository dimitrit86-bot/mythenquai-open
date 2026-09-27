"""Exercise the existing visible path for editing package values; no application changes."""
from pathlib import Path
p=Path('tools/nk18_entry.py');s=p.read_text()
a="p.locator('[data-action=\"edit-custom-food\"]').click()"
b="p.locator('#dialog details:has([data-action=\"edit-custom-food\"])>summary').click();p.locator('[data-action=\"edit-custom-food\"]').click()"
assert s.count(a)==1 or b in s
if b not in s:s=s.replace(a,b)
p.write_text(s)
print('Existing package edit opens its details section before activation.')
