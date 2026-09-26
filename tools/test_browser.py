from pathlib import Path
import json, copy, hashlib, threading, functools, os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1] if Path(__file__).parent.name=='tools' else Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(BASE)))
threading.Thread(target=server.serve_forever,daemon=True).start()
HOST=f'http://127.0.0.1:{server.server_port}'
URL=HOST+'/kompass/'
P='11111111-1111-4111-8111-111111111111';D='22222222-2222-4222-8222-222222222222'
initial={'schema':1,'profile':{'sex':'','age':None,'weight':None,'height':None,'special':False,'smoker':False,'menopause':'','phytate':'','manual':{}},'entries':[],'recipes':[],'foods':[],'favorites':[],'recent':[],'days':{},'recipeDraft':None}
profiles={i:{'id':i,'name':n,'revision':0,'state':copy.deepcopy(initial)} for i,n in [(P,'Patricia'),(D,'Dimitri')]}
profiles[P]['state']['profile'].update({'sex':'w','age':30,'weight':60,'height':170})
profiles[D]['state']['profile'].update({'sex':'m','age':40,'weight':80,'height':180})
(BASE/'test-output').mkdir(exist_ok=True)
passed=[];errors=[];flags={'offline':False,'lose_ack':False};calls=[]
def check(name,ok=True):
 assert ok,name
 passed.append(name);print('PASS',name,flush=True)
def route_handler(route):
 u=route.request.url
 if u.startswith(HOST+'/'):return route.continue_()
 if '/functions/v1/nutrient-' not in u:return route.abort()
 if flags['offline']:return route.abort()
 if route.request.method=='OPTIONS':return route.fulfill(status=204,headers={'Access-Control-Allow-Origin':'*','Access-Control-Allow-Headers':'content-type,x-nk-session','Access-Control-Allow-Methods':'POST,OPTIONS'})
 data=route.request.post_data_json or {};a=data.get('action');status=200;r={};calls.append((a,u))
 if u.endswith('nutrient-device-key'):r={'key':'ab'*32}
 elif u.endswith('nutrient-library'):
  items=[]
  for p in profiles.values():
   for kind in ['food','recipe']:
    for x in p['state'][kind+'s']:
     key='shared-'+hashlib.sha256((p['id']+'/'+kind+'/'+x['id']).encode()).hexdigest()
     items.append({'key':key,'kind':kind,'ownerId':p['id'],'ownerName':p['name'],'item':copy.deepcopy(x)})
  r={'version':1,'items':items,'skipped':0,'asOf':'2026-09-26T16:40:00Z'}
 elif a=='login':r={'token':'ab'*32,'expires':'2099-01-01T00:00:00Z'}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[data['id']])}
 elif a=='save':
  p=profiles[data['id']]
  if p['revision']!=data['revision']:status=409;r={'error':'Auf einem anderen Gerät geändert. Bitte beide Versionen prüfen.','conflict':True}
  else:
   p['revision']+=1;p['state']=copy.deepcopy(data['state']);r={'revision':p['revision']}
   if flags['lose_ack']:flags['lose_ack']=False;status=503;r={'error':'Synthetic response lost after commit'}
 elif a=='logout':r={'ok':True}
 else:status=400;r={'error':'Unexpected action '+str(a)}
 return route.fulfill(status=status,json=r,headers={'Access-Control-Allow-Origin':'*'})
def ctx(b):
 c=b.new_context(service_workers='block',viewport={'width':390,'height':844},accept_downloads=True)
 c.route('**/*',route_handler);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));return c,p
def login(p,url=URL,id=P):
 p.goto(url);p.locator('#gate-password').fill('test-password');p.locator('#gate-form button[type=submit]').click()
 p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('window.NK_APP && !document.querySelector("#app").hidden')
 if 'original' not in url:p.wait_for_function('window.NK_LIBRARY.asOf.length>0')
def nav(p,to):p.locator(f'.bottom-nav [data-route="{to}"]').click()
def sync(p,ok=True):
 r=p.evaluate('NK_HOUSEHOLD.flush().then(()=>"ok",e=>e.message)')
 if ok:assert r=='ok',r
 return r
def record(p,q='50'):
 nav(p,'search');p.locator('[data-action="filter"][data-filter="all"]').click();p.locator('#food-search').fill('planted.hack');p.locator('#search-results [data-id="veg-planted-hack"][data-action="food-pick"]').click();p.locator('#food-qty').fill(q);p.locator('#food-form button[type=submit]').click()
def custom(p,name='Pringles Test',protein='6.2'):
 nav(p,'search');p.locator('[data-action="new-food"]').first.click();p.locator('#custom-name').fill(name)
 for k,v in [('energy','512'),('protein',protein),('fat','29'),('carbs','54')]:p.locator('#custom-'+k).fill(v)
 p.locator('#custom-food-form button[type=submit]').click()
def recipe(p,name):
 nav(p,'recipes');p.locator('[data-action="new-recipe"]').first.click();p.locator('#recipe-name').fill(name);p.locator('#recipe-servings').fill('2');p.locator('[data-action="ingredient-search"]').click();p.locator('#ingredient-search').fill('planted.hack');p.locator('#ingredient-results [data-id="veg-planted-hack"][data-action="food-pick"]').click();p.locator('#food-qty').fill('100');p.locator('#food-form button[type=submit]').click();p.locator('[data-action="save-recipe"]').click()
with sync_playwright() as pl:
 b=getattr(pl,os.environ.get('TEST_BROWSER','chromium')).launch(headless=True)
 try:
  ca,pa=ctx(b);cb,pb=ctx(b);old=HOST+'/original/kompass/'
  login(pa,old);login(pb,old);record(pa);sync(pa);record(pb);sync(pb,False);record(pb,'60')
  check('Original iPhone error reproduced by stale revision', 'Browserspeicher ist voll' in pb.locator('#modal-error').inner_text())
  legacy=pb.evaluate('({session:sessionStorage.getItem("nk:session:1"),cache:localStorage.getItem("nk:encrypted-pending:1")})')
  ca.close();cb.close()
  # Upgrade that same device at the stable host: encrypted legacy state remains.
  cc,pc=ctx(b);pc.goto(URL);pc.evaluate('x=>{sessionStorage.setItem("nk:session:1",x.session);localStorage.setItem("nk:encrypted-pending:1",x.cache)}',legacy);pc.reload();pc.wait_for_function('window.NK_APP');sync(pc)
  check('Legacy encrypted pending entry recovered without wiping', len(profiles[P]['state']['entries'])==2)
  check('Legacy revision conflict automatically unblocked',not pc.evaluate('NK_HOUSEHOLD.conflicted'))
  # Two independent device contexts, same profile.
  cd,pd=ctx(b);login(pd);record(pc);sync(pc);record(pd);sync(pd)
  check('Two devices can add to the same diary',len(profiles[P]['state']['entries'])==4)
  check('Merged diary visible on saving device',pd.evaluate('NK_APP.getState().entries.length')==4)
  # Shared products already held in source profile, never injected into another diary.
  custom(pd);sync(pd);before=copy.deepcopy(profiles[D]['state'])
  ce,pe=ctx(b);login(pe,id=D);nav(pe,'search');pe.locator('#food-search').fill('Pringles Test');pe.locator('#search-results .food-open').first.wait_for()
  check('Patricia product appears in Dimitri normal search', 'Gemeinsam · Patricia' in pe.locator('#search-results').inner_text())
  shared_id=pe.locator('#search-results .food-open').first.get_attribute('data-id')
  pe.locator('#search-results .food-open').first.click();pe.locator('#food-qty').fill('50');pe.locator('#food-form button[type=submit]').click();sync(pe)
  check('Shared product logs into chosen profile only',len(profiles[D]['state']['entries'])==1 and len(profiles[P]['state']['entries'])==4)
  check('Shared product quantity calculated',profiles[D]['state']['entries'][0]['n']['protein']['value']==3.1)
  check('Personal goals not copied across profiles',profiles[D]['state']['profile']==before['profile'])
  # Shared recipes and non-destructive variants.
  recipe(pd,'Pasta Test');sync(pd);pe.evaluate('NK_LIBRARY.refresh(true)');nav(pe,'recipes')
  pe.locator('.recipe-card').filter(has_text='Pasta Test').wait_for();card=pe.locator('.recipe-card').filter(has_text='Pasta Test')
  check('Recipe visible to other profile', 'Von Patricia' in card.inner_text())
  card.locator('[data-action="log-recipe"]').click();pe.locator('#recipe-log-form button[type=submit]').click();sync(pe)
  check('Shared recipe can be logged without editing original',len(profiles[D]['state']['entries'])==2 and len(profiles[P]['state']['recipes'])==1)
  nav(pe,'recipes');pe.locator('[data-action="edit-recipe"]').first.click();pe.locator('#recipe-name').fill('Dimitri Variante');pe.locator('[data-action="save-recipe"]').click();sync(pe)
  check('Editing other recipe creates own variant',profiles[P]['state']['recipes'][0]['name']=='Pasta Test' and profiles[D]['state']['recipes'][0]['name']=='Dimitri Variante')
  # Change source product; prior diary snapshot immutable.
  old_snapshot=copy.deepcopy(profiles[D]['state']['entries'][0]);nav(pd,'search');pd.locator('#food-search').fill('Pringles Test');pd.locator('#search-results .food-open').first.click();pd.locator('#dialog details').last.locator('summary').click();pd.locator('[data-action="edit-custom-food"]').click();pd.locator('#custom-protein').fill('8');pd.locator('#custom-food-form button[type=submit]').click();sync(pd)
  check('Changes to product leave recorded nutrition unchanged',profiles[D]['state']['entries'][0]==old_snapshot)
  # True conflict deliberately preserves both and does not turn into storage error.
  cf,pf=ctx(b);login(pf);record(pd);sync(pd);pf.reload();pf.wait_for_function('window.NK_APP');pd.reload();pd.wait_for_function('window.NK_APP')
  for page,name in [(pd,'Patricia Edit A'),(pf,'Patricia Edit B')]:
   nav(page,'search');page.locator('#food-search').fill('Pringles Test');page.locator('#search-results .food-open').first.click();page.locator('#dialog details').last.locator('summary').click();page.locator('[data-action="edit-custom-food"]').click();page.locator('#custom-name').fill(name);page.locator('#custom-food-form button[type=submit]').click();sync(page,ok=page==pd)
  check('Conflicting edit is visibly retained',pf.evaluate('NK_HOUSEHOLD.conflicted'))
  custom(pf,'New product during conflict');check('New products still retained during conflict',pf.evaluate('NK_APP.getState().foods.some(f=>f.name==="New product during conflict")'))
  check('No false memory-full message',not pf.locator('body').inner_text().count('Browserspeicher ist voll'))
  pf.locator('#device-profile-button').click();pf.locator('[data-nk="resolve-conflict"]').click();pf.locator('#conflict-form').wait_for()
  for sel in pf.locator('#conflict-form select').all():sel.select_option('server')
  with pf.expect_download() as download:pf.locator('#conflict-form button[type=submit]').click()
  download.value.save_as(str(BASE/'test-output'/'synthetic-conflict-backup.json'))
  pf.wait_for_function('!NK_HOUSEHOLD.pending && !NK_HOUSEHOLD.conflicted')
  check('Conflict resolution also preserves unrelated new product',any(f['name']=='New product during conflict' for f in profiles[P]['state']['foods']))
  pf.locator('[data-nk="close"]').click()
  # Request succeeded but response lost: retry is idempotent with stable entry IDs.
  before_count=len(profiles[P]['state']['entries']);flags['lose_ack']=True;record(pf);sync(pf,False);sync(pf)
  check('Lost server acknowledgement does not duplicate entry',len(profiles[P]['state']['entries'])==before_count+1)
  # Offline edits remain encrypted and can be sent later.
  flags['offline']=True;record(pf);sync(pf,False);pf.wait_for_timeout(100)
  check('Offline pending entry has encrypted recovery copy',pf.evaluate('!!JSON.parse(localStorage.getItem("nk:encrypted-pending:1")).data'))
  flags['offline']=False;sync(pf);check('Offline entry synchronizes on reconnect',not pf.evaluate('NK_HOUSEHOLD.pending'))
  nav(pf,'today');check('Daily protein need retained',pf.locator('.protein-target').is_visible())
  pf.set_viewport_size({'width':320,'height':740});check('320px overview does not overflow',pf.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  pf.screenshot(path=str(BASE/'test-output'/'mobile-overview.png'))
  pe.evaluate('NK_LIBRARY.refresh(true)');nav(pe,'search');pe.locator('#food-search').fill('Patricia Edit A');pe.locator('#search-results .food-open').first.click();pe.screenshot(path=str(BASE/'test-output'/'shared-product.png'))
  check('No JavaScript runtime errors',not errors)
  print('TOTAL',len(passed),flush=True)
 except Exception:
  import traceback
  (BASE/'test-output'/'failure.txt').write_text(traceback.format_exc())
  for name,pg in list(locals().copy().items()):
   if name.startswith('p') and hasattr(pg,'screenshot'):
    try:pg.screenshot(path=str(BASE/'test-output'/('failure-'+name+'.png')))
    except:pass
  print('ERRORS',errors,flush=True);raise
 finally:
  (BASE/'test-output'/'browser-report.json').write_text(json.dumps({'passed':len(passed),'checks':passed,'runtimeErrors':errors},indent=2))
  b.close();server.shutdown()
