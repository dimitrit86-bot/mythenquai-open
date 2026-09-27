"""Fit named piece selectors to small screens and test the actual amount dialog."""
from pathlib import Path
p=Path('kompass/food-portions.css');s=p.read_text()
css='''
/* Preserve full native choices while constraining the painted selection in WebKit. */
#food-form .field,#ingredients .field{min-width:0}
#food-form select,#ingredients select{width:100%;min-width:0;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;appearance:none;-webkit-appearance:none;padding-right:28px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%23215a48' stroke-width='1.7'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;background-size:12px 8px}
'''
if css not in s:p.write_text(s+css)
p=Path('tools/nk18_browser.py');s=p.read_text()
old="  p.locator('#dialog [data-action=\"close-dialog\"]').click();nav(p,'reports');check('Reports still available after piece entries',p.locator('[data-action=\"report-pdf\"]').count()>0)"
new="""  p.locator('#custom-piece-amount').fill('30');p.locator('#custom-piece-label').fill('Lange Portionsbezeichnung für ein Stück');p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods[0].name==="Unsaved"');long_id=p.evaluate('NK_APP.getState().foods[0].id');p.locator(f'#search-results [data-action="food-pick"][data-id="{long_id}"]').click()
  for width in [320,390,1440]:
   p.set_viewport_size({'width':width,'height':950});p.wait_for_timeout(150);check(f'Long named piece amount dialog fits {width}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-piece-amount.png'))
  p.locator('#dialog [data-action="close-dialog"]').click();nav(p,'reports');check('Reports still available after piece entries',p.locator('[data-action="report-pdf"]').count()>0)"""
assert s.count(old)==1 or new in s
if new not in s:s=s.replace(old,new);p.write_text(s)
print('Named portion selectors fit narrow screens; amount dialog layout regression added.')
