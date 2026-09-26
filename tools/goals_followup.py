"""Keep the profile preview stable between input and blur/change events."""
from pathlib import Path
p=Path('kompass/app.js');s=p.read_text()
a="try{const p=readProfileForm();$('#goal-description').textContent="
b="try{const p=readProfileForm();const signature=JSON.stringify(p);if(el.dataset.goalPreview===signature)return;el.dataset.goalPreview=signature;$('#goal-description').textContent="
assert s.count(a)==1 or b in s
s=s.replace(a,b)
a="}catch(e){el.innerHTML='<p class=\"small\" role=\"status\">Vorschau: '"
b="}catch(e){delete el.dataset.goalPreview;el.innerHTML='<p class=\"small\" role=\"status\">Vorschau: '"
assert s.count(a)==1 or b in s
s=s.replace(a,b)
p.write_text(s)
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
print('Wait for viewport resize layout to settle and export geometry if strict width checks fail.')
