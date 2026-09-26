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
