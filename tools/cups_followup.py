"""Preserve a chosen recipe ingredient when its search input blurs unchanged."""
from pathlib import Path

def rep(s, old, new):
    assert s.count(old)==1 or new in s, old[:100]
    return s.replace(old,new) if old in s else s
p=Path('kompass/recipe-paste.js');s=p.read_text()
s=rep(s,"if(t.dataset.search!==undefined){r.name=t.value;", "if(t.dataset.search!==undefined&&r.name!==t.value){r.name=t.value;")
s=rep(s,"Die Zuordnung sind Vorschläge", "Die Zuordnungen sind Vorschläge")
s=rep(s,"errors.length+' Zutaten brauchen noch eine Zuordnung oder gültige Menge (Zeilen '", "errors.length+(errors.length===1?' Zutat braucht':' Zutaten brauchen')+' noch eine Zuordnung oder gültige Menge (Zeilen '")
p.write_text(s)
p=Path('tools/test_cups_recipes.py');s=p.read_text()
a="p.locator('#paste-unit-1').select_option('g');check('Unknown ingredient creates visible partial preview'"
b="p.locator('#paste-unit-1').select_option('g');check('Ingredient choice survives unchanged search blur',p.locator('#paste-food-1').input_value()=='unknown');check('Unknown ingredient creates visible partial preview'"
s=rep(s,a,b);p.write_text(s)
print('Unchanged search blur preserves selected ingredient; regression assertion retained.')
