"""Exercise actual app UI and encrypted persistence with synthetic API responses only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from datetime import datetime, timezone
import copy, json, os, subprocess, traceback
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
os.chdir(BASE)
OUT=BASE/'test-output';OUT.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),SimpleHTTPRequestHandler)
Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
engine=os.environ.get('TEST_BROWSER','chromium');checks=[];errors=[];unexpected=[]
ids=['11111111-1111-4111-8111-111111111111','22222222-2222-4222-8222-222222222222']
script="""global.window=global;require('./kompass/data.js');const C=require('./kompass/core.js');
const s=C.initial();s.profile={...s.profile,age:40,sex:'m',height:180,weight:80,manual:{protein:100,vitC:100,calcium:1000,energy:2000,fat:60,carbs:250,sugar:5}};
function entry(id,date,values){return {id,date,name:'Synthetic food '+id,kind:'food',meal:0,amountText:'100 g',n:Object.fromEntries(NK_DATA.nutrients.map(n=>[n.key,{value:values[n.key]??null,known:values[n.key]!=null?1:0,total:1,missing:values[n.key]!=null?[]:['Synthetic food '+id]}]))};}
s.entries=[entry('a','2026-09-21',{protein:100,vitC:120,calcium:500,energy:2000,fat:60,carbs:250,sugar:3}),entry('b','2026-09-22',{protein:100,vitC:80,calcium:500,energy:2000,fat:60,carbs:250,sugar:3}),entry('c','2026-09-23',{protein:30,vitC:200,calcium:300})];s.days={'2026-09-21':{complete:true},'2026-09-22':{complete:true},'2026-09-23':{complete:false}};
const t=C.clone(s);t.profile.sex='w';t.profile.reportFrequency='daily';t.profile.manual.vitC=95;t.entries=[entry('p','2026-09-21',{protein:30,vitC:95,calcium:1000})];t.days={'2026-09-21':{complete:true}};console.log(JSON.stringify([s,t]));"""
fixtures=json.loads(subprocess.check_output(['node','-e',script],text=True))
profiles={ids[i]:{'id':ids[i],'name':n,'revision':0,'state':fixtures[i]} for i,n in enumerate(['Dimitri','Patricia'])}
original_entries=copy.deepcopy(fixtures[0]['entries']);original_p=copy.deepcopy(fixtures[1])
def check(label,ok=True):
 assert ok,label
 checks.append(label);print('PASS',label,flush=True)
def api(route):
 data=route.request.post_data_json or {};a=data.get('action')
 if a=='login':r={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'b'*64}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[data['id']])}
 elif a=='save':
  p=profiles[data['id']]
  if p['revision']!=data['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
  p['revision']+=1;p['state']=data['state'];r={'revision':p['revision']}
 elif a=='catalog':r={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='logout':r={'ok':True}
 else:
  unexpected.append(a);return route.fulfill(status=400,json={'error':'Unexpected synthetic request'})
 route.fulfill(status=200,json=r)
def context(b):
 c=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/Zurich',service_workers='block',accept_downloads=True)
 def network(route):
  if route.request.url.startswith(URL):return route.continue_()
  if '/functions/v1/' in route.request.url:return api(route)
  unexpected.append(route.request.url);route.abort()
 c.route('**/*',network)
 return c
def page(c):
 p=c.new_page();p.clock.set_fixed_time(datetime(2026,9,26,12,0,0,tzinfo=timezone.utc));p.on('pageerror',lambda e:errors.append(str(e)));return p
def login(p):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator('#household-dialog[open]').wait_for()
def choose(p,id):
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open',arg=id)
def nav(p,r):
 p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
 if r=='reports' and p.locator('[data-action="report-expand-all"]').inner_text()=='Alle Details aufklappen':p.locator('[data-action="report-expand-all"]').click()
def report(p,k):return p.locator(f'[data-report-key="{k}"]')
with sync_playwright() as play:
 browser_args={}
 if engine=='chromium' and Path('/usr/bin/chromium').exists():browser_args={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']}
 browser=getattr(play,engine).launch(**browser_args);c=context(browser);p=page(c)
 try:
  login(p);choose(p,ids[0]);nav(p,'profile')
  check('Three report frequencies in profile',p.locator('#report-frequency option').count()==3)
  check('Legacy profile preselects weekly only in form',p.locator('#report-frequency').input_value()=='weekly' and p.evaluate('NK_APP.getState().profile.reportFrequency===undefined'))
  p.locator('#report-frequency').select_option('monthly');check('Selection alone is not saved',p.evaluate('NK_APP.getState().profile.reportFrequency===undefined'))
  p.locator('#profile-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().profile.reportFrequency==="monthly"');p.evaluate('NK_HOUSEHOLD.flush()')
  check('Frequency persisted through existing sync',profiles[ids[0]]['state']['profile']['reportFrequency']=='monthly')
  p.reload();p.wait_for_function('window.NK_APP && NK_HOUSEHOLD.id');nav(p,'profile');check('Frequency survives encrypted reload',p.locator('#report-frequency').input_value()=='monthly')
  nav(p,'reports');check('Reports navigation opens saved monthly preference','Monatsreport' in p.locator('#main h1').inner_text())
  check('All nutrient groups present',all(p.locator('.report-group h2').filter(has_text=s).count()==1 for s in ['Vitamine','Mengenelemente','Spurenelemente','Makronährstoffe']))
  check('Open diary comparison labelled provisional',report(p,'vitC').get_attribute('data-report-status')=='provisional')
  p.locator('[data-action="report-period"][data-frequency="weekly"]').click();check('Weekly Monday to Sunday calendar','21.09.2026' in p.locator('#main .sub').inner_text() and '27.09.2026' in p.locator('#main .sub').inner_text())
  check('Tab selection does not overwrite saved frequency',p.evaluate('NK_APP.getState().profile.reportFrequency')=='monthly')
  check('Unlogged and future days explicit','3 von 6' in p.locator('.report-coverage').inner_text() and '1 zukünftige' in p.locator('.report-coverage').inner_text())
  p.locator('.report-extra-options>summary').click();p.locator('#report-complete-only').check();check('Completed recorded vitamin mean reaches goal',report(p,'vitC').get_attribute('data-report-status')=='met' and '100 mg' in report(p,'vitC').inner_text())
  check('Known below target not confused with missing data',report(p,'calcium').get_attribute('data-report-status')=='below' and report(p,'vitB12').get_attribute('data-report-status')=='gaps')
  check('Incompatible folate has no percentage',report(p,'folate').get_attribute('data-report-status')=='incompatible');report(p,'folate').locator('summary').click();check('Folate explanation visible','Kein Prozentvergleich' in report(p,'folate').inner_text())
  check('No target explicitly displayed',report(p,'vitK').get_attribute('data-report-status')=='no_target')
  check('No unsafe sugar minimum assumed',report(p,'sugar').get_attribute('data-report-status')=='comparison')
  p.locator('#report-filter').select_option('met');check('Reached filter includes only assessed successes',all(x in ['met','within'] for x in p.locator('.report-nutrient').evaluate_all('(els)=>els.map(e=>e.dataset.reportStatus)')))
  p.locator('#report-filter').select_option('all');report(p,'vitB12').locator('summary').click();check('Missing product names available','Synthetic food a' in report(p,'vitB12').inner_text())
  report(p,'vitC').locator('summary').click();check('Distribution distinguishes days from mean','1 erreicht' in report(p,'vitC').inner_text() and '1 darunter' in report(p,'vitC').inner_text())
  with p.expect_download() as dl:p.locator('[data-action="report-export"]').click()
  download=dl.value;path=OUT/f'{engine}-report.csv';download.save_as(path);text=path.read_text();check('CSV export contains profile dates status and reference basis',all(x in text for x in ['Dimitri','2026-09-21','Vitamin C','Aktuelle gespeicherte Profilziele']))
  p.locator('[data-action="report-period"][data-frequency="daily"]').click();check('Empty day no false successes',p.locator('.report-counts b').first.inner_text()=='0' and 'Noch keine auswertbaren Tage' in p.locator('#main').inner_text())
  p.locator('#report-date').fill('2026-09-21');p.locator('#report-date').dispatch_event('change');check('Daily exact date comparison','Tagesreport' in p.locator('#main h1').inner_text() and report(p,'vitC').get_attribute('data-report-status')=='met')
  p.locator('[data-action="report-next"]').click();check('Next day navigation','22.09.2026' in p.locator('#main .sub').inner_text() and report(p,'vitC').get_attribute('data-report-status')=='below')
  p.locator('[data-action="report-period"][data-frequency="monthly"]').click();p.locator('#report-date').fill('2024-02-10');p.locator('#report-date').dispatch_event('change');check('Leap-month report boundary','29.02.2024' in p.locator('#main .sub').inner_text())
  p.locator('[data-action="report-current"]').click();p.locator('[data-action="report-previous-complete"]').click();check('Last closed month works','01.08.2026' in p.locator('#main .sub').inner_text())
  p.locator('.report-extra-options>summary').click();p.locator('#report-history').select_option('2026-09-01');check('Period archive opens previous data','September' not in p.locator('#main h1').inner_text() and '30.09.2026' in p.locator('#main .sub').inner_text())
  p.locator('#device-profile-button').click();choose(p,ids[1]);nav(p,'reports');check('Other profile uses own report frequency','Tagesreport' in p.locator('#main h1').inner_text());p.locator('#report-date').fill('2026-09-21');p.locator('#report-date').dispatch_event('change')
  check('Other profile own diary and goals only','Patricia' in p.locator('#main .sub').inner_text() and '95 mg' in report(p,'vitC').inner_text() and report(p,'vitC').get_attribute('data-report-status')=='met')
  check('Viewing report has not changed other profile',profiles[ids[1]]['state']==original_p)
  p.locator('#device-profile-button').click();choose(p,ids[0]);nav(p,'profile');p.locator('#report-frequency').select_option('daily');p.locator('details:has(#target-vitC)>summary').click();p.locator('#target-vitC').fill('200');p.locator('#profile-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().profile.manual.vitC===200');p.evaluate('NK_HOUSEHOLD.flush()');nav(p,'reports');p.locator('#report-date').fill('2026-09-21');p.locator('#report-date').dispatch_event('change');check('Saved target change updates historical comparison only',report(p,'vitC').get_attribute('data-report-status')=='below' and profiles[ids[0]]['state']['entries']==original_entries)
  c2=context(browser);p2=page(c2);login(p2);choose(p2,ids[0]);nav(p2,'profile');check('Report preference syncs to second device',p2.locator('#report-frequency').input_value()=='daily');c2.close()
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':950});p.wait_for_timeout(180);check(f'Reports fit {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-reports.png'),full_page=True)
  nav(p,'profile');p.locator('#report-frequency').scroll_into_view_if_needed();p.screenshot(path=str(OUT/f'{engine}-profile.png'))
  p.set_viewport_size({'width':320,'height':950});p.wait_for_timeout(180);check('Profile selector fits 320px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  nav(p,'reports');p.locator('[data-action="report-period"][data-frequency="weekly"]').click();p.locator('#report-date').fill('2026-09-21');p.locator('#report-date').dispatch_event('change')
  # Screenshot default collapsed overview, then test the real PDF workflow.
  if p.locator('[data-action="report-expand-all"]').inner_text()=='Details einklappen':p.locator('[data-action="report-expand-all"]').click()
  p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(180);p.screenshot(path=str(OUT/f'{engine}-visual-report.png'),full_page=True)
  check('Compact categories are collapsed initially',not p.locator('#report-group-vitamin').evaluate('(e)=>e.open'))
  p.locator('#report-group-vitamin>summary').click();check('Nutrient group expands on tap',report(p,'vitC').is_visible())
  before=p.evaluate('JSON.stringify(NK_APP.getState())')
  p.locator('[data-action="report-pdf"]').click();check('Export context shows correct profile and all-nutrient scope','Dimitri' in p.locator('#report-export-dialog').inner_text() and 'alle Nährstoffe' in p.locator('#report-export-dialog').inner_text())
  check('Creating PDF does not yet upload or save a file',p.locator('#pdf-download').count()==0)
  p.locator('input[name="pdf-layout"][value="compact"]').check();p.locator('#pdf-create').click();p.locator('#pdf-download').wait_for()
  check('Export ready links use on-device blob URLs',p.locator('#pdf-download').get_attribute('href').startswith('blob:') and p.locator('#pdf-open').get_attribute('href').startswith('blob:'))
  with p.expect_download() as download:p.locator('#pdf-download').click()
  compact=OUT/f'{engine}-compact.pdf';download.value.save_as(compact)
  from pypdf import PdfReader
  pdf=PdfReader(compact);text=' '.join(x.extract_text() for x in pdf.pages)
  check('Actual compact PDF is one page and names the profile',len(pdf.pages)==1 and 'Dimitri' in text)
  check('PDF preserves selected weekly dates','21.09.2026' in text and '27.09.2026' in text)
  check('Compact PDF warns about missing or open data','vorläufig' in text and 'Mangeldiagnose' in text)
  p.locator('input[name="pdf-layout"][value="full"]').check();p.locator('#pdf-create').click();p.wait_for_function('document.querySelector("#pdf-status").textContent.startsWith("Erstellt")')
  with p.expect_download() as download:p.locator('#pdf-download').click()
  full=OUT/f'{engine}-full.pdf';download.value.save_as(full);pdf=PdfReader(full);text=' '.join(x.extract_text() for x in pdf.pages)
  check('Full PDF contains vitamins minerals trace elements',all(x in text for x in ['Vitamin C','Calcium','Spurenelemente','Jod','Datenlücken']))
  check('Full PDF has meaningful source links',sum(len(page.get('/Annots',[])) for page in pdf.pages)>3)
  check('Full PDF does not contain other household profile', 'Patricia' not in text)
  check('PDF export never changes diary or targets',before==p.evaluate('JSON.stringify(NK_APP.getState())'))
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':950});p.wait_for_timeout(160);check(f'PDF dialog fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.locator('#pdf-close').click();p.locator('[data-action="report-period"][data-frequency="daily"]').click();p.locator('#report-date').fill('2026-09-25');p.locator('#report-date').dispatch_event('change');p.locator('[data-action="report-pdf"]').click();p.locator('input[name="pdf-layout"][value="compact"]').check();p.locator('#pdf-create').click();p.locator('#pdf-download').wait_for()
  with p.expect_download() as download:p.locator('#pdf-download').click()
  path=OUT/f'{engine}-empty.pdf';download.value.save_as(path);text=' '.join(x.extract_text() for x in PdfReader(path).pages)
  check('Empty export does not fake zero consumption','Keine Einträge' in text and '0 Tage berücksichtigt' in text)
  p.locator('#pdf-close').click()
  check('No runtime errors',not errors);check('No unmocked external data requests',not unexpected)
 except Exception:
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True)
  print('ERRORS',errors,'UNEXPECTED',unexpected);raise
 finally:
  (OUT/f'{engine}-reports-checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'runtimeErrors':errors,'unexpectedRequests':unexpected,'syntheticDataOnly':True},indent=2));browser.close();server.shutdown()
