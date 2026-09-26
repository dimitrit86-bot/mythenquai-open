"""Keep profile controls stable and fit narrow WebKit layouts."""
from pathlib import Path
p=Path('kompass/app.js');s=p.read_text()
a="try{const p=readProfileForm();$('#goal-description').textContent="
b="try{const p=readProfileForm();const signature=JSON.stringify(p);if(el.dataset.goalPreview===signature)return;el.dataset.goalPreview=signature;$('#goal-description').textContent="
assert s.count(a)==1 or b in s
s=s.replace(a,b)
a="}catch(e){el.innerHTML='<p class=\"small\" role=\"status\">Vorschau: '"
b="}catch(e){delete el.dataset.goalPreview;el.innerHTML='<p class=\"small\" role=\"status\">Vorschau: '"
assert s.count(a)==1 or b in s
s=s.replace(a,b);p.write_text(s)
print('Prevent unchanged preview rerender on blur from removing the clicked suggestion button.')
p=Path('tools/test_goals.py');s=p.read_text()
a="p.set_viewport_size({'width':width,'height':900});check"
b="p.set_viewport_size({'width':width,'height':900});p.wait_for_timeout(150);check"
assert s.count(a)==2 or b in s
s=s.replace(a,b)
a=" except Exception:\n  p.screenshot"
b=""" except Exception:
  layout=p.evaluate('''() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflows:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+.5||e.scrollWidth>e.clientWidth+2).map(e=>({tag:e.tagName,id:e.id,classes:String(e.className).slice(0,100),right:e.getBoundingClientRect().right,left:e.getBoundingClientRect().left,client:e.clientWidth,scroll:e.scrollWidth,display:getComputedStyle(e).display,text:e.textContent.slice(0,100)})).slice(0,100)})''')
  (BASE/'test-output'/f'{engine}-layout.json').write_text(json.dumps(layout,indent=2))
  p.screenshot"""
assert s.count(a)==1 or b in s
s=s.replace(a,b);p.write_text(s)
p=Path('kompass/macro-goals.css');s=p.read_text()
css='''
/* Prevent WebKit's native option width from expanding a narrow profile form. */
#profile-form .field{min-width:0;max-width:100%}
#profile-form .field label,#profile-form .field small{overflow-wrap:anywhere}
#profile-form select{display:block;appearance:none;-webkit-appearance:none;width:100%;max-width:100%;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding-right:32px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%23215a48' stroke-width='2'/%3E%3C/svg%3E");background-repeat:no-repeat;background-size:10px 7px;background-position:right 12px center}
'''
if css not in s:p.write_text(s+css)
p=Path('tools/test_goals.py');s=p.read_text()
a="  p.set_viewport_size({'width':390,'height':844});p.screenshot"
b="""  p.set_viewport_size({'width':320,'height':900});p.locator('details:has(#calc-weight)>summary').click();p.wait_for_timeout(150);check('Expanded reference fields also fit narrow WebKit layout',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot"""
assert s.count(a)==1 or b in s
s=s.replace(a,b);p.write_text(s)
print('Constrain select rendering, wrap labels, and test expanded references at 320px.')
