/* App-scoped static cache. Never caches private API responses or modifies another app. */
const CACHE='nk-kompass-1.0.0';
const SHELL=['./','./index.html','./style.css','./core.js','./app.js','./data.js','./household.js','./scanner.js','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon.svg'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('nk-kompass-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('message',e=>{if(e.data==='ACTIVATE_UPDATE')self.skipWaiting();});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==self.location.origin||!u.href.startsWith(self.registration.scope))return;if(!(/\.(js|css|png|svg|webmanifest|html|wasm|gz)$/.test(u.pathname)||e.request.mode==='navigate'))return;e.respondWith(caches.open(CACHE).then(async c=>{const cached=await c.match(e.request);if(cached)return cached;try{const r=await fetch(e.request);if(r.ok)c.put(e.request,r.clone());return r;}catch{return e.request.mode==='navigate'?await c.match('./index.html')||Response.error():Response.error();}}));});
