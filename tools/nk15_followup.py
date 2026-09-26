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
p=Path('kompass/macro-profile.css');s=p.read_text()
addition='''
/* Native WebKit select painting can exceed its assigned grid width. Keep the native
   picker/keyboard interaction while drawing a width-constrained field and arrow. */
#profile-form select{-webkit-appearance:none;appearance:none;padding-right:32px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%23215a48' stroke-width='1.7'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;background-size:12px 8px}
#profile-form .field label,.macro-preview-item>span,.macro-preview-item>small{overflow-wrap:anywhere;hyphens:auto}
'''
if addition not in s:p.write_text(s+addition)
p=Path('kompass/app.js');s=p.read_text()
changes=[
 ('Der Energiebedarf wird nicht automatisch geschätzt.','Bei gewähltem Ernährungsprofil wird der Energiebedarf mit der DGE-Ruheenergieformel und der ausgewählten Aktivität geschätzt. Konkrete Makro-Startwerte und Plananpassungen sind in der Profilansicht als App-Annahmen erklärt.'),
 ('DGE/ÖGE · Ableitung ${ref.year}, geprüft am 26.09.2026.',"${ref.type==='Planungswert'?'Modellquelle; Startannahmen siehe Profil':'DGE/ÖGE'} · Stand ${ref.year}, geprüft am 26.09.2026."),
 ('Import umfasst exakt ${D.foods.length} eindeutige Lebensmittel-IDs aus dem offiziellen Excel-Download.','Der ursprüngliche BLV-Import umfasst ${D.meta.counts.generic+D.meta.counts.brand} Lebensmittel. Separat gekennzeichnete Hersteller- und Händlerprodukte ergänzen diese Basis.')]
for old,new in changes:
 assert s.count(old)==1 or new in s,old
 s=s.replace(old,new)
p.write_text(s)
p=Path('kompass/tests/macros-browser.py');s=p.read_text()
old='  for w in [320,390,1440]:'
new="""  p.locator('[data-action="sources"]').click();check('source help describes automatic energy and model assumptions','DGE-Ruheenergieformel' in p.locator('#dialog').inner_text() and 'App-Annahmen' in p.locator('#dialog').inner_text());p.locator('#dialog [data-action="close-dialog"]').click()
  for w in [320,390,1440]:"""
assert old in s or new in s
if new not in s:s=s.replace(old,new)
p.write_text(s)
print('WebKit form painting and source descriptions aligned with current implementation.')
p=Path('kompass/macro-profile.css');s=p.read_text()
addition='\n#profile-form select{overflow:hidden;text-overflow:ellipsis}\n'
if addition not in s:p.write_text(s+addition)
