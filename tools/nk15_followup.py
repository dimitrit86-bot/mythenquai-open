"""Reviewed presentation and cross-browser test corrections. No user-data changes."""
from pathlib import Path
p=Path('kompass/tests/macros-browser.py');s=p.read_text()
old="'2’400' in preview(p,'energy')"
new="'2400' in preview(p,'energy').replace(chr(39),'').replace('’','')"
assert s.count(old)==1 or new in s
s=s.replace(old,new)
old="p.set_viewport_size({'width':w,'height':950});check"
new="p.set_viewport_size({'width':w,'height':950});p.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');check"
assert old in s or new in s;s=s.replace(old,new)
old=" except Exception:\n  (OUT/"
new=""" except Exception:
  layout=p.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,elements:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>innerWidth+1}).slice(0,30).map(e=>({tag:e.tagName,id:e.id,cls:e.className,text:e.textContent.slice(0,80),right:e.getBoundingClientRect().right,scroll:e.scrollWidth,display:getComputedStyle(e).display}))})''')
  (OUT/f'{engine}-layout.json').write_text(json.dumps(layout,indent=2))
  (OUT/"""
assert old in s or new in s;s=s.replace(old,new)
p.write_text(s)
p=Path('kompass/macro-profile.css');s=p.read_text()
addition='\n@media(max-width:520px){#profile-form .macro-profile-section .form-grid{grid-template-columns:minmax(0,1fr)}#profile-form .macro-profile-section .field select{width:100%;min-width:0}}\n'
if addition not in s:p.write_text(s+addition)
print('Readable mobile selectors; locale-neutral assertions and settled layout diagnostics.')
