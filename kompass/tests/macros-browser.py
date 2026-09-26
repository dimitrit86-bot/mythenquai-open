"""Real browser/profile/sync integration; every remote request is mocked. No real private data."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,re,traceback,sys
BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'test-output';OUT.mkdir(exist_ok=True)
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(BASE)))
Thread(target=server.serve_forever,daemon=True).start()
url=(BASE/'kompass').as_uri()+'/' if os.environ.get('LOCAL_FILE_RENDER') else f'http://127.0.0.1:{server.server_port}/kompass/'
entry=url+'index.html' if url.startswith('file:') else url
D='11111111-1111-4111-8111-111111111111';P='22222222-2222-4222-8222-222222222222'
initial={'schema':1,'profile':{'sex':'m','age':40,'weight':80,'height':180,'special':False,'smoker':False,'menopause':'','phytate':'','manual':{}},'entries':[],'recipes':[],'foods':[],'favorites':[],'recent':[],'days':{},'recipeDraft':None}
profiles={i:{'id':i,'name':n,'revision':0,'state':copy.deepcopy(initial)} for i,n in [(D,'Dimitri'),(P,'Patricia')]}
profiles[P]['state']['profile'].update({'sex':'w','age':35,'weight':65,'height':170})
profiles[P]['state']['foods']=[{'id':'custom-shared-test','name':'Gemeinsames Testprodukt','basis':'g','density':None,'kind':'custom','source':'Synthetische Testwerte','category':'Eigene Produkte','n':{'energy':200,'protein':20,'carbs':20,'fat':5},'q':{}}]
passed=[];errors=[];calls=[]
def check(name,ok=True):
 assert ok,name
 passed.append(name);print('PASS',name,flush=True)
def api(route):
 try:
  b=route.request.post_data_json or {};a=b.get('action');calls.append(a)
  if a=='login':r={'token':'a'*64,'expires':'2099-01-01T00:00:00Z'}
  elif a=='key':r={'key':'b'*64}
  elif a=='profiles':r={'profiles':[{k:v for k,v in p.items() if k!='state'} for p in profiles.values()]}
  elif a=='get':r={'profile':copy.deepcopy(profiles[b['id']])}
  elif a=='save':
   p=profiles[b['id']]
   if p['revision']!=b['revision']:return route.fulfill(status=409,json={'conflict':True,'error':'Synthetic conflict'})
   p['state']=copy.deepcopy(b['state']);p['revision']+=1;r={'revision':p['revision']}
  elif a=='catalog':r={'profiles':[{'id':p['id'],'name':p['name'],'revision':p['revision'],'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
  else:raise AssertionError('Unexpected network operation: '+str(a))
  route.fulfill(status=200,json=r)
 except Exception as e:
  errors.append('Mock API: '+str(e));route.fulfill(status=500,json={'error':str(e)})
def route_all(route):
 if '/functions/v1/' in route.request.url:return api(route)
 if route.request.url.startswith(url):return route.continue_()
 return route.abort()
def nav(p,r):p.locator(f'.nav-btn[data-route="{r}"]:visible').first.click()
def active(p,id):p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#household-dialog").open',arg=id)
def choose(p,id):
 p.locator('#device-profile-button').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();active(p,id)
def save(p):
 p.locator('#profile-form button[type="submit"]').click();p.wait_for_function('!NK_APP.hasDraft');p.evaluate('NK_HOUSEHOLD.flush()')
def preview(p,k):return p.locator(f'[data-preview-target="{k}"]').inner_text()
def target(p,k):return p.locator(f'[data-daily-target="{k}"]').inner_text()
def snapshot(p):return p.evaluate('NK_APP.getState()')
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as pw:
 exe=os.environ.get('CHROMIUM_EXECUTABLE')
 browser=getattr(pw,engine).launch(**({'executable_path':exe} if engine=='chromium' and exe else {}))
 ctx=browser.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True)
 ctx.route('**/*',route_all);p=ctx.new_page();p.set_default_timeout(10000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('dialog',lambda d:d.accept())
 try:
  p.goto(entry);p.locator('#gate-password').fill('synthetic-test-only');p.locator('#gate-form button[type="submit"]').click();p.locator(f'[data-nk="choose"][data-id="{D}"]').click();active(p,D)
  check('existing profile loads without migration',snapshot(p)['profile'].get('nutritionMode') is None)
  check('legacy protein reference visible in empty diary','64' in target(p,'protein') and 'Noch nicht' in target(p,'carbs'))
  nav(p,'profile');check('all four presets inside profile form',p.locator('#profile-form #nutrition-mode option').count()==5)
  before=json.dumps(snapshot(p),sort_keys=True)
  p.locator('#nutrition-mode').select_option('normal');p.locator('#activity-pal').select_option('1.4');p.wait_for_function('document.querySelector("[data-preview-target=energy]").textContent.includes("kcal") && !document.querySelector("[data-preview-target=energy]").textContent.includes("—")')
  check('preview does not save profile',before==json.dumps(snapshot(p),sort_keys=True))
  for mode,amount in [('muscle','128'),('sport','112'),('loss','96'),('normal','64')]:
   p.locator('#nutrition-mode').select_option(mode);check('live preview '+mode,amount in preview(p,'protein'))
  save(p);check('mode and activity persisted via actual sync',profiles[D]['state']['profile']['nutritionMode']=='normal' and profiles[D]['state']['profile']['activityPAL']==1.4)
  nav(p,'today');check('all macro goals visible with no intake',all('Noch nicht' not in target(p,k) for k in ['protein','carbs','fat','energy']))
  check('empty intake is not zero',all('—' in p.locator(f'[data-macro-card={k}] .metric-number').inner_text() for k in ['protein','carbs','fat']))
  p.screenshot(path=str(OUT/f'{engine}-overview-empty.png'),full_page=True)
  p.reload();active(p,D);nav(p,'profile');check('saved selector restored after reload',p.locator('#nutrition-mode').input_value()=='normal')
  p.locator('#weight').fill('75,5');p.wait_for_timeout(200);check('comma weight updates preview', '60.4' in preview(p,'protein'))
  save(p);nav(p,'today');check('saved weight updates daily goal','60.4' in target(p,'protein'))
  nav(p,'profile');p.locator('#nutrition-mode').select_option('muscle');p.locator('#target-protein').fill('100');p.locator('#target-energy').fill('2400');p.wait_for_timeout(200);save(p)
  p.locator('#nutrition-mode').select_option('loss');check('switching mode keeps own protein and energy','100' in preview(p,'protein') and '2400' in preview(p,'energy').replace(chr(39),'').replace('’',''));save(p)
  check('own fields survive save',profiles[D]['state']['profile']['manual']=={'energy':2400,'protein':100})
  p.locator('#target-protein').fill('');p.locator('#target-energy').fill('');p.locator('#nutrition-mode').select_option('muscle');p.wait_for_timeout(200);save(p);nav(p,'today');check('clearing own targets restores automatic plan','120.8' in target(p,'protein'))
  choose(p,P);nav(p,'profile');check('second profile untouched',p.locator('#nutrition-mode').input_value()=='' and p.locator('#weight').input_value()=='65')
  p.locator('#nutrition-mode').select_option('normal');p.locator('#activity-pal').select_option('1.6');save(p);nav(p,'today');check('profile switch uses correct body data','52' in target(p,'protein'))
  choose(p,D);check('first profile keeps different preset','120.8' in target(p,'protein'))
  nav(p,'search');p.locator('#food-search').fill('Gemeinsames Testprodukt');p.locator('#search-results [data-action="food-pick"]').first.wait_for();check('household shared products still searchable')
  p.locator('#food-search').fill('planted.hack');p.locator('#search-results [data-action="food-pick"][data-id="veg-planted-hack"]').click();p.locator('#food-qty').fill('100');p.locator('#food-form button[type="submit"]').click();p.wait_for_function('NK_APP.getState().entries.length===1');p.evaluate('NK_HOUSEHOLD.flush()')
  frozen=json.dumps(snapshot(p)['entries'],sort_keys=True);check('diary intake and remaining displayed','18' in p.locator('[data-macro-card=protein] .metric-number').inner_text() and '102.8' in p.locator('[data-macro-card=protein] .metric-bottom').inner_text())
  nav(p,'profile');p.locator('#nutrition-mode').select_option('sport');save(p);check('target changes never rewrite diary snapshots',frozen==json.dumps(snapshot(p)['entries'],sort_keys=True))
  with p.expect_download() as dl:p.locator('[data-action="export"]').first.click()
  backup=OUT/f'{engine}-synthetic-backup.json';dl.value.save_as(str(backup));data=json.loads(backup.read_text());check('export includes preset and activity',data['profile']['nutritionMode']=='sport' and data['profile']['activityPAL']==1.4)
  p.locator('#nutrition-mode').select_option('normal');save(p);p.locator('#backup-input').set_input_files(str(backup));p.wait_for_function('NK_APP.getState().profile.nutritionMode==="sport"');p.evaluate('NK_HOUSEHOLD.flush()');check('backup reimport restores same personal goals')
  nav(p,'profile');p.locator('#target-protein').fill('18');save(p);nav(p,'today');p.locator('#protein-party[open]').wait_for();check('Spanish celebration uses updated protein target','18 / 18' in p.locator('#party-amount').inner_text());p.locator('#party-close').click();p.reload();active(p,D);p.wait_for_timeout(350);check('celebration not repeated after reload',p.locator('#protein-party[open]').count()==0)
  nav(p,'profile');p.locator('#target-protein').fill('');p.locator('#special').check();save(p);nav(p,'today');check('special situations suppress automatic macro goals',all('Noch nicht' in target(p,k) for k in ['protein','carbs','fat']))
  nav(p,'profile');p.locator('#special').uncheck();p.locator('#nutrition-mode').select_option('muscle');save(p)
  p.locator('[data-action="sources"]').click();check('source help describes automatic energy and model assumptions','DGE-Ruheenergieformel' in p.locator('#dialog').inner_text() and 'App-Annahmen' in p.locator('#dialog').inner_text());p.locator('#dialog [data-action="close-dialog"]').click()
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':950});p.evaluate('() => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');check(f'profile width {w} no horizontal overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'));p.screenshot(path=str(OUT/f'{engine}-profile-{w}.png'))
   nav(p,'today');check(f'overview width {w} no horizontal overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'));p.screenshot(path=str(OUT/f'{engine}-overview-{w}.png'));nav(p,'profile')
  check('other profile diary remains separate',profiles[P]['state']['entries']==[])
  p.locator('#target-energy').fill('2000');check('unsaved profile protected',p.evaluate('NK_DEVICE.hasUnsavedForm()'))
  check('no runtime errors',not errors)
 except Exception:
  layout=p.evaluate("() => {\n const result={width:innerWidth,scroll:document.documentElement.scrollWidth};\n result.elements=[...document.querySelectorAll('body *')].filter(e=>e.scrollWidth>e.clientWidth+1).slice(0,60).map(e=>({tag:e.tagName,id:e.id,cls:String(e.className),text:e.textContent.slice(0,60),right:e.getBoundingClientRect().right,width:e.clientWidth,scroll:e.scrollWidth,display:getComputedStyle(e).display}));\n const rules=['#profile-form select{overflow:hidden;text-overflow:ellipsis}','#profile-form{overflow-wrap:anywhere}','details:not([open])>:not(summary){display:none!important}','#toast{display:none!important}'];\n result.probes=[];for(const rule of rules){const style=document.createElement('style');style.textContent=rule;document.head.append(style);result.probes.push({rule,scroll:document.documentElement.scrollWidth});style.remove();}\n return result;\n}")
  (OUT/f'{engine}-layout.json').write_text(json.dumps(layout,indent=2))
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc());p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print('ERRORS',errors,flush=True);print(p.locator('body').inner_text()[-3000:],flush=True);raise
 finally:
  (OUT/f'{engine}-macro-report.json').write_text(json.dumps({'passed':len(passed),'checks':passed,'errors':errors,'syntheticOnly':True},indent=2));browser.close();server.shutdown()
