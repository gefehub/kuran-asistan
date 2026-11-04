// Kuran asistanı — çevrimdışı önbellek. Yeni kart eklerken VERSION'u artır.
const VERSION = "kuran-v1";
const FILES = [
 "./",
 "index.html",
 "manifest.webmanifest",
 "icon-180.png",
 "icon-192.png",
 "icon-512.png",
 "lib/pdf.min.js",
 "lib/pdf.worker.min.js",
 "fonts/amiri-arabic-400-normal.woff2",
 "fonts/amiri-arabic-700-normal.woff2",
 "fonts/amiri-latin-400-normal.woff2",
 "fonts/amiri-latin-700-normal.woff2",
 "fonts/source-sans-3-latin-400-normal.woff2",
 "fonts/source-sans-3-latin-600-normal.woff2",
 "fonts/source-sans-3-latin-700-normal.woff2",
 "fonts/source-sans-3-latin-ext-400-normal.woff2",
 "fonts/source-sans-3-latin-ext-600-normal.woff2",
 "fonts/source-sans-3-latin-ext-700-normal.woff2",
 "fiches/bakara-020.pdf",
 "fiches/bakara-021.pdf",
 "fiches/bakara-022.pdf",
 "fiches/bakara-023.pdf",
 "fiches/bakara-024.pdf",
 "fiches/bakara-025.pdf",
 "fiches/bakara-026.pdf",
 "fiches/bakara-027.pdf",
 "fiches/bakara-028.pdf",
 "fiches/bakara-029.pdf",
 "fiches/bakara-030.pdf",
 "fiches/bakara-031.pdf",
 "fiches/bakara-032.pdf",
 "fiches/bakara-033.pdf",
 "fiches/bakara-034.pdf",
 "fiches/bakara-035.pdf",
 "fiches/bakara-036.pdf",
 "fiches/bakara-037.pdf"
];
self.addEventListener("install", e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request, {ignoreSearch:true}).then(r => r || fetch(e.request).then(res => {
    if (res.ok && new URL(e.request.url).origin === location.origin) { const cp = res.clone(); caches.open(VERSION).then(c => c.put(e.request, cp)); }
    return res;
  })));
});
