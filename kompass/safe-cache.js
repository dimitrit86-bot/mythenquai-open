/* Encrypted payload storage. IndexedDB first, previous localStorage remains a fallback. */
(function(){'use strict';let dbPromise;
function db(){if(!dbPromise)dbPromise=new Promise((resolve,reject)=>{let r;try{r=indexedDB.open('nk-private-recovery',1);}catch(e){reject(e);return;}r.onupgradeneeded=()=>r.result.createObjectStore('records');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.onblocked=()=>reject(Error('Lokaler Speicher ist in einem anderen Fenster blockiert.'));});return dbPromise;}
async function idb(op,key,value){const d=await db();return new Promise((resolve,reject)=>{const tx=d.transaction('records',op==='get'?'readonly':'readwrite'),store=tx.objectStore('records');const req=op==='get'?store.get(key):op==='put'?store.put(value,key):store.delete(key);let result;req.onsuccess=()=>result=req.result;tx.oncomplete=()=>resolve(result);tx.onerror=()=>reject(tx.error||req.error);tx.onabort=()=>reject(tx.error||Error('Lokales Speichern abgebrochen.'));});}
async function write(key,value){let cause;try{await idb('put',key,value);return 'indexeddb';}catch(e){cause=e;}try{localStorage.setItem(key,value);return 'localStorage';}catch(e){const error=Error('Die lokale Sicherung ist nicht verfügbar. Es wird versucht, direkt mit dem Server zu speichern.');error.code='LOCAL_CACHE_UNAVAILABLE';error.cause=e||cause;throw error;}}
async function read(key){let a=null,b=null;try{a=await idb('get',key);}catch{}try{b=localStorage.getItem(key);}catch{}if(!a)return b;if(!b)return a;try{return (JSON.parse(b).savedAt||0)>(JSON.parse(a).savedAt||0)?b:a;}catch{return a;}}
async function remove(key){await idb('delete',key).catch(()=>{});try{localStorage.removeItem(key);}catch{}}
window.NK_SAFE_CACHE={write,read,remove};
})();
