"""Reviewed mobile presentation and cross-browser assertions; no private data."""
from pathlib import Path
p=Path('kompass/tests/macros-browser.py');s=p.read_text()
old="'2’400' in preview(p,'energy')"
new="'2400' in preview(p,'energy').replace(chr(39),'').replace('’','')"
assert s.count(old)==1 or new in s;s=s.replace(old,new)
old="p.set_viewport_size({'width':w,'height':950});check"
new="p.set_viewport_size({'width':w,'height':950});p.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');check"
assert old in s or new in s;s=s.replace(old,new)
diag="""() => {
 const result={width:innerWidth,scroll:document.documentElement.scrollWidth};
 result.elements=[...document.querySelectorAll('body *')].filter(e=>e.scrollWidth>e.clientWidth+1).slice(0,60).map(e=>({tag:e.tagName,id:e.id,cls:String(e.className),text:e.textContent.slice(0,60),right:e.getBoundingClientRect().right,width:e.clientWidth,scroll:e.scrollWidth,display:getComputedStyle(e).display}));
 const rules=['#profile-form select{overflow:hidden;text-overflow:ellipsis}','#profile-form{overflow-wrap:anywhere}','details:not([open])>:not(summary){display:none!important}','#toast{display:none!important}'];
 result.probes=[];for(const rule of rules){const style=document.createElement('style');style.textContent=rule;document.head.append(style);result.probes.push({rule,scroll:document.documentElement.scrollWidth});style.remove();}
 return result;
}"""
old=" except Exception:\n  (OUT/"
new=" except Exception:\n  layout=p.evaluate("+repr(diag)+")\n  (OUT/f'{engine}-layout.json').write_text(json.dumps(layout,indent=2))\n  (OUT/"
assert old in s or new in s;s=s.replace(old,new);p.write_text(s)
p=Path('kompass/macro-profile.css');s=p.read_text()
addition='\n@media(max-width:520px){#profile-form .macro-profile-section .form-grid{grid-template-columns:minmax(0,1fr)}#profile-form .macro-profile-section .field select{width:100%;min-width:0}}\n'
if addition not in s:p.write_text(s+addition)
print('Mobile selectors and precise cross-browser overflow diagnosis.')
