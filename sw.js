/* Service Worker: hält die App offline verfügbar.
   Eigene Dateien: aus dem Speicher, im Hintergrund aktualisiert.
   Wetter (Open-Meteo) und Kartenkacheln (OpenStreetMap): nur online, werden nicht gespeichert. */
const CACHE = 'rur-tagebuch-0.9.0';
const SHELL = [
  './', 'index.html', 'manifest.webmanifest', 'vendor/leaflet.js', 'fonts/fonts.css',
  'fonts/amatic-sc-latin-700-normal.woff2', 'fonts/cabin-sketch-latin-700-normal.woff2',
  'fonts/roboto-condensed-latin-400-normal.woff2', 'fonts/roboto-condensed-latin-600-normal.woff2',
  'fonts/roboto-mono-latin-400-normal.woff2', 'fonts/roboto-mono-latin-600-normal.woff2',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png',
  'daten/schonzeiten-binnen.json'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('rur-tagebuch-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  /* Regeldaten: zuerst aus dem Netz, damit Korrekturen sofort ankommen; offline aus dem Speicher */
  if (url.pathname.includes('/daten/')) {
    e.respondWith(caches.open(CACHE).then(cache => fetch(req).then(res => { if (res.ok) cache.put(req, res.clone()); return res; })
      .catch(() => cache.match(req, { ignoreSearch: true }).then(hit => hit || Response.error()))));
    return;
  }
  e.respondWith(caches.open(CACHE).then(async cache => {
    const hit = await cache.match(req, { ignoreSearch: true });
    const net = fetch(req).then(res => { if (res.ok) cache.put(req, res.clone()); return res; }).catch(() => null);
    if (hit) { e.waitUntil(net); return hit; }
    const res = await net;
    return res || (req.mode === 'navigate' ? cache.match('index.html') : Response.error());
  }));
});
