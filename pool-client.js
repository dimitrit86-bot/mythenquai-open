(()=>{
const API='https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/betting-api';
const REST='https://wpmyuzpcraduhaybjvmb.supabase.co/rest/v1/rpc/';
const PUB='sb_publishable_yPj36dTiaHySwtJgKCA-wQ_lJuoE0OQ';
const $=id=>document.getElementById(id);
const CHF=n=>'CHF '+Number(n||0).toFixed(2);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let state=null;
let adminPin=sessionStorage.getItem('mq_admin_pin')||'';
let code=sessionStorage.getItem('mq_code')||'';

async function api(body){
  const r=await fetch(API,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
  const d=await r.json();
  if(!r.ok) throw new Error(d.error||'Fehler');
  return d;
}

async function rpc(name,body){
  const r=await fetch(REST+name,{method:'POST',headers:{'content-type':'application/json','apikey':PUB,'authorization':'Bearer '+PUB},body:JSON.stringify(body)});
  const d=await r.json();
  if(!r.ok)throw new Error(d.message||d.error||'RPC Fehler');
  return d;
}

async function refresh(){
  try{state=await api({action:'state'});render();}
  catch(e){if($('entryCount'))$('entryCount').textContent='Backend nicht erreichbar: '+e.message;}
}

function render(){
  if(!state)return;
  const ph=state.phase;
  $('entryCard').classList.toggle('hidden',ph!=='entry');
  $('accessCard').classList.toggle('hidden',ph==='entry');
  $('finalCard').classList.toggle('hidden',!['final','settled'].includes(ph));
  $('settleCard').classList.toggle('hidden',ph!=='settled');
  $('adminCard').classList.toggle('hidden',!adminPin);
  $('adminLogin').textContent=adminPin?'ADMIN AUS':'ADMIN';
  $('entryCount').textContent=ph==='entry'?state.entry_count+' Einsatz/Einsätze vorgemerkt.':'';
  ['p1','p2','p3','p4'].forEach(id=>$(id).classList.remove('active'));
  $(ph==='entry'?'p1':ph==='confirm'?'p2':ph==='final'?'p3':'p4').classList.add('active');

  if(state.final){
    $('finalD').textContent=CHF(state.final.d);
    $('finalF').textContent=CHF(state.final.f);
    $('finalQD').textContent=state.final.dGross?Number(state.final.dGross).toFixed(2)+'×':'–';
    $('finalQF').textContent=state.final.fGross?Number(state.final.fGross).toFixed(2)+'×':'–';
  }
  if(adminPin)loadAdmin();
  if(code&&ph!=='entry')loadPersonal(false);
}

async function submitBet(){
  const name=$('name').value.trim();
  const side=$('side').value;
  const amount=+$('amount').value;
  try{
    const created=await api({action:'submit',name,email:'noemail@mythenquai.local',side,amount});
    const accessCode=await rpc('mq_get_entry_code',{p_bet_id:created.id});
    $('entryForm').classList.add('hidden');
    $('entryMsg').innerHTML='<div class="person"><span class="ok"><b>Einsatz vorgemerkt ✓</b></span><br>'+esc(name)+' · '+(side==='D'?'Dimitri':'Florian')+' · '+CHF(amount)+'<hr><span class="note">Dein persönlicher 4-stelliger Code:</span><br><span class="codebox">'+esc(accessCode)+'</span><div class="row" style="margin-top:10px"><a class="btn primary" href="https://wpmyuzpcraduhaybjvmb.supabase.co/functions/v1/download-code?code='+encodeURIComponent(accessCode)+'&name='+encodeURIComponent(name)+'&side='+encodeURIComponent(side==='D'?'Dimitri':'Florian')+'&amount='+encodeURIComponent(amount)+'">CODE HERUNTERLADEN</a></div><span class="note">Mit diesem Code kannst du später deine Quote öffnen und bestätigen. Falls du ihn verlierst, kann der Admin ihn im Admin-Center nachsehen.</span><div class="row" style="margin-top:10px"><button class="btn" id="again">WEITEREN EINSATZ ERFASSEN</button></div></div>';
    $('again').onclick=()=>{$('entryMsg').innerHTML='';$('entryForm').classList.remove('hidden');};
    await refresh();
  }catch(e){$('entryMsg').innerHTML='<p class="out">'+esc(e.message)+'</p>';}
}

async function adminLogin(){
  if(adminPin){adminPin='';sessionStorage.removeItem('mq_admin_pin');render();return;}
  const p=prompt('Admin-PIN');
  if(!p)return;
  try{
    await rpc('mq_admin_bet_log',{p_pin:p});
    adminPin=p;sessionStorage.setItem('mq_admin_pin',p);render();
  }catch(e){alert('Falscher PIN oder Backendfehler.');}
}

async function loadAdmin(){
  if(!adminPin)return;
  try{
    const d=await rpc('mq_admin_bet_log',{p_pin:adminPin});
    $('adminInfo').textContent='Phase: '+d.pool.status+' · Runde '+d.pool.round_no+' · '+d.bets.length+' Einsätze';
    $('adminCodes').innerHTML=d.bets.map(b=>'<div class="person"><b>'+esc(b.name)+'</b> · '+(b.side==='D'?'Dimitri':'Florian')+' · '+CHF(b.amount)+'<br><span class="codebox">'+esc(b.access_code||'–')+'</span><br><span class="note">'+esc(b.status)+'</span></div>').join('');
  }catch(e){$('adminInfo').textContent=e.message;}
}

async function adminAction(action,extra={}){
  try{
    const d=await api({action,admin_pin:adminPin,...extra});
    if(action==='admin_settle')showSettlement(d);
    await refresh();
    alert('Erledigt.');
  }catch(e){alert(e.message);}
}

async function openPersonal(showError=true){
  if(showError){
    code=$('accessCode').value.trim().toUpperCase();
    sessionStorage.setItem('mq_code',code);
  }
  if(!code)return;
  try{
    const b=await api({action:'access',code});
    $('personalCard').classList.remove('hidden');
    $('accessMsg').textContent='';
    $('personalBody').innerHTML='<div class="person"><b>'+esc(b.name)+'</b><hr><b>'+(b.side==='D'?'Dimitri':'Florian')+'</b> · '+CHF(b.amount)+'<br>Quote: <b>'+Number(b.quote).toFixed(2)+'×</b><br>Möglicher Nettogewinn: <b>'+CHF(b.net_gain)+'</b><br>Maximaler Verlust: <b>'+CHF(b.amount)+'</b><br><br><span class="'+(b.status==='confirmed'?'ok':'wait')+'"><b>'+(b.status==='confirmed'?'VERBINDLICH BESTÄTIGT':'NOCH NICHT BESTÄTIGT')+'</b></span>'+(b.phase==='confirm'&&b.status!=='confirmed'?'<div class="row" style="margin-top:10px"><button class="btn primary" id="confirmMine">BESTÄTIGEN</button><button class="btn warn" id="leaveMine">AUSSTEIGEN</button></div>':'')+'</div>';
    if($('confirmMine'))$('confirmMine').onclick=()=>participant('confirm');
    if($('leaveMine'))$('leaveMine').onclick=()=>participant('leave');
  }catch(e){
    $('personalCard').classList.add('hidden');
    if(showError)$('accessMsg').textContent=e.message;
  }
}

async function participant(action){
  try{
    await api({action,code});
    if(action==='leave'){code='';sessionStorage.removeItem('mq_code');$('personalCard').classList.add('hidden');}
    else await openPersonal(false);
    await refresh();
  }catch(e){alert(e.message);}
}

function showSettlement(d){
  $('settleCard').classList.remove('hidden');
  $('settlement').innerHTML='<b>'+(d.winner==='D'?'Dimitri':'Florian')+' gewinnt.</b><br><span class="note">Verlierer-Pool: '+CHF(d.loser_pool)+'</span>';
  $('transfers').innerHTML=(d.transfers||[]).map(t=>'<div class="transfer"><span><b>'+esc(t.from)+'</b> → '+esc(t.to)+'</span><b>'+CHF(t.amount)+'</b></div>').join('');
}

$('submitBet').onclick=submitBet;
$('adminLogin').onclick=adminLogin;
$('openBet').onclick=()=>openPersonal(true);
$('adminCloseEntry').onclick=()=>adminAction('admin_close');
$('adminRecalc').onclick=()=>adminAction('admin_recalc');
$('adminFinalize').onclick=()=>adminAction('admin_finalize');
$('adminWinD').onclick=()=>adminAction('admin_settle',{winner:'D'});
$('adminWinF').onclick=()=>adminAction('admin_settle',{winner:'F'});
$('adminReset').onclick=async()=>{
  if(!adminPin)return;
  if(!confirm('Wirklich alle Einsätze, Codes und den aktuellen Pool zurücksetzen?'))return;
  try{
    await rpc('mq_admin_reset',{p_pin:adminPin});
    code='';sessionStorage.removeItem('mq_code');
    if($('personalCard'))$('personalCard').classList.add('hidden');
    if($('entryMsg'))$('entryMsg').innerHTML='';
    if($('entryForm'))$('entryForm').classList.remove('hidden');
    await refresh();
    alert('Alles wurde zurückgesetzt.');
  }catch(e){alert(e.message);}
};

refresh();
setInterval(refresh,15000);
})();