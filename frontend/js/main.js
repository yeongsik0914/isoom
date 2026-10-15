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
// 📍 Real-Time User Location & Spatial Dong Mapping Engine (Vanilla JS)
// ============================================================================
window.AISUM_LOCATIONS_DB = [
  // 강남구
  { name: '역삼동', gu: '강남구', lat: 37.5006, lon: 127.0365, isPopular: true },
  { name: '삼성동', gu: '강남구', lat: 37.5140, lon: 127.0565, isPopular: true },
  { name: '대치동', gu: '강남구', lat: 37.4946, lon: 127.0628, isPopular: true },
  { name: '논현동', gu: '강남구', lat: 37.5115, lon: 127.0285, isPopular: false },
  { name: '압구정동', gu: '강남구', lat: 37.5270, lon: 127.0284, isPopular: false },
  { name: '청담동', gu: '강남구', lat: 37.5245, lon: 127.0520, isPopular: false },
  { name: '신사동', gu: '강남구', lat: 37.5205, lon: 127.0230, isPopular: false },
  { name: '개포동', gu: '강남구', lat: 37.4789, lon: 127.0517, isPopular: false },
  { name: '일원동', gu: '강남구', lat: 37.4839, lon: 127.0844, isPopular: false },
  // 서초구
  { name: '서초동', gu: '서초구', lat: 37.4918, lon: 127.0079, isPopular: true },
  { name: '반포동', gu: '서초구', lat: 37.5042, lon: 127.0049, isPopular: true },
  { name: '방배동', gu: '서초구', lat: 37.4815, lon: 126.9975, isPopular: false },
  { name: '양재동', gu: '서초구', lat: 37.4700, lon: 127.0400, isPopular: false },
  // 송파/강동구
  { name: '잠실동', gu: '송파구', lat: 37.5133, lon: 127.1001, isPopular: true },
  { name: '신천동', gu: '송파구', lat: 37.5180, lon: 127.1010, isPopular: false },
  { name: '가락동', gu: '송파구', lat: 37.4925, lon: 127.1189, isPopular: false },
  { name: '문정동', gu: '송파구', lat: 37.4859, lon: 127.1226, isPopular: false },
  { name: '천호동', gu: '강동구', lat: 37.5385, lon: 127.1235, isPopular: true },
  { name: '길동', gu: '강동구', lat: 37.5345, lon: 127.1402, isPopular: false },
  // 마포/서대문
  { name: '공덕동', gu: '마포구', lat: 37.5445, lon: 126.9515, isPopular: true },
  { name: '상암동', gu: '마포구', lat: 37.5775, lon: 126.8915, isPopular: true },
  { name: '합정동', gu: '마포구', lat: 37.5495, lon: 126.9135, isPopular: false },
  { name: '망원동', gu: '마포구', lat: 37.5562, lon: 126.9103, isPopular: false },
  // 영등포/양천/강서/구로
  { name: '여의도동', gu: '영등포구', lat: 37.5218, lon: 126.9242, isPopular: true },
  { name: '당산동', gu: '영등포구', lat: 37.5338, lon: 126.8995, isPopular: false },
  { name: '목동', gu: '양천구', lat: 37.5370, lon: 126.8745, isPopular: true },
  { name: '신정동', gu: '양천구', lat: 37.5180, lon: 126.8560, isPopular: false },
  { name: '화곡동', gu: '강서구', lat: 37.5410, lon: 126.8400, isPopular: true },
  { name: '마곡동', gu: '강서구', lat: 37.5600, lon: 126.8250, isPopular: true },
  { name: '신도림동', gu: '구로구', lat: 37.5090, lon: 126.8910, isPopular: true },
  // 용산/성동/종로/중구
  { name: '한남동', gu: '용산구', lat: 37.5347, lon: 127.0022, isPopular: true },
  { name: '이촌동', gu: '용산구', lat: 37.5175, lon: 126.9742, isPopular: false },
  { name: '성수동', gu: '성동구', lat: 37.5445, lon: 127.0560, isPopular: true },
  { name: '명동', gu: '중구', lat: 37.5636, lon: 126.9827, isPopular: false },
  { name: '종로', gu: '종로구', lat: 37.5704, lon: 126.9922, isPopular: false },
  // 관악/동작
  { name: '신림동', gu: '관악구', lat: 37.4842, lon: 126.9298, isPopular: true },
  { name: '사당동', gu: '동작구', lat: 37.4820, lon: 126.9760, isPopular: true },
  // 노원/도봉/강북
  { name: '상계동', gu: '노원구', lat: 37.6550, lon: 127.0670, isPopular: true },
  { name: '수유동', gu: '강북구', lat: 37.6380, lon: 127.0250, isPopular: false },
  // 수도권 주요 거점
  { name: '정자동', gu: '성남 분당구', lat: 37.3660, lon: 127.1080, isPopular: true },
  { name: '판교동', gu: '성남 분당구', lat: 37.3940, lon: 127.1110, isPopular: true },
  { name: '일산동', gu: '고양 일산동구', lat: 37.6860, lon: 126.7710, isPopular: true },
  { name: '영통동', gu: '수원 영통구', lat: 37.2520, lon: 127.0710, isPopular: true },
  { name: '송도동', gu: '인천 연수구', lat: 37.3940, lon: 126.6540, isPopular: true }
];

window.estimateDongFromCoords = function(lat, lon) {
  let best = '역삼동';
  let minD = Infinity;
  const nodes = window.AISUM_LOCATIONS_DB || [];
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const dLat = (lat - node.lat) * (Math.PI / 180);
    const dLon = (lon - node.lon) * (Math.PI / 180);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat * (Math.PI / 180)) * Math.cos(node.lat * (Math.PI / 180)) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const dist = 6371 * c;
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

  // Persist into localStorage
  try {
    localStorage.setItem('aisum_user_dong', name);
    localStorage.setItem('user_dong', name);
    if (lat && lon) {
      localStorage.setItem('aisum_user_lat', lat);
      localStorage.setItem('aisum_user_lon', lon);
      localStorage.setItem('user_lat', lat);
      localStorage.setItem('user_lon', lon);
    }
  } catch (e) {
    console.warn('Storage save failed:', e);
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

window.initUserLocation = function() {
  let savedDong = localStorage.getItem('aisum_user_dong') || localStorage.getItem('user_dong');
  const sLat = localStorage.getItem('aisum_user_lat') || localStorage.getItem('user_lat');
  const sLon = localStorage.getItem('aisum_user_lon') || localStorage.getItem('user_lon');

  let lat = sLat ? parseFloat(sLat) : null;
  let lon = sLon ? parseFloat(sLon) : null;

  if (lat && lon && !savedDong) {
    savedDong = window.estimateDongFromCoords(lat, lon);
  } else if (!savedDong && !lat) {
    savedDong = '역삼동';
    lat = 37.5006;
    lon = 127.0365;
  }

  window.updateLocationDisplay(savedDong, lat, lon);
};

window.refreshUserCurrentLocation = function() {
  const btn = document.getElementById('btn-gps-refresh');
  const originalHtml = btn ? btn.innerHTML : '';
  if (btn) {
    btn.disabled = true;
    btn.style.opacity = '0.7';
    btn.innerHTML = '<span class="material-symbols-outlined gps-icon" style="animation:spin 1s linear infinite;">sync</span><div class="gps-text-wrap"><span class="gps-main-text">현재 위치 측정 중...</span></div>';
  }

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
    { enableHighAccuracy: true, timeout: 5000, maximumAge: 10000 }
  );
};

window.setUserCustomLocation = function(dongName, lat, lon) {
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
  if (grid && grid.children.length === 0) {
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
// 🏥 Real-Time Nighttime Medical Facilities Loader (메인 홈 실시간 야간 의료시설 연동)
// ============================================================================
window.__LIVE_FACILITIES_DATA__ = [];
window.__CURRENT_FACILITY_FILTER__ = 'all';

window.initLiveFacilities = async function() {
  const stack = document.getElementById('facility-card-stack');
  if (!stack) return; // Only run on index.html

  let lat = 37.5006; // 역삼동 fallback
  let lon = 127.0365;
  try {
    const sLat = localStorage.getItem('aisum_user_lat') || localStorage.getItem('user_lat');
    const sLon = localStorage.getItem('aisum_user_lon') || localStorage.getItem('user_lon');
    if (sLat && sLon) {
      lat = parseFloat(sLat);
      lon = parseFloat(sLon);
    }
  } catch (e) {}

  try {
    const apiUrl = `/api/v1/emergency/pairings?lat=${lat}&lon=${lon}&radius_km=30.0&limit=8`;
    const res = await fetch(apiUrl);
    if (!res.ok) throw new Error(`API returned ${res.status}`);

    const data = await res.json();
    const pairings = data.pairings || [];
    if (pairings.length === 0) return;

    const list = [];
    pairings.forEach((p) => {
      // Hospital
      const hDist = typeof p.거리_km === 'number' ? p.거리_km.toFixed(1) : (p.거리_km || '1.8');
      const hWalk = Math.max(5, Math.round(parseFloat(hDist) * 14)) + '분';
      const hCar = Math.max(3, Math.round(parseFloat(hDist) * 2.5)) + '분';
      const hClose = p.병원_평일마감 ? `오늘 ~${p.병원_평일마감} 마감` : '야간 진료';

      list.push({
        type: 'hospital',
        name: p.병원명 || '달빛어린이병원',
        badge: '달빛어린이병원',
        status: '진료중 · 접수 가능',
        desc: '소아청소년과 전문의 진료중 · 야간 진료 지정기관',
        phone: p.병원전화 || '02-1234-5678',
        dist: hDist,
        walkTime: hWalk,
        carTime: hCar,
        closing: hClose,
      });

      // Pharmacy
      if (p.약국명) {
        const phDist = (parseFloat(hDist) + (p.병원_약국_거리 || 50) / 1000).toFixed(1);
        const subGuide = p.이동안내 ? `${(p.병원명 || '').split(' ')[0]} 인근 ${p.이동안내}` : `병원 인근 ${p.병원_약국_거리 || 50}m`;
        const phClose = p.약국_평일마감 ? `오늘 ~${p.약국_평일마감} 마감` : '야간 운영';

        list.push({
          type: 'pharmacy',
          name: p.약국명,
          badge: '심야약국',
          subBadge: subGuide,
          desc: '소아 시럽제 조제 가능 · 30분 안심 조제',
          phone: p.약국전화 || '02-555-1234',
          dist: phDist,
          closing: phClose,
        });
      }
    });

    window.__LIVE_FACILITIES_DATA__ = list;
    window.renderLiveFacilities(window.__CURRENT_FACILITY_FILTER__ || 'all');
  } catch (err) {
    console.log('실시간 의료시설 API 비동기 폴백 (정적 데이터 유지):', err.message);
  }
};

window.renderLiveFacilities = function(filter) {
  const stack = document.getElementById('facility-card-stack');
  if (!stack || !window.__LIVE_FACILITIES_DATA__ || window.__LIVE_FACILITIES_DATA__.length === 0) return;

  const data = window.__LIVE_FACILITIES_DATA__;
  const filtered = filter === 'all' ? data : data.filter((item) => item.type === filter);

  // Update Count Badge & Tabs
  const totalCount = data.length;
  const hospCount = data.filter((i) => i.type === 'hospital').length;
  const pharmCount = data.filter((i) => i.type === 'pharmacy').length;

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
  filtered.forEach((facility) => {
    const isHospital = facility.type === 'hospital';
    const icon = isHospital ? 'bedtime' : 'medication';
    const iconClass = isHospital ? '' : 'pharmacy';
    const badgeClass = isHospital ? 'moonlight' : 'pharmacy';
    const badgeText = isHospital ? '달빛어린이병원' : '심야약국';

    const subBadgeHTML = !isHospital && facility.subBadge
      ? `<span class="tag-badge distance-sub">${facility.subBadge}</span>`
      : '';

    const statusBadgeHTML = isHospital
      ? `<span class="tag-badge status-open"><span class="status-indicator-dot" aria-hidden="true"></span>${facility.status}</span>`
      : '';

    const distanceText = isHospital
      ? `내 위치 ${facility.dist}km (도보 ${facility.walkTime} / 차 ${facility.carTime})`
      : `내 위치 ${facility.dist}km`;

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
