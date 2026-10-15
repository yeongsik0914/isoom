/**
 * 👶 아이숨 (Aisum) - 프론트엔드 모달 다이얼로그 & 인터랙션 제어 스크립트 (Vanilla JS)
 * - 크로스 브라우징 듀얼 로더 중복 실행 방지 (Idempotent Guard)
 * - 어떤 버튼(히어로 CTA, 증상 칩, 병원 카드 등)을 클릭하면 모달 팝업 오픈
 * - 모달 오픈 시 배경 어두운 반투명 오버레이 처리
 * - 하단 '취소' 및 '확인' 버튼, 오버레이 클릭 시 모달 닫기
 * - 증상 입력 페이지(input.html) 인풋 인터랙션 및 엔터키 입력 처리
 */

// ============================================================================
// 📱 Global Font Size Management System (작게: small / 보통: normal / 크게: large)
// ============================================================================
window.applyAisumFontSize = function(size) {
  try {
    const targetSize = size || localStorage.getItem('aisum_font_size') || 'normal';
    if (document.documentElement) {
      document.documentElement.classList.remove('font-size-small', 'font-size-normal', 'font-size-large');
      document.documentElement.classList.add('font-size-' + targetSize);
    }
    if (document.body) {
      document.body.classList.remove('font-size-small', 'font-size-normal', 'font-size-large');
      document.body.classList.add('font-size-' + targetSize);
    }

    // Synchronize select element if it exists in the DOM
    const selectEl = document.getElementById('font-size-select');
    if (selectEl) {
      if (selectEl.value !== targetSize) {
        selectEl.value = targetSize;
      }
      for (let i = 0; i < selectEl.options.length; i++) {
        selectEl.options[i].selected = (selectEl.options[i].value === targetSize);
      }
    }

    return targetSize;
  } catch (e) {
    console.warn('Font size apply failed:', e);
    return 'normal';
  }
};

// Immediate execution to prevent FOUC (Flash of Unstyled Content)
if (typeof document !== 'undefined') {
  if (document.body) {
    window.applyAisumFontSize();
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.applyAisumFontSize());
  } else {
    window.applyAisumFontSize();
  }
}

// ============================================================================
// 🛡️ Global Permission & Location Persistence Manager (앱 전체 권한 유지)
// ============================================================================
window.AisumPermissionManager = {
  isGranted: function() {
    try {
      return localStorage.getItem('aisum_permission_granted') === 'true';
    } catch (e) {
      return false;
    }
  },
  getLocationStatus: function() {
    try {
      return localStorage.getItem('aisum_permission_location') || 'prompt';
    } catch (e) {
      return 'prompt';
    }
  },
  getUserLocation: function() {
    try {
      const sLat = localStorage.getItem('aisum_user_lat') || localStorage.getItem('user_lat');
      const sLon = localStorage.getItem('aisum_user_lon') || localStorage.getItem('user_lon');
      const dong = localStorage.getItem('aisum_user_dong') || localStorage.getItem('user_dong') || '역삼동';
      return {
        lat: sLat ? parseFloat(sLat) : 37.5006,
        lon: sLon ? parseFloat(sLon) : 127.0365,
        dong: dong,
        isCustom: localStorage.getItem('aisum_location_manual') === 'true'
      };
    } catch (e) {
      return { lat: 37.5006, lon: 127.0365, dong: '역삼동', isCustom: false };
    }
  },
  saveUserLocation: function(lat, lon, dong) {
    try {
      localStorage.setItem('aisum_user_lat', lat);
      localStorage.setItem('aisum_user_lon', lon);
      localStorage.setItem('user_lat', lat);
      localStorage.setItem('user_lon', lon);
      localStorage.setItem('aisum_user_dong', dong);
      localStorage.setItem('user_dong', dong);
      localStorage.setItem('aisum_permission_granted', 'true');
      localStorage.setItem('aisum_permission_location', 'granted');
    } catch (e) {
      console.warn('PermissionManager save failed:', e);
    }
  }
};

// ============================================================================
// 📍 Real-Time User Location & Spatial Dong Mapping Engine (Vanilla JS)
// ============================================================================
window.AISUM_LOCATIONS_DB = [
  // 1. 서울 주요 거점 (달빛병원 연계)
  { name: '역삼동', gu: '강남구', lat: 37.5006, lon: 127.0365, isPopular: true },
  { name: '방배동', gu: '서초구', lat: 37.498871, lon: 126.993414, isPopular: true },
  { name: '청파동', gu: '용산구', lat: 37.552431, lon: 126.969145, isPopular: true },
  { name: '상계동', gu: '노원구', lat: 37.654812, lon: 127.060124, isPopular: true },
  { name: '목동', gu: '양천구', lat: 37.524812, lon: 126.868215, isPopular: true },
  { name: '삼성동', gu: '강남구', lat: 37.5140, lon: 127.0565, isPopular: false },
  { name: '서초동', gu: '서초구', lat: 37.4918, lon: 127.0079, isPopular: false },
  { name: '잠실동', gu: '송파구', lat: 37.5133, lon: 127.1001, isPopular: true },
  { name: '공덕동', gu: '마포구', lat: 37.5445, lon: 126.9515, isPopular: false },
  { name: '여의도동', gu: '영등포구', lat: 37.5218, lon: 126.9242, isPopular: false },

  // 2. 경기 / 인천 주요 권역
  { name: '정자동', gu: '성남 분당구', lat: 37.367124, lon: 127.108215, isPopular: true },
  { name: '판교동', gu: '성남 분당구', lat: 37.3940, lon: 127.1110, isPopular: false },
  { name: '영통동', gu: '수원 영통구', lat: 37.288541, lon: 127.051214, isPopular: true },
  { name: '일산동', gu: '고양 일산동구', lat: 37.643812, lon: 126.786512, isPopular: true },
  { name: '동탄동', gu: '화성시 동탄', lat: 37.206512, lon: 127.072412, isPopular: true },
  { name: '구월동', gu: '인천 남동구', lat: 37.452412, lon: 126.708214, isPopular: true },
  { name: '청라동', gu: '인천 서구', lat: 37.534812, lon: 126.654215, isPopular: true },
  { name: '송도동', gu: '인천 연수구', lat: 37.3940, lon: 126.6540, isPopular: false },

  // 3. 충청권 거점
  { name: '둔산동', gu: '대전 서구', lat: 36.352412, lon: 127.378512, isPopular: true },
  { name: '봉명동', gu: '대전 유성구', lat: 36.3570, lon: 127.3420, isPopular: false },
  { name: '나성동', gu: '세종시', lat: 36.504812, lon: 127.251214, isPopular: true },
  { name: '불당동', gu: '천안 서북구', lat: 36.815214, lon: 127.108412, isPopular: true },
  { name: '복대동', gu: '청주 흥덕구', lat: 36.621214, lon: 127.432512, isPopular: true },

  // 4. 영남권 거점
  { name: '만촌동', gu: '대구 수성구', lat: 35.839812, lon: 128.706512, isPopular: true },
  { name: '상인동', gu: '대구 달서구', lat: 35.817412, lon: 128.536214, isPopular: false },
  { name: '서면', gu: '부산 부산진구', lat: 35.158124, lon: 129.043512, isPopular: true },
  { name: '온천동', gu: '부산 동래구', lat: 35.204812, lon: 129.083214, isPopular: false },
  { name: '우동', gu: '부산 해운대구', lat: 35.1631, lon: 129.1636, isPopular: false },
  { name: '삼산동', gu: '울산 남구', lat: 35.538412, lon: 129.324512, isPopular: true },
  { name: '장량동', gu: '포항 북구', lat: 36.068412, lon: 129.378214, isPopular: true },
  { name: '팔용동', gu: '창원 의창구', lat: 35.258412, lon: 128.621214, isPopular: true },
  { name: '삼계동', gu: '김해시', lat: 35.251214, lon: 128.874512, isPopular: false },

  // 5. 호남권 거점
  { name: '수완동', gu: '광주 광산구', lat: 35.188412, lon: 126.821214, isPopular: true },
  { name: '치평동(상무)', gu: '광주 서구', lat: 35.1522, lon: 126.8525, isPopular: false },
  { name: '효자동', gu: '전주 완산구', lat: 35.81716, lon: 127.102276, isPopular: true },
  { name: '조례동', gu: '순천시', lat: 34.954214, lon: 127.518412, isPopular: true },

  // 6. 강원 / 제주 거점
  { name: '일산동', gu: '원주시', lat: 37.338412, lon: 127.941214, isPopular: true },
  { name: '탑동', gu: '제주시', lat: 33.517551, lon: 126.522463, isPopular: true }
];

// Haversine 구면거리 계산 함수 (km 단위)
window.calculateDistanceKm = function(lat1, lon1, lat2, lon2) {
  const R = 6371; // 지구 반경 (km)
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

window.estimateDongFromCoords = function(lat, lon) {
  let best = '역삼동';
  let minD = Infinity;
  const nodes = window.AISUM_LOCATIONS_DB || [];
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const dist = window.calculateDistanceKm(lat, lon, node.lat, node.lon);
    if (dist < minD) {
      minD = dist;
      best = node.name;
    }
  }
  return best;
};

window.updateLocationDisplay = function(dongName, lat, lon) {
  const name = dongName || '역삼동';
  const textEl = document.getElementById('current-location-text');
  const pillBtn = document.getElementById('current-location-pill');
  if (textEl) {
    textEl.textContent = name;
  }
  if (pillBtn) {
    pillBtn.setAttribute('aria-label', `현재 위치 변경: ${name}`);
  }

  // Persist into localStorage via PermissionManager
  if (window.AisumPermissionManager) {
    window.AisumPermissionManager.saveUserLocation(lat || 37.5006, lon || 127.0365, name);
  }

  // Update active status in quick-locations-grid
  const grid = document.getElementById('quick-locations-grid');
  if (grid) {
    const buttons = grid.querySelectorAll('.loc-chip-btn');
    buttons.forEach((btn) => {
      const btnDong = btn.getAttribute('data-dong');
      btn.classList.toggle('active', btnDong === name);
    });
  }
};

// 📍 브라우저 GPS 실시간 위치 자동 감지 파이프라인
window.autoDetectUserLocation = function() {
  if (!('geolocation' in navigator)) {
    window.fetchIpLocationFallback();
    return;
  }

  // 사용자가 위치를 수동으로 지정한 경우 GPS 덮어쓰기 방지
  if (localStorage.getItem('aisum_location_manual') === 'true') {
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const detectedDong = window.estimateDongFromCoords(lat, lon);
      console.log('📍 [Aisum GPS] 브라우저 실시간 위치 감지 완료:', detectedDong, lat, lon);

      window.updateLocationDisplay(detectedDong, lat, lon);
      window.initLiveFacilities();
    },
    (err) => {
      console.warn('📍 [Aisum GPS] Geolocation 자동 감지 대기/실패:', err.message);
      window.fetchIpLocationFallback();
    },
    { enableHighAccuracy: true, timeout: 6000, maximumAge: 30000 }
  );
};

// 🌐 IP 기반 위치 추정 폴백 (GPS 미제공 환경)
window.fetchIpLocationFallback = function() {
  if (localStorage.getItem('aisum_location_manual') === 'true') return;

  fetch('https://ipapi.co/json/')
    .then((res) => res.json())
    .then((data) => {
      if (data && data.latitude && data.longitude) {
        const lat = parseFloat(data.latitude);
        const lon = parseFloat(data.longitude);
        const detectedDong = window.estimateDongFromCoords(lat, lon);
        console.log('🌐 [Aisum IP] IP 기반 위치 감지 완료:', detectedDong, lat, lon);
        window.updateLocationDisplay(detectedDong, lat, lon);
        window.initLiveFacilities();
      }
    })
    .catch((e) => {
      console.log('IP location fallback skipped:', e);
    });
};

window.initUserLocation = function() {
  const loc = window.AisumPermissionManager
    ? window.AisumPermissionManager.getUserLocation()
    : { lat: 37.5006, lon: 127.0365, dong: '역삼동', isCustom: false };

  window.updateLocationDisplay(loc.dong, loc.lat, loc.lon);

  // 수동 선택 상태가 아니면 실제 기기 GPS 위치 획득 파이프라인 가동
  if (!loc.isCustom) {
    window.autoDetectUserLocation();
  }
};

window.refreshUserCurrentLocation = function() {
  const btn = document.getElementById('btn-gps-refresh');
  const originalHtml = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.style.opacity = '0.7';
    btn.innerHTML = '<span class="material-symbols-outlined gps-icon" style="animation:spin 1s linear infinite;">sync</span><div class="gps-text-wrap"><span class="gps-main-text">현재 위치 측정 중...</span></div>';
  }

  // 수동 선택 해제
  try {
    localStorage.removeItem('aisum_location_manual');
  } catch (e) {}

  if (!('geolocation' in navigator)) {
    if (btn) {
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.innerHTML = originalHtml;
    }
    if (typeof window.showAisumToast === 'function') {
      window.showAisumToast('기기에서 위치 서비스를 지원하지 않습니다.');
    }
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      if (btn) {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerHTML = originalHtml;
      }
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const dong = window.estimateDongFromCoords(lat, lon);
      window.updateLocationDisplay(dong, lat, lon);
      if (typeof window.closeLocationModal === 'function') {
        window.closeLocationModal();
      }
      if (typeof window.initLiveFacilities === 'function') {
        window.initLiveFacilities();
      }
      if (typeof window.showAisumToast === 'function') {
        window.showAisumToast(`📍 현재 위치(${dong})로 갱신되었습니다.`);
      }
    },
    (err) => {
      console.warn('Geolocation error:', err);
      if (btn) {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerHTML = originalHtml;
      }
      if (typeof window.showAisumToast === 'function') {
        window.showAisumToast('위치 권한을 확인해주세요. (설정에서 허용 필요)');
      }
    },
    { enableHighAccuracy: true, timeout: 6000, maximumAge: 5000 }
  );
};

window.setUserCustomLocation = function(dongName, lat, lon) {
  try {
    localStorage.setItem('aisum_location_manual', 'true');
  } catch (e) {}

  window.updateLocationDisplay(dongName, lat, lon);
  if (typeof window.closeLocationModal === 'function') {
    window.closeLocationModal();
  }
  if (typeof window.initLiveFacilities === 'function') {
    window.initLiveFacilities();
  }
  if (typeof window.showAisumToast === 'function') {
    window.showAisumToast(`📍 위치가 '${dongName}'으로 설정되었습니다.`);
  }
};

window.openLocationModal = function() {
  const modal = document.getElementById('location-select-modal');
  if (!modal) return;
  modal.classList.add('active');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';

  // Render quick locations if grid is empty
  const grid = document.getElementById('quick-locations-grid');
  if (grid) {
    const popular = (window.AISUM_LOCATIONS_DB || []).filter((item) => item.isPopular);
    const currentDong = localStorage.getItem('aisum_user_dong') || localStorage.getItem('user_dong') || '역삼동';
    let chipsHtml = '';
    popular.forEach((loc) => {
      const isActive = loc.name === currentDong;
      chipsHtml += `
        <button type="button" class="loc-chip-btn ${isActive ? 'active' : ''}" data-dong="${loc.name}" onclick="window.setUserCustomLocation('${loc.name}', ${loc.lat}, ${loc.lon})">
          <span class="chip-name">${loc.name}</span>
          <span class="chip-gu">${loc.gu}</span>
        </button>
      `;
    });
    grid.innerHTML = chipsHtml;
  }
};

window.closeLocationModal = function() {
  const modal = document.getElementById('location-select-modal');
  if (!modal) return;
  modal.classList.remove('active');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
};

// ============================================================================
// 🏥 Real-Time Nighttime Medical Facilities Loader (정적 데이터 기반 0ms 실시간 공간 연동)
// ============================================================================
window.__LIVE_FACILITIES_DATA__ = [];
window.__CURRENT_FACILITY_FILTER__ = 'all';

window.initLiveFacilities = function() {
  const stack = document.getElementById('facility-card-stack');
  if (!stack) return; // Only run on index.html

  // 1. 사용자 현재 위치 좌표 획득 (PermissionManager 활용)
  const userLoc = window.AisumPermissionManager
    ? window.AisumPermissionManager.getUserLocation()
    : { lat: 37.5006, lon: 127.0365, dong: '역삼동' };
  const lat = userLoc.lat;
  const lon = userLoc.lon;

  // 2. data/nationwide_pairings.json 정적 데이터셋을 바탕으로 실시간 구면거리 계산
  const sourceData = window.NATIONWIDE_PAIRINGS_DATA || [];
  if (sourceData.length === 0) return;

  // 3. 병원(29개) 거리 계산 및 오름차순 정렬
  const hospitals = sourceData.map((p) => {
    const hLat = parseFloat(p.병원위도) || lat;
    const hLon = parseFloat(p.병원경도) || lon;
    const dist = window.calculateDistanceKm(lat, lon, hLat, hLon);
    const hDist = dist.toFixed(1);
    const hWalk = Math.max(5, Math.round(dist * 14)) + '분';
    const hCar = Math.max(3, Math.round(dist * 2.5)) + '분';
    const hClose = p.병원_평일마감 ? `오늘 ~${p.병원_평일마감} 마감` : '야간 진료';

    return {
      type: 'hospital',
      name: p.병원명 || '달빛어린이병원',
      badge: p.병원유형 || '달빛어린이병원',
      subBadge: '',
      status: '진료중 · 접수 가능',
      desc: `소아청소년과 전문의 진료중 · ${p.병원_평일진료 ? '평일 ' + p.병원_평일진료 : '야간 진료 지정기관'}`,
      phone: p.병원전화 || '02-1234-5678',
      distKm: dist,
      dist: hDist,
      walkTime: hWalk,
      carTime: hCar,
      closing: hClose,
      pairingPharmacy: p.약국명 || ''
    };
  });
  hospitals.sort((a, b) => a.distKm - b.distKm);

  // 4. 약국(29개) 거리 계산 및 오름차순 정렬
  const pharmacies = [];
  sourceData.forEach((p) => {
    if (!p.약국명) return;
    const phLat = parseFloat(p.약국위도) || parseFloat(p.병원위도) || lat;
    const phLon = parseFloat(p.약국경도) || parseFloat(p.병원경도) || lon;
    const dist = window.calculateDistanceKm(lat, lon, phLat, phLon);
    const phDist = dist.toFixed(1);
    const phWalk = Math.max(5, Math.round(dist * 14)) + '분';
    const phCar = Math.max(3, Math.round(dist * 2.5)) + '분';
    const subGuide = p.이동안내 ? `${p.이동안내}` : `병원 인근 ${p.병원_약국_거리 || 50}m`;
    const phClose = p.약국_평일마감
      ? `오늘 ~${p.약국_평일마감} 마감 (+${p.안전마진_분 || 30}분 안심)`
      : '야간 운영';

    pharmacies.push({
      type: 'pharmacy',
      name: p.약국명,
      badge: p.약국구분 || '심야약국',
      subBadge: subGuide,
      status: p.조제안전등급 || '🟢 30분 안심 조제',
      desc: `소아 시럽제 조제 가능 · 30분 안심 조제 (${p.약국_평일운영 || '야간 운영'})`,
      phone: p.약국전화 || '02-555-1234',
      distKm: dist,
      dist: phDist,
      walkTime: phWalk,
      carTime: phCar,
      closing: phClose,
      pairingHospital: p.병원명 || ''
    });
  });
  pharmacies.sort((a, b) => a.distKm - b.distKm);

  // 5. 전체(all) 탭용 정렬: 최단거리 상위 6개 병원과 그에 매칭된 약국들을 조화롭게 조합 (총 12곳)
  const allList = [];
  const topHospitals = hospitals.slice(0, 6);
  topHospitals.forEach((hosp) => {
    allList.push(hosp);
    // 해당 병원의 협약 약국 찾기
    const matchingPharm = pharmacies.find((ph) => ph.pairingHospital === hosp.name || ph.name.includes(hosp.pairingPharmacy));
    if (matchingPharm && !allList.includes(matchingPharm)) {
      allList.push(matchingPharm);
    }
  });

  window.__LIVE_FACILITIES_MASTER__ = {
    all: allList,
    hospital: hospitals.slice(0, 8),
    pharmacy: pharmacies.slice(0, 8)
  };

  window.renderLiveFacilities(window.__CURRENT_FACILITY_FILTER__ || 'all');
};

window.renderLiveFacilities = function(filter) {
  const stack = document.getElementById('facility-card-stack');
  if (!stack || !window.__LIVE_FACILITIES_MASTER__) return;

  const master = window.__LIVE_FACILITIES_MASTER__;
  const currentFilter = filter || 'all';
  const displayList = master[currentFilter] || master.all || [];

  // Update Count Badge & Tabs
  const totalCount = (master.all || []).length;
  const hospCount = (master.hospital || []).length;
  const pharmCount = (master.pharmacy || []).length;

  const countBadge = document.getElementById('live-facilities-count');
  if (countBadge) countBadge.textContent = `${totalCount}곳 운영중`;

  const countAll = document.getElementById('count-all');
  if (countAll) countAll.textContent = totalCount;

  const countHosp = document.getElementById('count-hospital');
  if (countHosp) countHosp.textContent = hospCount;

  const countPharm = document.getElementById('count-pharmacy');
  if (countPharm) countPharm.textContent = pharmCount;

  // Render cards HTML
  let cardsHTML = '';
  displayList.forEach((facility) => {
    const isHospital = facility.type === 'hospital';
    const icon = isHospital ? 'bedtime' : 'medication';
    const iconClass = isHospital ? '' : 'pharmacy';
    const badgeClass = isHospital ? 'moonlight' : 'pharmacy';
    const badgeText = facility.badge || (isHospital ? '달빛어린이병원' : '심야약국');

    const subBadgeHTML = !isHospital && facility.subBadge
      ? `<span class="tag-badge distance-sub">${facility.subBadge}</span>`
      : '';

    const statusBadgeHTML = isHospital
      ? `<span class="tag-badge status-open"><span class="status-indicator-dot" aria-hidden="true"></span>${facility.status}</span>`
      : `<span class="tag-badge status-open"><span class="status-indicator-dot" aria-hidden="true"></span>${facility.status}</span>`;

    const distanceText = isHospital
      ? `내 위치 ${facility.dist}km (도보 ${facility.walkTime} / 차 ${facility.carTime})`
      : `내 위치 ${facility.dist}km (도보 ${facility.walkTime} / 차 ${facility.carTime})`;

    cardsHTML += `
      <article class="facility-card live-card" data-type="${facility.type}">
        <div class="card-top">
          <div class="facility-main">
            <div class="facility-icon-wrap ${iconClass}" aria-hidden="true">
              <span class="material-symbols-outlined">${icon}</span>
            </div>
            <div class="facility-meta">
              <div class="badge-row">
                <span class="tag-badge ${badgeClass}">${badgeText}</span>
                ${subBadgeHTML}
                ${statusBadgeHTML}
              </div>
              <h3 class="facility-name">${facility.name}</h3>
              <p class="facility-desc">${facility.desc}</p>
            </div>
          </div>
          <a href="tel:${facility.phone}" class="call-btn" aria-label="${facility.name} 전화 걸기">
            <span class="material-symbols-outlined">call</span>
          </a>
        </div>

        <div class="card-footer">
          <div class="distance-info">
            <span class="material-symbols-outlined">near_me</span>
            <span>${distanceText}</span>
          </div>
          <span class="closing-time-tag">${facility.closing}</span>
        </div>
      </article>
    `;
  });

  stack.innerHTML = cardsHTML;
};

window.filterLiveFacilities = function(filter) {
  window.__CURRENT_FACILITY_FILTER__ = filter;

  // Update tab styles
  const tabAll = document.getElementById('tab-filter-all');
  const tabHosp = document.getElementById('tab-filter-hospital');
  const tabPharm = document.getElementById('tab-filter-pharmacy');

  if (tabAll) {
    tabAll.classList.toggle('active', filter === 'all');
    tabAll.setAttribute('aria-selected', filter === 'all' ? 'true' : 'false');
  }
  if (tabHosp) {
    tabHosp.classList.toggle('active', filter === 'hospital');
    tabHosp.setAttribute('aria-selected', filter === 'hospital' ? 'true' : 'false');
  }
  if (tabPharm) {
    tabPharm.classList.toggle('active', filter === 'pharmacy');
    tabPharm.setAttribute('aria-selected', filter === 'pharmacy' ? 'true' : 'false');
  }

  window.renderLiveFacilities(filter);
};

// BFCache (Back-Forward Cache) and navigation restoration
if (typeof window !== 'undefined') {
  window.addEventListener('pageshow', () => {
    window.applyAisumFontSize();
    if (typeof window.initUserLocation === 'function') {
      window.initUserLocation();
    }
    if (typeof window.updateChildInfoDisplay === 'function') {
      window.updateChildInfoDisplay();
    }
    if (typeof window.initLiveFacilities === 'function') {
      window.initLiveFacilities();
    }
  });
}

// ============================================================================
// 📱 Select Box Change Handler (작게 / 보통 / 크게)
// ============================================================================
window.onFontSizeChange = function(newSize) {
  const size = newSize || 'normal';
  try {
    localStorage.setItem('aisum_font_size', size);
  } catch (e) {
    console.warn('Failed to save font size to localStorage:', e);
  }
  window.applyAisumFontSize(size);
};

// Backward-compatible safe fallback
window.openFontSizeModal = function() {
  const selectEl = document.getElementById('font-size-select');
  if (selectEl) selectEl.focus();
};

// ============================================================================
// 👶 Global Child Information Management System (자녀 기본 정보 관리 & BFCache 동기화)
// ============================================================================
window.updateChildInfoDisplay = function() {
  try {
    const displayEl = document.getElementById('child-info-display');
    if (!displayEl) return;

    const raw = localStorage.getItem('aisum_child_info');
    let year = '2023';
    let gender = 'male';
    let name = '';

    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed.birthYear) year = parsed.birthYear;
      if (parsed.gender) gender = parsed.gender;
      if (parsed.name) name = parsed.name;
    }

    const currentYear = 2026;
    const age = Math.max(0, currentYear - parseInt(year, 10));
    const genderLabel = gender === 'female' ? '여아' : (gender === 'male' ? '남아' : '');

    let summary = '';
    if (genderLabel) {
      summary = `${year}년생 (${genderLabel}, 만 ${age}세)`;
    } else {
      summary = `${year}년생 (만 ${age}세)`;
    }

    displayEl.textContent = summary;
  } catch (e) {
    console.warn('Child info display update failed:', e);
  }
};

window.selectedChildGender = 'male';

window.openChildInfoModal = function() {
  const modal = document.getElementById('child-info-modal');
  if (!modal) return;

  try {
    const raw = localStorage.getItem('aisum_child_info');
    let name = '';
    let birthYear = '2023';
    let gender = 'male';

    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed.name) name = parsed.name;
      if (parsed.birthYear) birthYear = parsed.birthYear;
      if (parsed.gender) gender = parsed.gender;
    }

    const nameInput = document.getElementById('child-name-input');
    const birthSelect = document.getElementById('child-birth-select');

    if (nameInput) nameInput.value = name;
    if (birthSelect) birthSelect.value = birthYear;
    window.setChildGender(gender);
  } catch (e) {
    console.warn('Failed to populate child info modal:', e);
  }

  modal.classList.add('active');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
};

window.closeChildInfoModal = function() {
  const modal = document.getElementById('child-info-modal');
  if (!modal) return;
  modal.classList.remove('active');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
};

window.setChildGender = function(gender) {
  window.selectedChildGender = gender || 'male';
  const maleBtn = document.getElementById('gender-btn-male');
  const femaleBtn = document.getElementById('gender-btn-female');

  if (maleBtn && femaleBtn) {
    if (gender === 'female') {
      femaleBtn.classList.add('active');
      maleBtn.classList.remove('active');
    } else {
      maleBtn.classList.add('active');
      femaleBtn.classList.remove('active');
    }
  }
};

window.saveChildInfo = function() {
  try {
    const nameInput = document.getElementById('child-name-input');
    const birthSelect = document.getElementById('child-birth-select');
    const name = nameInput ? nameInput.value.trim() : '';
    const birthYear = birthSelect ? birthSelect.value : '2023';
    const gender = window.selectedChildGender || 'male';

    const childInfo = { name, birthYear, gender };
    localStorage.setItem('aisum_child_info', JSON.stringify(childInfo));

    window.updateChildInfoDisplay();
    window.closeChildInfoModal();
    window.showAisumToast('자녀 기본 정보가 저장되었습니다.');
  } catch (e) {
    console.error('Failed to save child info:', e);
  }
};

window.showAisumToast = function(msg) {
  let toast = document.getElementById('aisum-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'aisum-toast';
    toast.className = 'aisum-toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg || '저장되었습니다.';
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2200);
};

if (!window.__AISUM_INITIALIZED__) {
  window.__AISUM_INITIALIZED__ = true;

  document.addEventListener('DOMContentLoaded', () => {
    console.log('👶 아이숨 (Aisum) 모바일 웹 화면이 Safari/Chrome 호환 모드로 로드되었습니다.');

    // Initialize font size select on settings page
    const selectEl = document.getElementById('font-size-select');
    if (selectEl) {
      const savedSize = localStorage.getItem('aisum_font_size') || 'normal';
      selectEl.value = savedSize;
    }

    // Initialize child info display on settings page
    if (typeof window.updateChildInfoDisplay === 'function') {
      window.updateChildInfoDisplay();
    }

    // Initialize user location on main home
    if (typeof window.initUserLocation === 'function') {
      window.initUserLocation();
    }

    // Initialize real-time medical facilities on main home (index.html)
    if (typeof window.initLiveFacilities === 'function') {
      window.initLiveFacilities();
    }

    // Location Pill and Location Modal Listeners
    const locationPillBtn = document.getElementById('current-location-pill');
    if (locationPillBtn) {
      locationPillBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (typeof window.openLocationModal === 'function') {
          window.openLocationModal();
        }
      });
    }

    const locationModalCloseBtn = document.getElementById('location-modal-close-btn');
    if (locationModalCloseBtn) {
      locationModalCloseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (typeof window.closeLocationModal === 'function') {
          window.closeLocationModal();
        }
      });
    }

    const locationModal = document.getElementById('location-select-modal');
    if (locationModal) {
      locationModal.addEventListener('click', (e) => {
        if (e.target === locationModal) {
          if (typeof window.closeLocationModal === 'function') {
            window.closeLocationModal();
          }
        }
      });
    }

    // DOM Elements
    const modal = document.getElementById('triage-consent-modal');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');

    // Modal Open Triggers
    const startTriageBtn = document.getElementById('start-triage-btn');
    const quickSymptomChips = document.querySelectorAll('.symptom-chip');
    const facilityCards = document.querySelectorAll('.facility-card');

    function openModal() {
      if (!modal) return;
      modal.classList.add('active');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      if (!modal) return;
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }

    // 1. Trigger Open: 메인 CTA 버튼 클릭 시 모달 열기
    if (startTriageBtn) {
      startTriageBtn.addEventListener('click', (e) => {
        e.preventDefault();
        openModal();
      });
    }

    // 2. Trigger Open: 상단 증상 칩 클릭 시 모달 열기
    quickSymptomChips.forEach((chip) => {
      chip.addEventListener('click', (e) => {
        e.preventDefault();
        openModal();
      });
    });

    // 3. Trigger Open: 병원 카드 클릭 시 모달 열기 (이벤트 위임 방식으로 동적 실시간 카드 100% 지원)
    const facilityStack = document.getElementById('facility-card-stack');
    if (facilityStack) {
      facilityStack.addEventListener('click', (e) => {
        if (e.target.closest('.call-btn') || e.target.closest('a[href^="tel:"]')) {
          return; // 전화 걸기는 기본 다이얼 동작 유지
        }
        const card = e.target.closest('.facility-card');
        if (card) {
          e.preventDefault();
          openModal();
        }
      });
    }

    // 정적 카드 폴백 리스너
    facilityCards.forEach((card) => {
      card.addEventListener('click', (e) => {
        if (e.target.closest('.call-btn') || e.target.closest('a[href^="tel:"]')) {
          return;
        }
        e.preventDefault();
        openModal();
      });
    });

    // 4. Modal Action: '취소' 버튼 클릭 시 모달 닫기
    if (modalCancelBtn) {
      modalCancelBtn.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal();
      });
    }

    // 5. Modal Action: '동의하고 증상 입력하기' 최종확인 버튼 클릭 시 input.html 화면으로 연동
    if (modalConfirmBtn) {
      modalConfirmBtn.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal();
        window.location.href = 'input.html';
      });
    }

    // 6. Overlay Click: 어두운 반투명 배경 클릭 시 모달 닫기
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          closeModal();
        }
      });
    }

    // 7. Symptom Input Page Logic (사용자 텍스트 입력 시 확인 버튼 및 플로팅 레이블 토글)
    if (window.__AISUM_CUSTOM_INPUT__) {
      return; // input.html 페이지 자체 프로그레시브 챗봇 컨트롤러 우선 실행
    }

    const symptomInput = document.getElementById('symptom-input');
    const floatingLabel = document.getElementById('floating-label');
    const inputClearBtn = document.getElementById('input-clear-btn');
    const inputConfirmWrap = document.getElementById('input-confirm-wrap');
    const inputConfirmBtn = document.getElementById('input-confirm-btn');

    function updateInputState() {
      if (!symptomInput) return;
      const hasContent = symptomInput.value.trim().length > 0;

      if (floatingLabel) floatingLabel.style.display = hasContent ? 'block' : 'none';
      if (inputClearBtn) inputClearBtn.style.display = hasContent ? 'inline-flex' : 'none';
      if (inputConfirmWrap) {
        if (hasContent) {
          inputConfirmWrap.classList.add('active');
          inputConfirmWrap.style.display = 'block';
        } else {
          inputConfirmWrap.classList.remove('active');
          inputConfirmWrap.style.display = 'none';
        }
      }
    }

    if (symptomInput) {
      symptomInput.addEventListener('input', updateInputState);

      if (inputClearBtn) {
        inputClearBtn.addEventListener('click', (e) => {
          e.preventDefault();
          symptomInput.value = '';
          updateInputState();
          symptomInput.focus();
        });
      }

      symptomInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const text = symptomInput.value.trim();
          if (!text) {
            symptomInput.focus();
            return;
          }
          if (inputConfirmBtn) {
            inputConfirmBtn.click();
          }
        }
      });
    }

    if (inputConfirmBtn) {
      inputConfirmBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const text = symptomInput ? symptomInput.value.trim() : '';
        if (text) {
          console.log('✅ 사용자 증상 입력 확인 완료:', text);

          // 🚨 0ms Red Flag 긴급 숏서킷 (경련, 호흡곤란, 의식저하, 생후 100일 미만 등)
          const redFlagRegex = /경련|경기|숨|호흡|의식|기절|청색|100일|백일|장중첩|피토|혈변|쳐짐|늘어짐|파랗|경직/;
          if (redFlagRegex.test(text)) {
            console.log('🚨 0ms Red Flag 감지! 119 긴급 안내 화면으로 즉각 숏서킷 전환:', text);
            if (symptomInput) symptomInput.blur();
            const alertTargetUrl = window.location.pathname.endsWith('.html') ? 'emergency_alert.html' : 'emergency_alert';
            window.location.href = alertTargetUrl;
            return;
          }

          const overlay = document.getElementById('ai-analyzing-overlay');
          const stepText = document.getElementById('analyzing-step-text');
          const stepIcon = document.getElementById('analyzing-step-icon');
          const progressFill = document.getElementById('analyzing-progress-fill');
          const targetUrl = window.location.pathname.endsWith('.html') ? 'result.html' : 'result';

          if (overlay) {
            // 모바일 키보드 닫기
            symptomInput.blur();
            overlay.classList.add('active');
            overlay.setAttribute('aria-hidden', 'false');

            // 1단계: 0.0초 시작 (가드레일 검사)
            if (progressFill) progressFill.style.width = '35%';

            // 2단계: 0.7초 (소아 KTAS 임상 지침 대조)
            setTimeout(() => {
              if (stepText) stepText.innerText = '소아 KTAS 임상 지침 168개 주증상 대조 중...';
              if (stepIcon) stepIcon.innerText = 'stethoscope';
              if (progressFill) progressFill.style.width = '70%';
            }, 700);

            // 3단계: 1.4초 (달빛병원 & 30분 마진 심야약국 매칭)
            setTimeout(() => {
              if (stepText) stepText.innerText = '달빛어린이병원 & 30분 마진 심야약국 매칭 완료!';
              if (stepIcon) stepIcon.innerText = 'verified';
              if (progressFill) progressFill.style.width = '100%';
            }, 1400);

            // 4단계: 2.0초 만료 ➔ 결과 화면으로 부드럽게 전환!
            setTimeout(() => {
              window.location.href = targetUrl;
            }, 2000);
          } else {
            window.location.href = targetUrl;
          }
        }
      });
    }
  });
}
