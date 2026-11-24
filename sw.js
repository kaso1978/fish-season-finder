/* Fish Season Finder service worker.
 *
 * Goal: testers always get the newest version when they have a connection,
 * and the last good copy when they don't. So app files are NETWORK-FIRST
 * (the HTTP cache is bypassed too), never cache-first. Nobody gets stuck on
 * an old build, and nobody needs a new link.
 *
 * Bump VERSION together with APP_VERSION in index.html on each release.
 */
const VERSION = '2026-11-24.5';
const CACHE = 'fsf-' + VERSION;
const SHELL = [
  './', './index.html', './manifest.webmanifest',
  './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'
];
const CDN = 'https://cdnjs.cloudflare.com/';

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL.map(u => new Request(u, {cache:'reload'}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('fsf-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET') return;
  const url = new URL(req.url);

  // Same-origin app files: network first, fall back to the cached copy offline.
  if(url.origin === self.location.origin){
    e.respondWith(
      fetch(req, {cache:'no-cache'})
        .then(res => {
          if(res.ok){ const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
          return res;
        })
        .catch(() => caches.match(req, {ignoreSearch:true})
          .then(hit => hit || (req.mode === 'navigate' ? caches.match('./index.html') : Response.error())))
    );
    return;
  }

  // Leaflet from cdnjs: version-pinned URL, so cache-first is safe.
  if(req.url.startsWith(CDN)){
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        if(res.ok || res.type === 'opaque'){ const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
        return res;
      }))
    );
  }
  // Everything else (map tiles) goes straight to the network.
});
