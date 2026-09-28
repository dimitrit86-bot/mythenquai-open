"""Accurate test clocks instead of injecting state outside the storage adapter."""
from pathlib import Path
p=Path('tools/test_daily_review.py');s=p.read_text()
s=s.replace('def context(b,sw=False):','def context(b,sw=False,offset=0):')
s=s.replace('c.add_init_script(CLOCK)','c.add_init_script(CLOCK.replace("window.__dayOffset=0", "window.__dayOffset="+str(offset)))')
s=s.replace("reset_person('test-d',False);c=context(b);p=c.new_page();login(p);nav(p,'search');", "reset_person('test-d');c=context(b,offset=-172800000);p=c.new_page();login(p);nav(p,'search');")
s=s.replace("reset_person('test-d',False);c=context(b);p=c.new_page();login(p);nav(p,'profile');", "reset_person('test-d');c=context(b,offset=-172800000);p=c.new_page();login(p);nav(p,'profile');")
a="p.evaluate('s=>{NK_APP.acceptSyncState(s);NK_DAY_REVIEW.refresh();}',copy.deepcopy(initial)|{'profile':{**initial['profile'],'releaseNotesSeen':'1.12.0'}})"
s=s.replace(a,"p.evaluate('()=>{window.__dayOffset=0;NK_DAY_REVIEW.refresh();}')")
a="  p.wait_for_function('NK_APP.getState().profile.releaseNotesSeen===\"1.12.0\"');flush(p)"
s=s.replace(a,a+"\n  p.screenshot(path=str(OUT/f'{engine}-release-once.png'))")
a="  check('Cups, estimated household measures and recipe paste remain loaded',"
insert="""  c.close();reset_person('test-d');c=context(b);p=c.new_page();login(p);p.locator('#day-review-dialog[open]').wait_for()
  server_down=True;p.locator('[data-day-review="yes"]').click();p.wait_for_function('!document.querySelector("#day-review-dialog").open');p.wait_for_timeout(500)
  check('With server unavailable the explicit yes stays encrypted locally',p.evaluate('NK_APP.getState().days["2026-09-27"].complete && NK_HOUSEHOLD.pending') and not profiles['test-d']['state']['days']['2026-09-27']['complete'])
  p.reload();p.wait_for_function('window.NK_APP');check('Locally secured completion survives reload without repeated prompt',no(p,'day-review-dialog') and p.evaluate('NK_APP.getState().days["2026-09-27"].complete'))
  server_down=False;flush(p);check('Pending confirmation synchronizes when server returns',profiles['test-d']['state']['days']['2026-09-27']['complete'])
"""
if insert not in s:s=s.replace(a,insert+a)
p.write_text(s)
p=Path('kompass/day-review.css');s=p.read_text();extra='\n#day-review-error:empty{display:none}\n'
if extra not in s:p.write_text(s+extra)
print('Fixture uses real stored diaries while advancing the test calendar; empty error banner hidden.')
