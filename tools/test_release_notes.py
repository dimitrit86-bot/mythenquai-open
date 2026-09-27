"""Real browser interaction and encrypted storage, synthetic HTTP API only."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import os,json,copy,subprocess
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
OUT=ROOT/'test-output-notes';OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/kompass/'
initial=json.loads(subprocess.check_output(['node','-e',"console.log(JSON.stringify(require('./kompass/core.js').initial()))"]))
profiles={i:{'id':i,'name':name,'revision':0,'state':copy.deepcopy(initial)} for i,name in [('test-d','Dimitri'),('test-p','Patricia')]}
requests=[];unexpected=[];errors=[];checks=[]
def check(name,ok=True):
    assert ok,name
    checks.append(name);print('PASS',name,flush=True)
def api(route):
    req=route.request;d=req.post_data_json or {};requests.append((req.url,d));a=d.get('action')
    if a=='login':r={'token':'f'*64,'expires':'2099-01-01T00:00:00Z'}
    elif a=='key':r={'key':'ab'*32}
    elif a=='profiles':r={'profiles':[{k:p[k] for k in ['id','name','revision']} for p in profiles.values()]}
    elif a=='get':r={'profile':copy.deepcopy(profiles[d['id']])}
    elif a=='save':
        p=profiles[d['id']]
        if p['revision']!=d['revision']:return route.fulfill(status=409,json={'error':'Synthetic conflict','conflict':True})
        p['state']=d['state'];p['revision']+=1;r={'revision':p['revision']}
    elif a=='catalog':r={'profiles':[{**{k:p[k] for k in ['id','name','revision']},'foods':p['state']['foods'],'recipes':p['state']['recipes']} for p in profiles.values()]}
    elif a=='logout':r={'ok':True}
    else:raise AssertionError('Unexpected API request '+str(d))
    route.fulfill(status=200,json=r)
def context(browser,sw=False):
    c=browser.new_context(viewport={'width':390,'height':844},service_workers='allow' if sw else 'block',accept_downloads=True)
    def route(r):
        if '/functions/v1/' in r.request.url:return api(r)
        if r.request.url.startswith(URL) or r.request.url.startswith('blob:'+URL.split('/kompass/')[0]+'/'):return r.continue_()
        unexpected.append(r.request.url);return r.abort()
    c.route('**/*',route);return c

def login(p,id='test-d'):
    p.goto(URL);p.locator('#gate-password').fill('synthetic-password');p.locator('#gate-form button[type=submit]').click();choose(p,id)
def choose(p,id):
    p.locator(f'[data-nk="choose"][data-id="{id}"]').click();p.wait_for_function('id=>window.NK_APP && NK_HOUSEHOLD.id===id && !document.querySelector("#app").hidden',arg=id)
def switch(p,id):p.locator('#device-profile-button').click();choose(p,id)
def nav(p,r):p.locator(f'[data-action="nav"][data-route="{r}"]:visible').first.click()
def show(p):p.locator('#release-notes-dialog[open]').wait_for()
def ack(p):p.locator('#release-notes-dialog [data-release-action="ack"]').click();p.wait_for_function('!document.querySelector("#release-notes-dialog").open');p.evaluate('NK_HOUSEHOLD.flush()')
def no_dialog(p):p.wait_for_timeout(250);return p.locator('#release-notes-dialog[open]').count()==0
engine=os.environ.get('TEST_BROWSER','chromium')
with sync_playwright() as play:
    launch={'headless':True}
    if os.environ.get('LOCAL_CHROME'):launch['executable_path']='/usr/bin/chromium'
    b=getattr(play,engine).launch(**launch);c=context(b);p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
    try:
        p.goto(URL);p.locator('#gate-password').wait_for();check('No changelog popup before authentication',no_dialog(p) and p.locator('#release-notes-button').is_hidden())
        login(p);show(p)
        check('First open starts at 1.9 and includes current patch',p.locator('#release-notes-dialog [data-release-version]').count()==2 and p.locator('[data-release-version="1.9.0"]').count()==1)
        check('Correct personal profile name',p.locator('.release-for').inner_text()=='Für Dimitri')
        check('Dialog has a meaningful focus target',p.evaluate('document.activeElement.id')=='release-dialog-title')
        check('Viewing alone does not write or acknowledge',profiles['test-d']['revision']==0 and 'releaseNotesSeen' not in p.evaluate('NK_APP.getState().profile'))
        for w in [320,390,1440]:
            p.set_viewport_size({'width':w,'height':900});p.wait_for_timeout(100)
            check(f'Release dialog fits {w}px',p.evaluate('document.documentElement.scrollWidth<=innerWidth && document.querySelector("#release-notes-dialog").scrollWidth<=document.querySelector("#release-notes-dialog").clientWidth'))
        p.set_viewport_size({'width':390,'height':844});p.screenshot(path=str(OUT/f'{engine}-whats-new.png'))
        p.locator('#release-notes-dialog [data-release-action="archive"]').click();check('Archive reachable from automatic dialog','Release-Archiv' in p.locator('#release-dialog-title').inner_text())
        p.locator('#release-notes-dialog [data-release-action="later"]').first.click();nav(p,'profile');check('Defer does not reopen on ordinary navigation',no_dialog(p))
        check('Profile contains archive entry',p.locator('#release-profile-card').is_visible())
        p.reload();show(p);check('Deferred release returns on next app load',True)
        p.keyboard.press('Escape');check('Escape closes without acknowledging',no_dialog(p) and 'releaseNotesSeen' not in p.evaluate('NK_APP.getState().profile'))
        p.locator('#release-notes-button').click();show(p)
        before=p.evaluate('NK_APP.getState()');ack(p);after=p.evaluate('NK_APP.getState()');after['profile'].pop('releaseNotesSeen')
        check('Acknowledgement changes only display metadata',before==after and profiles['test-d']['state']['profile']['releaseNotesSeen']=='1.9.1')
        check('Another profile is not acknowledged', 'releaseNotesSeen' not in profiles['test-p']['state']['profile'])
        p.reload();p.wait_for_function('window.NK_APP');check('Confirmed version not repeated after reload',no_dialog(p))
        c2=context(b);p2=c2.new_page();login(p2);check('Confirmed stand follows profile to another device',no_dialog(p2));c2.close()
        switch(p,'test-p');show(p);check('Other profile gets its own first-open notices',p.locator('.release-for').inner_text()=='Für Patricia')
        p.evaluate("() => {window.__savedSet=NK_STORE.setItem;NK_STORE.setItem=async()=>{throw Error('Synthetic storage failure');};}")
        p.locator('#release-notes-dialog [data-release-action="ack"]').click();p.wait_for_function('document.querySelector("#release-ack-status").textContent.includes("Synthetic storage failure")')
        check('Storage failure leaves notice and unread marker intact',p.locator('#release-notes-dialog[open]').count()==1 and 'releaseNotesSeen' not in p.evaluate('NK_APP.getState().profile'))
        p.evaluate('()=>{NK_STORE.setItem=window.__savedSet;}');ack(p)
        check('Retry safely persists the right profile','releaseNotesSeen' in profiles['test-p']['state']['profile'])
        nav(p,'profile');p.locator('#age').fill('39');p.locator('#profile-form button[type=submit]').click();p.evaluate('NK_HOUSEHOLD.flush()')
        check('Saving personal settings keeps read stand',p.evaluate('NK_APP.getState().profile.releaseNotesSeen')=='1.9.1')
        p.locator('#release-notes-button').click();show(p)
        check('Archive stays accessible without new releases',p.locator('#release-notes-dialog [data-release-version]').count()==2 and p.locator('#release-notes-dialog [data-release-action="ack"]').count()==0)
        with p.expect_download() as d:p.locator('#release-notes-dialog .release-text-link').first.click()
        d.value.save_as(str(OUT/'release-note.md'));check('Individual note downloads as real Markdown','Nährstoff-Kompass' in (OUT/'release-note.md').read_text())
        p.locator('#release-notes-dialog [data-release-action="later"]').first.click()
        p.reload();p.wait_for_function('window.NK_APP');nav(p,'search');p.locator('[data-nk-scan]:visible').first.click()
        p.evaluate("()=>{for(const version of ['1.10.0','1.10.2']) NK_RELEASE_DATA.releases.push({...NK_RELEASE_DATA.releases[0],version,title:'Future test '+version});NK_DEVICE.version='1.10.2';NK_RELEASES.refresh();}")
        check('New-release auto dialog waits behind scanner',no_dialog(p));p.locator('#scan-close').click();show(p)
        check('Multiple skipped future releases shown together and sorted',p.locator('#release-notes-dialog [data-release-version]').evaluate_all('(xs)=>xs.map(x=>x.dataset.releaseVersion)')==['1.10.2','1.10.0'])
        ack(p);check('Future profile marker retained',profiles['test-p']['state']['profile']['releaseNotesSeen']=='1.10.2')
        p.reload();p.wait_for_function('window.NK_APP');check('Rollback does not reset higher acknowledged stand',no_dialog(p))
        nav(p,'profile');p.locator('#age').fill('40')
        p.evaluate("()=>{NK_RELEASE_DATA.releases.push({...NK_RELEASE_DATA.releases[0],version:'2.0.0',title:'Future test 2.0'});NK_DEVICE.version='2.0.0';NK_RELEASES.refresh();}")
        check('New-release notification waits for unsaved profile',no_dialog(p));p.locator('#profile-form button[type=submit]').click();show(p);check('Pending notification opens after profile save',p.locator('[data-release-version="2.0.0"]').count()==1)
        p.locator('#release-notes-dialog [data-release-action="later"]').first.click();p.evaluate('NK_HOUSEHOLD.flush()')
        c3=context(b);p3=c3.new_page();login(p3,'test-d');nav(p3,'profile');p3.locator('#age').fill('43')
        profiles['test-d']['state']['profile']['releaseNotesSeen']='1.10.0';profiles['test-d']['revision']+=1
        p3.locator('#profile-form button[type=submit]').click();p3.evaluate('NK_HOUSEHOLD.flush()')
        check('Stale device save retains newer server read marker',profiles['test-d']['state']['profile']['releaseNotesSeen']=='1.10.0' and profiles['test-d']['state']['profile']['age']==43 and not p3.evaluate('NK_HOUSEHOLD.blocked'));c3.close()
        archive=c.new_page();archive.goto(URL+'release-notes/');archive.locator('h1').wait_for()
        check('Public release folder readable without profile code',archive.locator('.release-card').count()==2 and not archive.evaluate('!!window.NK_APP'))
        for w in [320,1440]:
            archive.set_viewport_size({'width':w,'height':900});archive.wait_for_timeout(100);check(f'Standalone archive fits {w}px',archive.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        archive.screenshot(path=str(OUT/f'{engine}-archive.png'),full_page=True);archive.close()
        check('No product, meal or body-data collection added by notes',all(not any(k in d for k in ['photo','image','releaseLog']) for _,d in requests))
        swc=context(b,sw=True);sp=swc.new_page();sp.goto(URL);sp.wait_for_function('navigator.serviceWorker.controller!==null',timeout=25000)
        sp.goto(URL+'release-notes/');sp.locator('h1').wait_for();swc.set_offline(True);sp.reload();sp.locator('h1').wait_for()
        check('Actual service worker serves release folder offline','Schritt für Schritt' in sp.locator('h1').inner_text())
        sp.goto(URL);sp.locator('#gate-password').wait_for();check('Archive navigation never poisons cached main app',sp.locator('#gate-password').is_visible());swc.close()
        check('No unexpected external requests',not unexpected);check('No JavaScript runtime errors',not errors)
    except Exception:
        import traceback
        (OUT/f'{engine}-failure.txt').write_text(traceback.format_exc()+str(errors));p.screenshot(path=str(OUT/f'{engine}-failure.png'),full_page=True);print(p.locator('body').inner_text()[-6000:]);raise
    finally:
        (OUT/f'{engine}-report.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'unexpected':unexpected},indent=2));b.close();server.shutdown()
