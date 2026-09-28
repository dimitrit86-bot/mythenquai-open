"""Real UI and encrypted storage, synthetic household only. No production data."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,subprocess
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
OUT=ROOT/'test-output-daily';OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
initial=json.loads(subprocess.check_output(['node','-e',"global.window=global;require('./kompass/data.js');const C=require('./kompass/core.js'),s=C.initial(),keys=NK_DATA.nutrients.map(n=>n.key);s.profile.releaseNotesSeen='1.11.0';s.profile.age=40;const f={id:'sample',name:'Test Meal',basis:'g',density:null,n:Object.fromEntries(keys.map(k=>[k,k==='protein'?10:k==='energy'?100:null]))};s.entries=['2026-09-26','2026-09-27','2026-09-28'].map((date,i)=>({id:'e'+i,date,meal:1,kind:'food',name:'Test Meal',amountText:'100 g',n:C.snapshot(f,100,'g',null,keys)}));s.days['2026-09-27']={complete:false};console.log(JSON.stringify(s));"]))
profiles={i:{'id':i,'name':name,'revision':0,'state':copy.deepcopy(initial)} for i,name in [('test-d','Dimitri'),('test-p','Patricia')]}
requests=[];unexpected=[];errors=[];checks=[];server_down=False
def check(name,ok=True):
 assert ok,name
 checks.append(name);print('PASS',name,flush=True)
def api(route):
 req=route.request;d=req.post_data_json or {};requests.append(d);a=d.get('action')
 if a=='login':r={'token':'f'*64,'expires':'2099-01-01T00:00:00Z'}
 elif a=='key':r={'key':'ab'*32}
 elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
 elif a=='get':r={'profile':copy.deepcopy(profiles[d['id']])}
 elif a=='save':
  if server_down:return route.fulfill(status=503,json={'error':'Synthetic server unavailable'})
  p=profiles[d['id']]
  if d['revision']!=p['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
  p['state']=d['state'];p['revision']+=1;r={'revision':p['revision']}
 elif a=='catalog':r={'profiles':[{**{k:p[k] for k in ['id','name','revision']},'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
 elif a=='logout':r={'ok':True}
 else:raise AssertionError(str(d))
 return route.fulfill(status=200,json=r)
CLOCK="""(()=>{const RealDate=Date,base=RealDate.now(),start=RealDate.parse('2026-09-28T10:00:00+02:00');window.__dayOffset=0;window.Date=class extends RealDate{constructor(...args){super(...(args.length?args:[start+(RealDate.now()-base)+window.__dayOffset]));}static now(){return start+(RealDate.now()-base)+window.__dayOffset;}};})();"""
def context(b,sw=False):
 c=b.new_context(viewport={'width':390,'height':844},timezone_id='Europe/Zurich',service_workers='allow' if sw else 'block',accept_downloads=True)
 c.add_init_script(CLOCK)
 def route(r):
  if '/functions/v1/' in r.request.url:return api(r)
  if r.request.url.startswith(URL):return r.continue_()
  unexpected.append(r.request.url);return r.abort()
 c.route('**/*',route);return c

def login(p,id='test-d'):
 p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP&&NK_HOUSEHOLD.id===id&&!document.querySelector("#app").hidden',arg=id)
def nav(p,r):p.locator(f'[data-action="nav"][data-route="{r}"]:visible').first.click()
def flush(p):p.wait_for_function('!NK_APP.hasDraft');p.evaluate('NK_HOUSEHOLD.flush()')
def no(p,id):p.wait_for_timeout(330);return p.locator('#'+id+'[open]').count()==0
def reset_person(id,entries=True,complete=False):
 s=copy.deepcopy(initial);s['profile']['releaseNotesSeen']='1.12.0';s['days']['2026-09-27']['complete']=complete
 if not entries:s['entries']=[]
 profiles[id]['state']=s;profiles[id]['revision']+=1
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
 launch={'headless':True}
 if os.environ.get('LOCAL_CHROME'):launch['executable_path']='/usr/bin/chromium'
 b=getattr(play,engine).launch(**launch);c=context(b);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 try:
  p.goto(URL);p.locator('#gate-password').wait_for();check('No automatic messages before login',no(p,'release-notes-dialog') and no(p,'day-review-dialog'))
  login(p);p.locator('#release-notes-dialog[open]').wait_for()
  check('Only new release shown, not old archived versions',p.locator('#release-notes-dialog [data-release-version]').evaluate_all('(xs)=>xs.map(e=>e.dataset.releaseVersion)')==['1.12.0'])
  p.wait_for_function('NK_APP.getState().profile.releaseNotesSeen==="1.12.0"');flush(p)
  check('Release saved as shown without any click',profiles['test-d']['state']['profile']['releaseNotesSeen']=='1.12.0')
  check('Dialog does not vanish after automatic saving',p.locator('#release-notes-dialog').is_visible())
  check('Yesterday prompt waits behind release notes',no(p,'day-review-dialog'))
  p.locator('#release-notes-dialog [data-release-action="close"]').first.click();p.locator('#day-review-dialog[open]').wait_for()
  check('Yesterday date and profile are clear','27. September' in p.locator('#day-review-description').inner_text() and p.locator('.day-review-for').inner_text()=='Für Dimitri')
  check('Showing the prompt does not set completion',not p.evaluate('NK_APP.getState().days["2026-09-27"].complete'))
  before=p.evaluate('NK_APP.getState()')
  for w in [320,390,1440]:
   p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(120);check(f'Yesterday prompt fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#day-review-dialog").scrollWidth<=document.querySelector("#day-review-dialog").clientWidth'))
  p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-yesterday.png'))
  p.locator('[data-day-review="yes"]').click();p.wait_for_function('!document.querySelector("#day-review-dialog").open');flush(p)
  after=p.evaluate('NK_APP.getState()');check('Yes directly sets the existing completion flag',after['days']['2026-09-27']['complete'])
  check('Only yesterday and prompt metadata changed',after['entries']==before['entries'] and after['recipes']==before['recipes'] and after['foods']==before['foods'] and after['days'].get('2026-09-28')==before['days'].get('2026-09-28'))
  p.evaluate('NK_APP.openDay("2026-09-27")');check('Existing diary checkbox is immediately checked',p.locator('#day-complete').is_checked())
  check('Complete-day reporting picks up the flag',p.evaluate('NK.history(NK_APP.getState(),"2026-09-28",7,["protein"],true).completeDays')==1)
  p.reload();p.wait_for_function('window.NK_APP');check('Neither notice repeats after ordinary reload',no(p,'release-notes-dialog') and no(p,'day-review-dialog'))
  c2=context(b);p2=c2.new_page();login(p2);check('Same profile on another device does not repeat notices',no(p2,'release-notes-dialog') and no(p2,'day-review-dialog'));c2.close()
  p.locator('#release-notes-button').click();p.locator('#release-notes-dialog[open]').wait_for();check('Manual archive is always accessible',p.locator('#release-notes-dialog [data-release-version="1.9.0"]').count()==1)
  check('No read-confirmation or Later requirement for release notes',p.locator('#release-notes-dialog [data-release-action="ack"]').count()==0 and 'Gelesen – weiter' not in p.locator('#release-notes-dialog .release-footer').inner_text())
  p.keyboard.press('Escape');p.reload();p.wait_for_function('window.NK_APP');check('Escape also prevents repeated automatic release notices',no(p,'release-notes-dialog'))
  p.locator('#device-profile-button').click();p.locator('[data-nk="choose"][data-id="test-p"]').click();p.locator('#release-notes-dialog[open]').wait_for();check('Other profile receives its own release notice',p.locator('.release-for').inner_text()=='Für Patricia')
  p.keyboard.press('Escape');p.locator('#day-review-dialog[open]').wait_for();p.locator('[data-day-review="no"]').click();p.wait_for_function('!document.querySelector("#day-review-dialog").open');flush(p)
  check('No opens yesterday without ticking completion',p.locator('#diary-date').input_value()=='2026-09-27' and not p.locator('#day-complete').is_checked())
  check('No is saved per profile while Dimitri remains complete',profiles['test-p']['state']['profile']['dayReviewThrough']=='2026-09-27' and profiles['test-d']['state']['days']['2026-09-27']['complete'])
  p.reload();p.wait_for_function('window.NK_APP');check('No is not asked again after reload',no(p,'day-review-dialog'));c.close()
  reset_person('test-d');c=context(b);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));login(p);p.locator('#day-review-dialog[open]').wait_for();p.locator('[data-day-review="later"]').last.click();nav(p,'profile');check('Later does not nag again in the same session',no(p,'day-review-dialog'))
  check('Later does not modify completion or response marker','dayReviewThrough' not in profiles['test-d']['state']['profile'] and not profiles['test-d']['state']['days']['2026-09-27']['complete'])
  p.reload();p.locator('#day-review-dialog[open]').wait_for();check('Deferred reminder returns next load');c.close()
  for name,has_entries,complete in [('Empty yesterday',False,False),('Already complete yesterday',True,True)]:
   reset_person('test-d',has_entries,complete);c=context(b);p=c.new_page();login(p);check(name+' is not asked',no(p,'day-review-dialog'));c.close()
  reset_person('test-d');c=context(b);p=c.new_page();login(p);p.locator('#day-review-dialog[open]').wait_for()
  server_down=True;p.evaluate("()=>{window.__write=NK_SAFE_CACHE.write;NK_SAFE_CACHE.write=async()=>{throw new DOMException('Synthetic local failure','QuotaExceededError');};}")
  p.locator('[data-day-review="yes"]').click();p.wait_for_function('document.querySelector("#day-review-error").textContent.includes("Noch nicht dauerhaft gespeichert")');p.wait_for_timeout(250)
  check('Buffered storage error stays visible instead of false success',p.locator('#day-review-dialog').is_visible() and not profiles['test-d']['state']['days']['2026-09-27']['complete'])
  server_down=False;p.evaluate('()=>{NK_SAFE_CACHE.write=window.__write;}');p.locator('[data-day-review="yes"]').click();p.wait_for_function('!document.querySelector("#day-review-dialog").open');flush(p);check('Retry safely persists the explicit yes',profiles['test-d']['state']['days']['2026-09-27']['complete']);c.close()
  reset_person('test-d');c=context(b);p=c.new_page();login(p);p.locator('#day-review-dialog[open]').wait_for()
  p.evaluate("()=>{const s=NK_APP.getState();s.entries.find(e=>e.date==='2026-09-27').name='Changed remotely';NK_APP.acceptSyncState(s);document.dispatchEvent(new Event('nk-synced'));}")
  p.wait_for_function('document.querySelector("#day-review-error").textContent.includes("zwischenzeitlich")');check('Changed entries require a fresh review',not profiles['test-d']['state']['days']['2026-09-27']['complete']);c.close()
  reset_person('test-d');c=context(b);p=c.new_page();login(p);p.locator('#day-review-dialog[open]').wait_for()
  p.evaluate('()=>{window.__dayOffset=86400000;NK_DAY_REVIEW.refresh();}');p.wait_for_function('document.querySelector("#day-review-description").textContent.includes("28. September")');check('Midnight refresh asks the new previous calendar day',not p.evaluate('NK_APP.getState().days["2026-09-27"].complete'))
  p.locator('[data-day-review="yes"]').click();p.wait_for_function('!document.querySelector("#day-review-dialog").open');flush(p);check('After midnight only the displayed new yesterday is completed',profiles['test-d']['state']['days']['2026-09-28']['complete'] and not profiles['test-d']['state']['days']['2026-09-27']['complete']);c.close()
  reset_person('test-d',False);c=context(b);p=c.new_page();login(p);nav(p,'search');p.locator('[data-nk-scan]:visible').first.click()
  p.evaluate('s=>{NK_APP.acceptSyncState(s);NK_DAY_REVIEW.refresh();}',copy.deepcopy(initial)|{'profile':{**initial['profile'],'releaseNotesSeen':'1.12.0'}})
  check('Prompt never covers an open scanner',no(p,'day-review-dialog'));p.locator('#scan-close').click();p.locator('#day-review-dialog[open]').wait_for();check('Prompt follows scanner close');c.close()
  reset_person('test-d',False);c=context(b);p=c.new_page();login(p);nav(p,'profile');p.locator('#age').fill('41')
  p.evaluate('s=>{NK_APP.acceptSyncState(s);NK_DAY_REVIEW.refresh();}',copy.deepcopy(initial)|{'profile':{**initial['profile'],'releaseNotesSeen':'1.12.0'}})
  check('Unsaved profile inputs are not interrupted',no(p,'day-review-dialog'));p.locator('#profile-form button[type=submit]').click();p.locator('#day-review-dialog[open]').wait_for();check('Prompt follows profile save');c.close()
  reset_person('test-d',False);profiles['test-d']['state']['profile']['releaseNotesSeen']='1.11.0'
  c=context(b);p=c.new_page();login(p);p.locator('#release-notes-dialog[open]').wait_for();p.locator('[data-release-action="close"]').first.click();p.reload();p.wait_for_function('window.NK_APP');check('Immediate dismissal survives a page reload',no(p,'release-notes-dialog'))
  check('Cups, estimated household measures and recipe paste remain loaded',p.evaluate('!!NK_CUPS && !!NK_MEASURES && !!NK_RECIPE_IMPORT'))
  check('Reports and PDF remain loaded',p.evaluate('!!NK_REPORTS && !!NK_REPORT_PDF'))
  check('No unexpected external requests',not unexpected);check('No JavaScript runtime errors',not errors)
 except Exception:
  import traceback
  (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc()+str(errors));p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-6000:]);raise
 finally:
  (OUT/f'{engine}-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'unexpected':unexpected},indent=2));b.close();server.shutdown()
