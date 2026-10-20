/**
 * 🌙 아이숨 (Aisum) - PWA Service Worker
 * 버전: aisum-sw-v1.0.0
 * 전략:
 *   1) 정적 자산(CSS, JS, 폰트, 아이콘, 셸 HTML): Stale-While-Revalidate
 *   2) 실시간 백엔드 API (/api/*): Network First
 *   3) 음영지역 오프라인 대응
 */

const CACHE_NAME = 'aisum-pwa-cache-v4';

const STATIC_ASSETS = [
  '/',
  '/home',
  '/index.html',
  '/history.html',
  '/briefing_card.html',
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
  '/img/icon-512.png',
  '/favicon.ico'
];

// 1. Install Event: 정적 리소스 프리캐싱 및 대기 없이 즉시 활성화
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Aisum SW v2] Pre-caching static assets');
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('[Aisum SW v2] Non-critical asset cache skip:', err);
      });
    })
  );
});

// 2. Activate Event: 구버전 캐시(v1 등) 전면 정리 및 즉시 모든 클라이언트 제어권 획득
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[Aisum SW v2] Purging legacy cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 3. Fetch Event: HTML 탐색 및 API는 Network-First, 정적 리소스는 최신 업데이트 보장
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // POST, PUT 등 비-GET 요청은 캐싱하지 않고 네트워크 직접 통과
  if (event.request.method !== 'GET') {
    return;
  }

  // 1) HTML 문서 탐색(페이지 이동, 새로고침)은 최신 배포 버전을 즉시 반영하기 위해 Network-First 적용
  const isHtmlNavigation = event.request.mode === 'navigate' ||
    (event.request.headers.get('accept') && event.request.headers.get('accept').includes('text/html'));

  if (isHtmlNavigation) {
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
          return caches.match(event.request) || caches.match('/home') || caches.match('/index.html');
        })
    );
    return;
  }

  // 2) 실시간 E-Gen 병상 및 페어링 API는 Network First
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
          return caches.match(event.request);
        })
    );
    return;
  }

  // 3) 정적 리소스 (CSS, JS, 이미지, 폰트): Stale-While-Revalidate
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return networkResponse;
      }).catch(() => {
        return cachedResponse;
      });

      return cachedResponse || fetchPromise;
    })
  );
});
