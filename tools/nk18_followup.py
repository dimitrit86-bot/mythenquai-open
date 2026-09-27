"""Correct the test expression language; preserve application and user data."""
from pathlib import Path
p=Path('kompass/tests/test_food_entry.py')
s=p.read_text()
a='document.documentElement.scrollWidth<=innerWidth and document.querySelector'
b='document.documentElement.scrollWidth<=innerWidth && document.querySelector'
assert s.count(a)==1 or b in s, 'Unexpected browser fixture'
p.write_text(s.replace(a,b))
print('Use JavaScript && rather than Python and inside Page.evaluate; same layout condition.')
