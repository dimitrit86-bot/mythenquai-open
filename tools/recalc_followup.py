"""Correction navigation and independent fixture target. No personal-data changes."""
from pathlib import Path
p=Path('tools/test_recalc_browser.py');s=p.read_text();s=s.replace('manual={protein:50,vitC:50}','manual={protein:500,vitC:50}');p.write_text(s)
p=Path('kompass/app.js');s=p.read_text()
old="else if(a==='show-day'){date=b.dataset.date;nav('today');}"
new="else if(a==='show-day'){closeDialog();date=b.dataset.date;nav('today');}"
assert old in s or new in s;s=s.replace(old,new)
old="else if(a==='edit-recipe')newRecipe(recipe(id));"
new="else if(a==='edit-recipe'){closeDialog();newRecipe(recipe(id));}"
assert old in s or new in s;s=s.replace(old,new);p.write_text(s)
print('Issue-review links close the modal; nutrition fixture stays below unrelated celebration target.')
