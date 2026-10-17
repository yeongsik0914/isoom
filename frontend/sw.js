/**
 * 🌙 아이숨 (Aisum) - PWA Service Worker
 * 버전: aisum-sw-v1.0.0
 * 전략:
 *   1) 정적 자산(CSS, JS, 폰트, 아이콘, 셸 HTML): Stale-While-Revalidate
 *   2) 실시간 백엔드 API (/api/*): Network First
 *   3) 음영지역 오프라인 대응
 */

const CACHE_NAME = 'aisum-pwa-cache-v1';

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/input.html',
  '/result.html',
  '/settings.html',
  '/emergency_guide.html',
  '/emergency_guide_symptoms.html',
  '/emergency_guide_checklist.html',
  '/terms.html',
  '/permission.html',
  '/css/style.css',
  '/js/main.js',
  '/manifest.json',
  '/img/icon-192.png',
  '/img/icon-512.png'
];

// 1. Install Event: 정적 리소스 프리캐싱
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Aisum SW] Pre-caching static assets');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[Aisum SW] Non-critical asset cache skip:', err);
      });
    })
  );
});

// 2. Activate Event: 구버전 캐시 정리 및 즉시 제어권 획득
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Aisum SW] Removing legacy cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Event: API는 Network-First, 정적 자산은 Stale-While-Revalidate
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // POST, PUT 등 비-GET 요청은 캐싱하지 않고 네트워크 직접 통과
  if (event.request.method !== 'GET') {
    return;
  }

  // 실시간 E-Gen 병상 및 페어링 API는 Network First
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => {
          // 오프라인일 경우 직전 캐시 반환
          return caches.match(event.request);
        })
    );
    return;
  }

  // 정적 리소스 (HTML, CSS, JS, 이미지, 폰트): Stale-While-Revalidate
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return networkResponse;
      }).catch(() => {
        // 네트워크 실패 시 조용히 캐시 사용
        return cachedResponse;
      });

      return cachedResponse || fetchPromise;
    })
  );
});
