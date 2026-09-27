"""Actual browser UI + synthetic household/API. No real users or photo uploads."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,subprocess,base64
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
OUT=ROOT/'test-output';OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
initial=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/core.js').initial()))"]))
profiles={i:{'id':i,'name':name,'revision':0,'state':copy.deepcopy(initial)} for i,name in [('test-d','Dimitri'),('test-p','Patricia')]}
requests=[];unexpected=[];errors=[];checks=[];lookup_error=False
product={'code':'4006381333931','product_name':'Phototest Cocoa','brands':'Phototest','quantity':'120 g','nutriments':{'energy-kcal_100g':500,'proteins_100g':10,'carbohydrates_100g':40,'fat_100g':30,'sugars_100g':0,'salt_100g':.2}}
drink={**product,'code':'96385074','product_name':'Phototest Drink','quantity':'1 l'}
def check(name,ok=True):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
def api(route):
 global lookup_error
 req=route.request;d=req.post_data_json or {};requests.append((req.url,d));a=d.get('action')
 if a=='login':r={'token':'f'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'ab'*32}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[d['id']])}
 elif a=='save':
  p=profiles[d['id']];p['state']=d['state'];p['revision']+=1;r={'revision':p['revision']}
 elif a=='catalog':r={'profiles':[{**{k:p[k] for k in ['id','name','revision']},'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a in ['barcode','search']:
  if lookup_error:return route.fulfill(status=503,json={'error':'Synthetic offline service'})
  selected=drink if 'drink' in d.get('query','').lower() else product
  r={'product':selected} if a=='barcode' else {'products':[] if d.get('query')=='ZZUnknown product' else [selected]}
 elif a=='logout':r={'ok':True}
 else:raise AssertionError('Unexpected action '+str(d))
 return route.fulfill(status=200,json=r)
STUB='''window.__ocrText='Phototest\\nCocoa\\n120 g';window.__ocrCalls=0;window.__ocrDelay=0;window.__barcode='';
window.Tesseract={createWorker:async()=>({setParameters:async()=>{},recognize:async()=>{window.__ocrCalls++;const text=window.__ocrText;await new Promise(r=>setTimeout(r,window.__ocrDelay));return {data:{text}};},terminate:async()=>{}})};
window.ZXingBrowser={BrowserMultiFormatReader:class{decodeFromCanvas(){if(!window.__barcode)throw Error('not found');return {getText:()=>window.__barcode};}}};'''
def context(browser,stub=True):
 c=browser.new_context(viewport={'width':390,'height':844},service_workers='block',accept_downloads=True)
 if stub:c.add_init_script(STUB)
 def route(r):
  if '/functions/v1/' in r.request.url:return api(r)
  if r.request.url.startswith(URL) or r.request.url.startswith('blob:'+URL.split('/kompass/')[0]+'/'):return r.continue_()
  unexpected.append(r.request.url);return r.abort()
 c.route('**/*',route);return c

def login(p,id='test-d'):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#app").hidden',arg=id)
def nav(p,r):p.locator(f'[data-action="nav"][data-route="{r}"]:visible').first.click()
def upload(p):
 data=p.evaluate('''()=>{const c=document.createElement('canvas');c.width=1000;c.height=600;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,1000,600);x.fillStyle='black';x.font='bold 64px Arial';x.fillText('REDEFINE',50,120);x.fillText('FLANK STEAK',50,240);return c.toDataURL('image/png').split(',')[1];}''')
 p.locator('#gallery-photo').set_input_files({'name':'synthetic-package.png','mimeType':'image/png','buffer':base64.b64decode(data)})
 p.locator('#recognize-product').wait_for(state='visible')
def scan(p):
 nav(p,'search');p.locator('[data-nk-scan]:visible').first.click();upload(p)
def identify(p):p.locator('#recognize-product').click();p.wait_for_function('document.querySelectorAll("[data-photo-match]").length>0')
def confirm_product(p,basis='g'):
 p.locator('[data-photo-match]').last.click()
 if not p.locator('#photo-product-basis').is_disabled():p.locator('#photo-product-basis').select_option(basis)
 p.locator('#photo-product-checked').check();p.locator('#photo-product-confirm button[type=submit]').click()
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
 launch={'headless':True}
 if os.environ.get('LOCAL_CHROME'):launch['executable_path']='/usr/bin/chromium'
 b=getattr(play,engine).launch(**launch);c=context(b);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  login(p);scan(p)
  check('One photo offers product and nutrition actions',p.locator('#recognize-photo').is_visible())
  check('Photo selection alone sends no lookup',not any(x[1]['action'] in ['search','barcode'] for x in requests))
  identify(p)
  check('Photo text automatically starts name lookup',any(x[1]=={'action':'search','query':'Phototest Cocoa'} for x in requests))
  check('Recognition did not save a product',p.evaluate('NK_APP.getState().foods.length')==0)
  p.wait_for_function('!document.querySelector("#scan-status").textContent.includes("geladen")');check('Completed product search clears stale OCR progress')
  p.locator('[data-photo-match]').first.click();check('External 100g/ml basis must be chosen',p.locator('#photo-product-basis').input_value()=='')
  p.locator('#photo-product-confirm button[type=submit]').click();check('Unconfirmed result cannot transfer',p.locator('#scan-dialog').is_visible())
  p.locator('#photo-product-basis').select_option('g');p.locator('#photo-product-checked').check();p.locator('#photo-product-confirm button[type=submit]').click()
  check('Review editor receives exact numeric and missing values',p.locator('#custom-protein').input_value()=='10' and p.locator('#custom-vitC').input_value()=='' and p.locator('#custom-sugar').input_value()=='0')
  p.locator('#custom-piece-size').fill('30');p.locator('#custom-food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().foods.length===1');p.evaluate('NK_HOUSEHOLD.flush()')
  check('Only explicit save persists template with piece definition',len(profiles['test-d']['state']['foods'])==1 and profiles['test-d']['state']['foods'][0]['portion']['size']==30)
  check('Template is not consumed automatically',len(profiles['test-d']['state']['entries'])==0)
  scan(p);p.evaluate("window.__barcode='4006381333931'");before=p.evaluate('__ocrCalls');identify(p);check('Barcode in photo skips text recognition',p.evaluate('__ocrCalls')==before)
  confirm_product(p);p.locator('#food-form').wait_for();check('Existing product reused rather than duplicated',p.evaluate('NK_APP.getState().foods.length')==1)
  check('Piece quantity preserved from product',p.locator('#food-unit').input_value()=='piece');p.locator('#food-form button[type=submit]').click();p.wait_for_function('NK_APP.getState().entries.length===1');p.evaluate('NK_HOUSEHOLD.flush()')
  nav(p,'search');p.locator('[data-action="new-food"]').click();p.locator('#custom-name').fill('My unsaved cup');p.locator('#custom-piece-label').fill('Becher');p.locator('#custom-piece-size').fill('150');p.locator('#custom-piece-unit').select_option('ml');p.locator('[data-action="custom-photo"]').click();upload(p)
  p.evaluate("window.__barcode='';window.__ocrText='Phototest\\nDrink'");identify(p);confirm_product(p,'ml')
  check('Photo works inside unsaved own-product editor',p.locator('#custom-basis').input_value()=='ml' and p.locator('#custom-piece-size').input_value()=='150' and p.locator('#custom-piece-label').input_value()=='Becher')
  check('Photo transfer leaves draft unsaved',p.evaluate('NK_APP.getState().foods.length')==1)
  p.locator('[data-action="custom-photo"]').click();upload(p);p.evaluate("window.__ocrText='per 30 g\\nEnergy 150 kcal\\nFat 9 g\\nCarbohydrates 12 g\\nProtein 3 g'")
  p.locator('#recognize-photo').click();p.locator('#scan-amount').wait_for();check('Same upload can directly read nutrition',p.locator('#scan-amount').input_value()=='30')
  check('30g normalization retained','10 g'==p.locator('#scan-out-protein').inner_text())
  p.locator('#scan-raw-protein').fill('6');p.evaluate("window.__ocrText='Phototest\\nDrink'");identify(p);p.locator('#recognize-photo').click();check('Switching modes preserves manually corrected raw values',p.locator('#scan-raw-protein').input_value()=='6' and p.locator('#scan-out-protein').inner_text()=='20 g')
  p.locator('#scan-close').click();check('Cancelling photo preserves unsaved parent product',p.locator('#custom-piece-size').input_value()=='150' and p.locator('#custom-basis').input_value()=='ml')
  p.locator('#dialog [data-action="close-dialog"]').click();scan(p);p.evaluate("window.__ocrText='';window.__barcode=''");count=len(requests);p.locator('#recognize-product').click();p.wait_for_function('document.querySelector("#photo-product-status").textContent.includes("Keine lesbare")')
  check('Unreadable image does not send guessed query',not any(x[1]['action']=='search' for x in requests[count:]))
  p.locator('#photo-product-query').fill('ZZUnknown product');p.locator('#photo-product-search button').click();p.wait_for_function('document.querySelector("#photo-product-status").textContent.includes("Kein Treffer")');check('No result stays explicit without invented nutrients')
  lookup_error=True;p.locator('#photo-product-query').fill('Phototest Cocoa');p.locator('#photo-product-search button').click();p.wait_for_function('document.querySelector("#photo-product-status").textContent.includes("Online-Suche:")');check('Network error preserves local matches',p.locator('[data-photo-match]').count()>0);lookup_error=False
  p.screenshot(path=str(OUT/f'{engine}-photo-results.png'),full_page=True)
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(120);check(f'Photo panel fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  p.set_viewport_size({'width':390,'height':844});p.locator('#scan-close').click();scan(p);p.evaluate("window.__ocrText='Late product';window.__ocrDelay=600");p.locator('#recognize-product').click();p.wait_for_timeout(60);p.locator('#scan-close').click();p.locator('[data-nk-scan]:visible').first.click();p.wait_for_timeout(750)
  check('Closed scan cannot populate a newer dialog',p.locator('#photo-product-review').count()==0 and p.locator('#scan-review').inner_text()=='')
  p.locator('#scan-close').click();p.evaluate('NK_HOUSEHOLD.flush()');c2=context(b);p2=c2.new_page();login(p2,'test-p');p2.evaluate('NK_SHARED.refresh(true)');check('Other profile sees shared photo template',p2.evaluate('NK_SHARED.foods().some(f=>f.name.includes("Phototest"))'))
  check('Other profile diary stays separate',p2.evaluate('NK_APP.getState().entries.length')==0);c2.close()
  p.reload();p.wait_for_function('window.NK_APP');check('Reload preserves entries and piece definition',p.evaluate('NK_APP.getState().entries.length===1 && NK_APP.getState().foods[0].portion.size===30'))
  check('Reports and PDF module retained',p.evaluate('!!window.NK_REPORT_PDF'))
  if os.environ.get('REAL_OCR')=='1':
   real=context(b,stub=False);pr=real.new_page();login(pr);scan(pr);pr.locator('#recognize-product').click();pr.wait_for_function('document.querySelector("#photo-product-query")?.value.toLowerCase().includes("flank")',timeout=60000);check('Real bundled OCR reads synthetic packaging without an image upload');real.close()
  lookups=[d for u,d in requests if d.get('action') in ['search','barcode']];check('Network lookup payloads contain only query or barcode',all(set(d)<=({'action','query'} if d['action']=='search' else {'action','code'}) for d in lookups))
  check('No unexpected external requests',not unexpected);check('No JavaScript runtime errors',not errors)
 except Exception:
  import traceback
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc()+str(errors));p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-6500:]);raise
 finally:
  (OUT/f'{engine}-photo-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'unexpected':unexpected,'realOCR':os.environ.get('REAL_OCR')=='1'},indent=2));b.close();server.shutdown()
