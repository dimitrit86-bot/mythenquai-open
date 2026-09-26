"""Reset the active UI filter in the browser fixture; preserve application code."""
from pathlib import Path
p=Path('tools/test_browser.py')
s=p.read_text()
old="nav(p,'search');p.locator('#food-search').fill('planted.hack');"
new="nav(p,'search');p.locator('[data-action=\"filter\"][data-filter=\"all\"]').click();p.locator('#food-search').fill('planted.hack');"
assert s.count(old)==1 or new in s
s=s.replace(old,new)
old=" except Exception:\n  for name,pg"
new=" except Exception:\n  import traceback\n  (BASE/'test-output'/'failure.txt').write_text(traceback.format_exc())\n  for name,pg"
assert old in s or new in s
s=s.replace(old,new)
p.write_text(s)
print('Browser fixture resets search filter; failure trace exported.')
