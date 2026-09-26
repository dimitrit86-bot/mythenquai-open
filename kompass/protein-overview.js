/* Protein overview: read-only display using the existing profile reference engine. */
(function () {
  'use strict';
  const C = window.NK, root = document.getElementById('app');
  if (!C || !root || window.NK_PROTEIN_OVERVIEW) return;
  const fmt = value => new Intl.NumberFormat('de-CH', {maximumFractionDigits: 1}).format(value);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));

  // No new target calculation: manual goals and safety exclusions stay in core.js.
  function model(profile, intake) {
    const reference = C.targets(profile).values.protein;
    const target = Number.isFinite(reference?.value) && reference.value > 0 ? reference.value : null;
    const recorded = (intake?.total || 0) > 0;
    const known = recorded && intake.known > 0 && Number.isFinite(intake.value);
    const partial = recorded && intake.known < intake.total;
    const amount = known ? intake.value : null;
    return {
      target, amount, recorded, partial,
      own: reference?.type === 'Eigenes Ziel',
      note: reference?.note || '',
      remaining: target !== null && amount !== null && !partial ? Math.max(0, target - amount) : null,
      percent: target !== null && amount !== null && !partial ? 100 * amount / target : null
    };
  }

  function enhance() {
    if (root.hidden || !window.NK_APP) return;
    const card = [...root.querySelectorAll('#main .summary-grid > .metric')].find(element =>
      element.querySelector('.metric-label > span')?.textContent.trim() === 'Protein'
    );
    const date = root.querySelector('#diary-date')?.value;
    if (!card || !date || !C.validDate(date)) return;
    const state = window.NK_APP.getState();
    const intake = C.aggregate(C.dayEntries(state, date).map(entry => entry.n), ['protein']).protein;
    const m = model(state.profile, intake);
    const signature = JSON.stringify([date, m]);
    // The host rerenders its cards on diary, profile and day changes. Avoid observer loops.
    if (card.dataset.proteinOverview === signature) return;
    card.dataset.proteinOverview = signature;
    card.classList.add('protein-overview');
    card.setAttribute('aria-label', 'Protein: erfasste Menge und Tagesbedarf');
    card.querySelector('.protein-target')?.remove();
    card.querySelector('.protein-target-kind')?.remove();
    card.querySelector('.protein-target-help')?.remove();
    card.querySelector('.track')?.remove();
    const number = card.querySelector('.metric-number');
    number.setAttribute('aria-label', m.amount === null ? 'Protein noch nicht erfasst oder unbekannt' : 'Erfasst: ' + fmt(m.amount) + ' Gramm Protein' + (m.partial ? ', bekannte Teilmenge' : ''));
    const target = document.createElement('div');
    target.className = 'protein-target';
    target.innerHTML = '<span>Tagesbedarf</span><strong>' + (m.target === null ? 'Noch nicht festgelegt' : esc(fmt(m.target)) + ' <small>g / Tag</small>') + '</strong>';
    number.after(target);
    const bottom = card.querySelector('.metric-bottom');
    if (!m.recorded) bottom.textContent = 'Noch nichts erfasst.';
    else if (m.partial) bottom.textContent = 'Bekannte Teilmenge – Proteinangaben fehlen.';
    else if (m.amount === null) bottom.textContent = 'Erfasste Proteinmenge unbekannt.';
    else if (m.remaining === null) bottom.textContent = 'Erfasste Zufuhr: ' + fmt(m.amount) + ' g.';
    else bottom.textContent = m.remaining > 0 ? 'Noch ' + fmt(m.remaining) + ' g bis zum Tagesziel.' : 'Tagesziel laut erfassten Mengen erreicht.';
    if (m.percent !== null) {
      const track = document.createElement('div');
      track.className = 'track';
      track.setAttribute('role', 'progressbar');
      track.setAttribute('aria-label', 'Erfasste Proteinmenge im Verhältnis zum Tagesbedarf');
      track.setAttribute('aria-valuemin', '0');
      track.setAttribute('aria-valuemax', '100');
      track.setAttribute('aria-valuenow', String(Math.min(100, Math.max(0, m.percent))));
      track.setAttribute('aria-valuetext', fmt(m.amount) + ' von ' + fmt(m.target) + ' Gramm erfasst');
      const bar = document.createElement('span');
      bar.style.width = Math.min(100, Math.max(0, m.percent)) + '%';
      track.append(bar);
      bottom.after(track);
    }
    const info = document.createElement('div');
    info.className = 'protein-target-kind';
    info.textContent = m.target === null ? 'Profil ergänzen oder eigenes Proteinziel speichern.' : m.own ? 'Dein eigenes Tagesziel' : 'Basisreferenz für dein Profil';
    if (m.note) info.title = m.note;
    card.append(info);
    if (m.target === null) {
      const help = document.createElement('button');
      help.type = 'button';
      help.className = 'muted-link protein-target-help';
      help.dataset.action = 'nav';
      help.dataset.route = 'profile';
      help.textContent = 'Bedarf / Ziel festlegen';
      card.append(help);
    }
  }

  let queued = false;
  const schedule = () => {
    if (queued) return;
    queued = true;
    queueMicrotask(() => { queued = false; enhance(); });
  };
  new MutationObserver(schedule).observe(root, {childList: true, subtree: true, attributes: true, attributeFilter: ['hidden']});
  document.addEventListener('nk-profile-loaded', schedule);
  window.NK_PROTEIN_OVERVIEW = {version: '1.2.1', model, refresh: schedule};
  schedule();
})();
