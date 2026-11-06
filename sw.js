// Offline cache: the app shell is cached on install; each unit is cached the first time it is opened.
const CACHE = 'word-review-v4';
const SHELL = ['./', 'index.html', 'manifest.json', 'icon-192.png', 'icon-512.png', 'data/movers/index.json', 'data/movers/thumbs.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  const isUnit = /\/data\/.+\/u\d\d\.json$/.test(url.pathname);
  if (isUnit) {   // units: cache first (big, rarely change)
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      const copy = r.clone(); if (r.ok) caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })));
  } else {        // shell: network first, fall back to cache when offline
    e.respondWith(fetch(e.request).then(r => {
      const copy = r.clone(); if (r.ok) caches.open(CACHE).then(c => c.put(e.request, copy)); return r;
    }).catch(() => caches.match(e.request)));
  }
});
