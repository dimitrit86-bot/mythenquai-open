"""Build the public release archive from releases.json. Never reads private data.
Usage: python3 kompass/release-notes/build.py [--check]
Add a release to releases.json, set kompass/version.json and loader/cache versions,
then rebuild. Existing releases must remain in the manifest.
"""
from pathlib import Path
import argparse,json,html,re
P=Path(__file__).resolve().parent

def build():
    data=json.loads((P/'releases.json').read_text())
    def ver(v):
        if not re.fullmatch(r'(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})',v):raise ValueError('Invalid version')
        return tuple(map(int,v.split('.')))
    current=json.loads((P.parent/'version.json').read_text())['version']
    records=data['releases']
    assert data['schema']==1 and records and len({r['version'] for r in records})==len(records)
    assert all(ver(r['version'])>=(1,9,0) for r in records), 'Archive starts at 1.9'
    assert ver(current)==max(ver(r['version']) for r in records),'Current release needs notes'
    e=html.escape;ordered=sorted(records,key=lambda r:ver(r['version']),reverse=True);files={}
    files['catalog.js']='/* Generated from releases.json; edit the JSON and run build.py. */\n(function(root,data){if(typeof module===\'object\'&&module.exports)module.exports=data;else root.NK_RELEASE_DATA=data;})(typeof globalThis!==\'undefined\'?globalThis:this,'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+');\n'
    cards=[]
    for r in ordered:
        assert r['title'] and r['changes'] and isinstance(r['notes'],list)
        md='# Nährstoff-Kompass v'+r['version']+' · '+r['title']+'\n\n'+r['date']+'\n\n'+r['summary']+'\n\n'
        content=''
        for i,c in enumerate(r['changes'],1):
            md+='## '+c['title']+'\n\n'+c['text']+'\n\n'
            content+=f'<section class="release-change"><span class="release-step" aria-hidden="true">{i:02}</span><div><h3>{e(c["title"])}</h3><p>{e(c["text"])}</p></div></section>'
        md+='## Gut zu wissen\n\n'+'\n\n'.join(r['notes'])+'\n'
        files['v'+r['version']+'.md']=md
        notes=''.join('<p>'+e(t)+'</p>' for t in r['notes'])
        cards.append(f'<details open class="release-card" id="v{e(r["version"])}"><summary><span class="release-stamp">v{e(r["version"])}</span><span class="release-card-heading"><strong>{e(r["title"])}</strong><time datetime="{e(r["date"])}">{e(r["date"])}</time></span><span class="release-chevron" aria-hidden="true">⌄</span></summary><div class="release-card-body"><p class="release-summary">{e(r["summary"])}</p><div class="release-changes">{content}</div><details class="release-fineprint"><summary>Gut zu wissen</summary>{notes}</details><a class="release-text-link" href="v{e(r["version"])}.md" download>Als Text speichern</a></div></details>')
    files['index.html']='''<!doctype html>
<html lang="de-CH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"><meta name="theme-color" content="#215a48"><title>Release Notes · Nährstoff-Kompass</title><link rel="icon" type="image/svg+xml" href="../icon.svg"><link rel="stylesheet" href="../release-notes.css?v='''+e(current)+'''"><style>body{margin:0;background:#edf3ee;color:#233b32;font:15px system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}*{box-sizing:border-box}main{max-width:820px;margin:28px auto;background:#f5f8f6;border:1px solid #d7e3db;border-radius:24px;overflow:hidden}a{color:#215a48}.release-hero a{color:#e1efe5}.release-footer a{display:inline-block;padding:12px 0;font-weight:600;min-height:44px}.archive-back{display:inline-block;min-height:44px;padding-top:12px;font-size:13px}.release-hero h1{font-size:clamp(28px,5vw,42px);letter-spacing:-.04em;margin:15px 0}.archive-note{font-size:12px;line-height:1.7;color:#5f7368;margin:0}@media(max-width:600px){main{margin:0;border:0;border-radius:0}.release-hero{border-radius:0}}</style></head><body><main><header class="release-hero"><span class="release-kicker">NÄHRSTOFF-KOMPASS · RELEASE NOTES</span><h1>Schritt für Schritt besser.</h1><p>Alle Neuerungen ab v1.9. Einmal zurückschauen, danach kein Update mehr verpassen.</p><div class="release-hero-pills"><span>Aktuell: v'''+e(current)+'''</span><span>'''+str(len(records))+''' dokumentierte Updates</span></div><a class="archive-back" href="../">← Zurück zum Kompass</a></header><div class="release-body">'''+''.join(cards)+'''<p class="archive-note">Dieses Archiv enthält nur allgemeine Produktinformationen, keine persönlichen Profildaten. Lesen im Archiv verändert deinen Lesestand nicht. Die App merkt automatisch, welche Neuerungen sie deinem Profil bereits gezeigt hat. Frühere Versionen als v1.9 werden nicht nachgetragen.</p></div><footer class="release-footer"><a href="../">Nährstoff-Kompass öffnen</a></footer></main></body></html>
'''
    files['README.md']='# Release Notes · Nährstoff-Kompass\n\nDas benutzerfreundliche Archiv beginnt auf Wunsch einmalig mit **v1.9.0**. Frühere technische UPDATE-Dateien bleiben unverändert, werden hier aber nicht nachgetragen. Neue Releases werden ab jetzt ergänzt.\n\n'+''.join('- [v'+r['version']+' – '+r['title']+'](v'+r['version']+'.md)\n' for r in ordered)+'''\n## Künftige Veröffentlichung

`releases.json` ist die einzige redaktionelle Quelle. Für jede neue App-Version einen vollständigen Eintrag hinzufügen, bestehende Einträge erhalten und `python3 kompass/release-notes/build.py` ausführen. Das erzeugt `catalog.js`, den sichtbaren Ordner `index.html` und die lesbaren Markdown-Dateien. Die App bindet den Katalog versionsgebunden ein; Offline-Dateien in `sw.js` beim Ergänzen mitführen. `build.py --check` prüft, ob die generierten Dateien aktuell sind. Die Release-Prüfung verlangt einen passenden Eintrag zur veröffentlichten `version.json`.

Automatisch angezeigt werden alle Releases neuer als `profile.releaseNotesSeen` bis einschliesslich zur geladenen App-Version, numerisch sortiert. Ohne gespeicherten Lesestand beginnt die Anzeige bei v1.9. Nach dem tatsächlichen automatischen Anzeigen wird der Stand ins Personenprofil geschrieben; zusätzlich merkt dieses Gerät den Versionsstand, auch wenn das Fenster direkt geschlossen wird. Die bestehende verschlüsselte Sicherung und Synchronisierung werden genutzt. Ein höherer bestätigter Stand hat beim Abgleich Vorrang, damit parallele Geräte und ein Rollback keine Rückstufung verursachen. Die automatische Anzeige wartet bei offenen Formularen/Scannern. Schliessen und Escape lösen keine erneute automatische Anzeige aus. Archivbesuche markieren nichts automatisch als gelesen.
'''
    return files

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files=build();bad=[]
    for name,text in files.items():
        dest=P/name
        if args.check:
            if not dest.exists() or dest.read_text()!=text:bad.append(name)
        else:dest.write_text(text)
    if bad:raise SystemExit('Outdated generated release files: '+', '.join(bad))
    print(('Verified' if args.check else 'Generated'),len(files),'release archive files.')
