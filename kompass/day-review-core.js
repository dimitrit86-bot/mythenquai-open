/* Pure calendar/eligibility rules. A complete day is always the user's decision. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NK_DAY_REVIEW_CORE=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 function validDate(s){if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;const d=new Date(s+'T12:00:00Z');return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s;}
 function previousDay(today){if(!validDate(today))throw Error('Ungültiger Kalendertag.');const d=new Date(today+'T12:00:00Z');d.setUTCDate(d.getUTCDate()-1);return d.toISOString().slice(0,10);}
 function highest(...dates){return dates.filter(validDate).sort().at(-1)||null;}
 function candidate(state,today){const date=previousDay(today);if(state?.days?.[date]?.complete===true)return null;if(validDate(state?.profile?.dayReviewThrough)&&state.profile.dayReviewThrough>=date)return null;const entries=(state?.entries||[]).filter(e=>e.date===date);return entries.length?{date,count:entries.length}:null;}
 function signature(state,day,stable){return stable((state.entries||[]).filter(e=>e.date===day).slice().sort((a,b)=>a.id.localeCompare(b.id)));}
 return {validDate,previousDay,highest,candidate,signature};
});
