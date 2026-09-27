"""Add eight sourced records to the latest published UI without reverting piece/text/report features."""
from pathlib import Path
import hashlib,json
p=Path('kompass')
expected={'index.html':'094570251e888c07d8a822bd0e264447928b26a609e0c7b36e4f743dc6c0a7fd','device.js':'e493590055c2a8fe543779956c53fd97e940da8d1323fd33fd9da7c95ad97bdf','household.js':'0e7818743ffd087688c425f1cb34b8b01c19ac7ae4d4b921ab36dc4b9e9c3a2f','sw.js':'b275d2bf395558d88ec3871b85ad5de346127c6640c84bd0f6fbfb3ae8e1db48','version.json':'5d804911489bb7d0b4a3956ee81b2f493374f937784585eaf8814662f6c19621'}
if json.loads((p/'version.json').read_text())['version']=='1.8.0':
 for n,h in expected.items():assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h,'Unexpected base: '+n
 for n in expected:
  s=(p/n).read_text().replace('1.8.0','1.8.1')
  if n=='index.html':
   a='<script src="catalog.js?v=1.8.1"></script>';assert s.count(a)==1
   s=s.replace(a,a+'<script src="additional-foods.js?v=1.8.1"></script>')
  if n=='sw.js':s=s.replace("const scripts=[","const scripts=['additional-foods.js',",1)
  (p/n).write_text(s)
fixture=Path('tools/test_pieces_v18.py');s=fixture.read_text()
a="  new_food(p,'Testriegel',30,label='Riegel');"
b="""  check('Eight new manufacturer records loaded',p.evaluate('NK_ADDITIONAL_FOODS.count===8 && NK_DATA.foods.length===1305'))
  nav(p,'search');p.locator('#food-search').fill('planted.chicken Nature');p.locator('#search-results [data-action="food-pick"][data-id="label-planted-chicken-natur"]').click();p.locator('#food-qty').fill('50')
  check('New product quantity preview uses declared protein','12' in p.locator('#food-preview').inner_text());p.locator('#dialog [data-action="close-dialog"]').click();p.locator('#food-search').fill('')
  new_food(p,'Testriegel',30,label='Riegel');"""
assert s.count(a)==1 or b in s
if b not in s:fixture.write_text(s.replace(a,b))
print('Preserved latest piece/text/report implementation; added catalogue and safe cache version.')
