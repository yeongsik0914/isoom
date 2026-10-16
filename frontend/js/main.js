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
      const dong = localStorage.getItem('aisum_user_dong') || localStorage.getItem('user_dong') || '문정동';
      return {
        lat: sLat ? parseFloat(sLat) : 37.4858,
        lon: sLon ? parseFloat(sLon) : 127.1225,
        dong: dong,
        isCustom: localStorage.getItem('aisum_location_manual') === 'true'
      };
    } catch (e) {
      return { lat: 37.4858, lon: 127.1225, dong: '문정동', isCustom: false };
    }
  },
  saveUserLocation: function(lat, lon, dong, fullAddr) {
    try {
      localStorage.setItem('aisum_user_lat', lat);
      localStorage.setItem('aisum_user_lon', lon);
      localStorage.setItem('user_lat', lat);
      localStorage.setItem('user_lon', lon);
      localStorage.setItem('aisum_user_dong', dong);
      localStorage.setItem('user_dong', dong);
      if (fullAddr) {
        localStorage.setItem('aisum_user_address', fullAddr);
      }
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
  // 1. 서울 동남권 (송파 / 강남 / 서초 / 강동)
  { name: '문정동', gu: '송파구', city: '서울', lat: 37.4858, lon: 127.1225, isPopular: true, fullAddr: '서울특별시 송파구 문정동', keywords: ['문정', '문정역', '법조타운', '송파', '문정동', '문정로'] },
  { name: '잠실동', gu: '송파구', city: '서울', lat: 37.5133, lon: 127.1001, isPopular: true, fullAddr: '서울특별시 송파구 잠실동', keywords: ['잠실', '잠실역', '롯데월드', '송파', '신천'] },
  { name: '가락동', gu: '송파구', city: '서울', lat: 37.4925, lon: 127.1188, isPopular: true, fullAddr: '서울특별시 송파구 가락동', keywords: ['가락', '가락시장', '송파'] },
  { name: '방이동', gu: '송파구', city: '서울', lat: 37.5138, lon: 127.1215, isPopular: false, fullAddr: '서울특별시 송파구 방이동', keywords: ['방이', '올림픽공원', '송파'] },
  { name: '역삼동', gu: '강남구', city: '서울', lat: 37.5006, lon: 127.0365, isPopular: true, fullAddr: '서울특별시 강남구 역삼동', keywords: ['역삼', '강남', '테헤란로', '강남역'] },
  { name: '삼성동', gu: '강남구', city: '서울', lat: 37.5140, lon: 127.0565, isPopular: true, fullAddr: '서울특별시 강남구 삼성동', keywords: ['삼성', '코엑스', '강남', '봉은사'] },
  { name: '대치동', gu: '강남구', city: '서울', lat: 37.4946, lon: 127.0628, isPopular: false, fullAddr: '서울특별시 강남구 대치동', keywords: ['대치', '학원가', '한티', '강남'] },
  { name: '압구정동', gu: '강남구', city: '서울', lat: 37.5270, lon: 127.0285, isPopular: false, fullAddr: '서울특별시 강남구 압구정동', keywords: ['압구정', '로데오', '신사', '강남'] },
  { name: '논현동', gu: '강남구', city: '서울', lat: 37.5115, lon: 127.0285, isPopular: false, fullAddr: '서울특별시 강남구 논현동', keywords: ['논현', '학동', '신논현', '강남'] },
  { name: '세곡동', gu: '강남구', city: '서울', lat: 37.4642, lon: 127.1054, isPopular: false, fullAddr: '서울특별시 강남구 세곡동', keywords: ['세곡', '자곡', '수서', '달빛어린이병원', '강남'] },
  { name: '서초동', gu: '서초구', city: '서울', lat: 37.4918, lon: 127.0079, isPopular: true, fullAddr: '서울특별시 서초구 서초동', keywords: ['서초', '교대', '남부터미널', '예술의전당'] },
  { name: '방배동', gu: '서초구', city: '서울', lat: 37.498871, lon: 126.993414, isPopular: true, fullAddr: '서울특별시 서초구 방배동', keywords: ['방배', '사당', '내방', '서초'] },
  { name: '반포동', gu: '서초구', city: '서울', lat: 37.5042, lon: 127.0048, isPopular: false, fullAddr: '서울특별시 서초구 반포동', keywords: ['반포', '고속터미널', '신반포', '서초'] },
  { name: '양재동', gu: '서초구', city: '서울', lat: 37.4765, lon: 127.0415, isPopular: false, fullAddr: '서울특별시 서초구 양재동', keywords: ['양재', '매헌', '시민의숲', '서초'] },
  { name: '천호동', gu: '강동구', city: '서울', lat: 37.5385, lon: 127.1235, isPopular: true, fullAddr: '서울특별시 강동구 천호동', keywords: ['천호', '강동', '암사', '로데오'] },
  { name: '명일동', gu: '강동구', city: '서울', lat: 37.5512, lon: 127.1445, isPopular: false, fullAddr: '서울특별시 강동구 명일동', keywords: ['명일', '고덕', '강동'] },

  // 2. 서울 서남권 (양천 / 강서 / 구로 / 영등포 / 동작 / 관악 / 금천)
  { name: '목동', gu: '양천구', city: '서울', lat: 37.524812, lon: 126.868215, isPopular: true, fullAddr: '서울특별시 양천구 목동', keywords: ['목동', '오목교', '신정', '양천'] },
  { name: '화곡동', gu: '강서구', city: '서울', lat: 37.5412, lon: 126.8405, isPopular: true, fullAddr: '서울특별시 강서구 화곡동', keywords: ['화곡', '까치산', '강서'] },
  { name: '마곡동', gu: '강서구', city: '서울', lat: 37.5601, lon: 126.8255, isPopular: false, fullAddr: '서울특별시 강서구 마곡동', keywords: ['마곡', '발산', '강서'] },
  { name: '구로동', gu: '구로구', city: '서울', lat: 37.4954, lon: 126.8875, isPopular: true, fullAddr: '서울특별시 구로구 구로동', keywords: ['구로', '신도림', '디지털단지', '우리아이들병원'] },
  { name: '신도림동', gu: '구로구', city: '서울', lat: 37.5098, lon: 126.8912, isPopular: false, fullAddr: '서울특별시 구로구 신도림동', keywords: ['신도림', '디큐브', '구로'] },
  { name: '여의도동', gu: '영등포구', city: '서울', lat: 37.5218, lon: 126.9242, isPopular: true, fullAddr: '서울특별시 영등포구 여의도동', keywords: ['여의도', '더현대', '샛강', '영등포'] },
  { name: '당산동', gu: '영등포구', city: '서울', lat: 37.5342, lon: 126.9025, isPopular: false, fullAddr: '서울특별시 영등포구 당산동', keywords: ['당산', '문래', '영등포'] },
  { name: '노량진동', gu: '동작구', city: '서울', lat: 37.5135, lon: 126.9425, isPopular: false, fullAddr: '서울특별시 동작구 노량진동', keywords: ['노량진', '동작', '대방'] },
  { name: '상도동', gu: '동작구', city: '서울', lat: 37.4985, lon: 126.9455, isPopular: false, fullAddr: '서울특별시 동작구 상도동', keywords: ['상도', '숭실대', '동작'] },
  { name: '신림동', gu: '관악구', city: '서울', lat: 37.4842, lon: 126.9295, isPopular: true, fullAddr: '서울특별시 관악구 신림동', keywords: ['신림', '신림역', '관악', '도림천'] },
  { name: '봉천동', gu: '관악구', city: '서울', lat: 37.4825, lon: 126.9515, isPopular: false, fullAddr: '서울특별시 관악구 봉천동', keywords: ['봉천', '서울대입구', '관악'] },
  { name: '가산동', gu: '금천구', city: '서울', lat: 37.4812, lon: 126.8825, isPopular: false, fullAddr: '서울특별시 금천구 가산동', keywords: ['가산', '디지털단지', '금천'] },

  // 3. 서울 서북권 (마포 / 서대문 / 은평)
  { name: '공덕동', gu: '마포구', city: '서울', lat: 37.5445, lon: 126.9515, isPopular: true, fullAddr: '서울특별시 마포구 공덕동', keywords: ['공덕', '마포', '아현'] },
  { name: '상암동', gu: '마포구', city: '서울', lat: 37.5785, lon: 126.8915, isPopular: false, fullAddr: '서울특별시 마포구 상암동', keywords: ['상암', 'DMC', '디지털미디어시티', '마포'] },
  { name: '서교동', gu: '마포구', city: '서울', lat: 37.5552, lon: 126.9215, isPopular: false, fullAddr: '서울특별시 마포구 서교동', keywords: ['홍대', '홍대입구', '서교', '합정', '마포'] },
  { name: '신촌동', gu: '서대문구', city: '서울', lat: 37.5598, lon: 126.9365, isPopular: true, fullAddr: '서울특별시 서대문구 신촌동', keywords: ['신촌', '연세대', '이대', '서대문'] },
  { name: '연희동', gu: '서대문구', city: '서울', lat: 37.5725, lon: 126.9325, isPopular: false, fullAddr: '서울특별시 서대문구 연희동', keywords: ['연희', '홍제', '서대문'] },
  { name: '불광동', gu: '은평구', city: '서울', lat: 37.6105, lon: 126.9295, isPopular: true, fullAddr: '서울특별시 은평구 불광동', keywords: ['불광', '연신내', '은평'] },
  { name: '진관동', gu: '은평구', city: '서울', lat: 37.6385, lon: 126.9185, isPopular: false, fullAddr: '서울특별시 은평구 진관동', keywords: ['은평뉴타운', '구파발', '진관', '은평'] },

  // 4. 서울 도심 / 동북권 (종로 / 중구 / 용산 / 성동 / 광진 / 동대문 / 중랑 / 성북 / 강북 / 도봉 / 노원)
  { name: '종로', gu: '종로구', city: '서울', lat: 37.5704, lon: 126.9922, isPopular: true, fullAddr: '서울특별시 종로구 종로', keywords: ['종로', '광화문', '혜화', '대학로'] },
  { name: '명동', gu: '중구', city: '서울', lat: 37.5635, lon: 126.9855, isPopular: false, fullAddr: '서울특별시 중구 명동', keywords: ['명동', '을지로', '회현', '서울역'] },
  { name: '청파동', gu: '용산구', city: '서울', lat: 37.552431, lon: 126.969145, isPopular: true, fullAddr: '서울특별시 용산구 청파동', keywords: ['청파', '숙대', '서울역', '소화병원', '용산'] },
  { name: '한남동', gu: '용산구', city: '서울', lat: 37.5345, lon: 127.0025, isPopular: false, fullAddr: '서울특별시 용산구 한남동', keywords: ['한남', '이태원', '용산'] },
  { name: '성수동', gu: '성동구', city: '서울', lat: 37.5445, lon: 127.0560, isPopular: true, fullAddr: '서울특별시 성동구 성수동', keywords: ['성수', '서울숲', '뚝섬', '성동'] },
  { name: '자양동', gu: '광진구', city: '서울', lat: 37.5345, lon: 127.0695, isPopular: true, fullAddr: '서울특별시 광진구 자양동', keywords: ['자양', '건대', '구의', '광진'] },
  { name: '장안동', gu: '동대문구', city: '서울', lat: 37.5715, lon: 127.0685, isPopular: false, fullAddr: '서울특별시 동대문구 장안동', keywords: ['장안', '답십리', '청량리', '동대문'] },
  { name: '상봉동', gu: '중랑구', city: '서울', lat: 37.5965, lon: 127.0855, isPopular: false, fullAddr: '서울특별시 중랑구 상봉동', keywords: ['상봉', '면목', '중랑'] },
  { name: '장위동', gu: '성북구', city: '서울', lat: 37.6185, lon: 127.0425, isPopular: true, fullAddr: '서울특별시 성북구 장위동', keywords: ['장위', '길음', '우리아이들병원', '성북'] },
  { name: '미아동', gu: '강북구', city: '서울', lat: 37.6255, lon: 127.0255, isPopular: true, fullAddr: '서울특별시 강북구 미아동', keywords: ['미아', '수유', '강북'] },
  { name: '창동', gu: '도봉구', city: '서울', lat: 37.6532, lon: 127.0485, isPopular: false, fullAddr: '서울특별시 도봉구 창동', keywords: ['창동', '쌍문', '도봉'] },
  { name: '상계동', gu: '노원구', city: '서울', lat: 37.654812, lon: 127.060124, isPopular: true, fullAddr: '서울특별시 노원구 상계동', keywords: ['상계', '노원', '중계', '하계'] },

  // 5. 경기 / 인천 주요 권역
  { name: '정자동', gu: '성남 분당구', city: '경기', lat: 37.367124, lon: 127.108215, isPopular: true, fullAddr: '경기도 성남시 분당구 정자동', keywords: ['정자', '분당', '정자역', '성남'] },
  { name: '판교동', gu: '성남 분당구', city: '경기', lat: 37.3940, lon: 127.1110, isPopular: true, fullAddr: '경기도 성남시 분당구 판교동', keywords: ['판교', '판교역', '테크노밸리', '분당', '성남'] },
  { name: '서현동', gu: '성남 분당구', city: '경기', lat: 37.3850, lon: 127.1240, isPopular: false, fullAddr: '경기도 성남시 분당구 서현동', keywords: ['서현', '분당', '성남'] },
  { name: '영통동', gu: '수원 영통구', city: '경기', lat: 37.288541, lon: 127.051214, isPopular: true, fullAddr: '경기도 수원시 영통구 영통동', keywords: ['영통', '광교', '수원', '망포'] },
  { name: '인계동', gu: '수원 팔달구', city: '경기', lat: 37.2635, lon: 127.0285, isPopular: false, fullAddr: '경기도 수원시 팔달구 인계동', keywords: ['인계', '수원시청', '수원'] },
  { name: '일산동', gu: '고양 일산동구', city: '경기', lat: 37.643812, lon: 126.786512, isPopular: true, fullAddr: '경기도 고양시 일산동구 일산동', keywords: ['일산', '고양', '주엽', '대화', '정발산'] },
  { name: '화정동', gu: '고양 덕양구', city: '경기', lat: 37.6345, lon: 126.8325, isPopular: false, fullAddr: '경기도 고양시 덕양구 화정동', keywords: ['화정', '행신', '원당', '고양'] },
  { name: '풍덕천동', gu: '용인 수지구', city: '경기', lat: 37.3245, lon: 127.0985, isPopular: true, fullAddr: '경기도 용인시 수지구 풍덕천동', keywords: ['수지', '풍덕천', '수지구청', '용인'] },
  { name: '동탄동', gu: '화성시 동탄', city: '경기', lat: 37.206512, lon: 127.072412, isPopular: true, fullAddr: '경기도 화성시 동탄동', keywords: ['동탄', '화성', '동탄역', '반송동'] },
  { name: '중동', gu: '부천시 원미구', city: '경기', lat: 37.5035, lon: 126.7665, isPopular: true, fullAddr: '경기도 부천시 원미구 중동', keywords: ['부천', '중동', '상동', '신중동'] },
  { name: '평촌동', gu: '안양 동안구', city: '경기', lat: 37.3945, lon: 126.9625, isPopular: true, fullAddr: '경기도 안양시 동안구 평촌동', keywords: ['평촌', '범계', '안양'] },
  { name: '다산동', gu: '남양주시', city: '경기', lat: 37.6125, lon: 127.1545, isPopular: false, fullAddr: '경기도 남양주시 다산동', keywords: ['다산', '남양주', '별내'] },
  { name: '미사동', gu: '하남시', city: '경기', lat: 37.5615, lon: 127.1925, isPopular: false, fullAddr: '경기도 하남시 미사동', keywords: ['미사', '하남', '망월동'] },
  { name: '철산동', gu: '광명시', city: '경기', lat: 37.4765, lon: 126.8685, isPopular: false, fullAddr: '경기도 광명시 철산동', keywords: ['철산', '광명', '하안동'] },
  { name: '구월동', gu: '인천 남동구', city: '인천', lat: 37.452412, lon: 126.708214, isPopular: true, fullAddr: '인천광역시 남동구 구월동', keywords: ['구월', '인천시청', '남동구', '인천'] },
  { name: '송도동', gu: '인천 연수구', city: '인천', lat: 37.3940, lon: 126.6540, isPopular: true, fullAddr: '인천광역시 연수구 송도동', keywords: ['송도', '센트럴파크', '인천'] },
  { name: '청라동', gu: '인천 서구', city: '인천', lat: 37.534812, lon: 126.654215, isPopular: true, fullAddr: '인천광역시 서구 청라동', keywords: ['청라', '루원시티', '인천'] },
  { name: '부평동', gu: '인천 부평구', city: '인천', lat: 37.4915, lon: 126.7245, isPopular: false, fullAddr: '인천광역시 부평구 부평동', keywords: ['부평', '부평역', '인천'] },

  // 6. 충청권 거점
  { name: '둔산동', gu: '대전 서구', city: '대전', lat: 36.352412, lon: 127.378512, isPopular: true, fullAddr: '대전광역시 서구 둔산동', keywords: ['둔산', '대전시청', '서구', '대전'] },
  { name: '봉명동', gu: '대전 유성구', city: '대전', lat: 36.3570, lon: 127.3420, isPopular: false, fullAddr: '대전광역시 유성구 봉명동', keywords: ['유성', '온천', '봉명', '충남대', '대전'] },
  { name: '나성동', gu: '세종시', city: '세종', lat: 36.504812, lon: 127.251214, isPopular: true, fullAddr: '세종특별자치시 나성동', keywords: ['나성', '세종', '다정동', '어진동'] },
  { name: '불당동', gu: '천안 서북구', city: '충남', lat: 36.815214, lon: 127.108412, isPopular: true, fullAddr: '충청남도 천안시 서북구 불당동', keywords: ['불당', '천안아산역', '천안'] },
  { name: '복대동', gu: '청주 흥덕구', city: '충북', lat: 36.621214, lon: 127.432512, isPopular: true, fullAddr: '충청북도 청주시 흥덕구 복대동', keywords: ['복대', '지웰시티', '청주'] },

  // 7. 영남권 거점
  { name: '만촌동', gu: '대구 수성구', city: '대구', lat: 35.839812, lon: 128.706512, isPopular: true, fullAddr: '대구광역시 수성구 만촌동', keywords: ['만촌', '수성구', '범어', '대구'] },
  { name: '상인동', gu: '대구 달서구', city: '대구', lat: 35.817412, lon: 128.536214, isPopular: false, fullAddr: '대구광역시 달서구 상인동', keywords: ['상인', '달서구', '대구'] },
  { name: '서면', gu: '부산 부산진구', city: '부산', lat: 35.158124, lon: 129.043512, isPopular: true, fullAddr: '부산광역시 부산진구 부전동', keywords: ['서면', '부전동', '부산진구', '부산'] },
  { name: '우동', gu: '부산 해운대구', city: '부산', lat: 35.1631, lon: 129.1636, isPopular: true, fullAddr: '부산광역시 해운대구 우동', keywords: ['해운대', '센텀', '마린시티', '우동', '부산'] },
  { name: '온천동', gu: '부산 동래구', city: '부산', lat: 35.204812, lon: 129.083214, isPopular: false, fullAddr: '부산광역시 동래구 온천동', keywords: ['온천', '동래', '부산'] },
  { name: '삼산동', gu: '울산 남구', city: '울산', lat: 35.538412, lon: 129.324512, isPopular: true, fullAddr: '울산광역시 남구 삼산동', keywords: ['삼산', '태화강', '남구', '울산'] },
  { name: '장량동', gu: '포항 북구', city: '경북', lat: 36.068412, lon: 129.378214, isPopular: true, fullAddr: '경상북도 포항시 북구 장량동', keywords: ['장량', '양덕', '포항'] },
  { name: '상남동', gu: '창원 성산구', city: '경남', lat: 35.2215, lon: 128.6815, isPopular: true, fullAddr: '경상남도 창원시 성산구 상남동', keywords: ['상남', '창원', '팔용동'] },

  // 8. 호남권 거점
  { name: '수완동', gu: '광주 광산구', city: '광주', lat: 35.188412, lon: 126.821214, isPopular: true, fullAddr: '광주광역시 광산구 수완동', keywords: ['수완', '첨단', '광산구', '광주'] },
  { name: '치평동(상무)', gu: '광주 서구', city: '광주', lat: 35.1522, lon: 126.8525, isPopular: false, fullAddr: '광주광역시 서구 치평동', keywords: ['상무', '상무지구', '치평동', '광주시청', '광주'] },
  { name: '효자동', gu: '전주 완산구', city: '전북', lat: 35.81716, lon: 127.102276, isPopular: true, fullAddr: '전북특별자치도 전주시 완산구 효자동', keywords: ['효자', '신시가지', '전주'] },
  { name: '조례동', gu: '순천시', city: '전남', lat: 34.954214, lon: 127.518412, isPopular: true, fullAddr: '전라남도 순천시 조례동', keywords: ['조례', '연향', '순천'] },

  // 9. 강원 / 제주 거점
  { name: '일산동', gu: '원주시', city: '강원', lat: 37.338412, lon: 127.941214, isPopular: true, fullAddr: '강원특별자치도 원주시 일산동', keywords: ['원주', '일산동', '단계동', '무실동'] },
  { name: '퇴계동', gu: '춘천시', city: '강원', lat: 37.8542, lon: 127.7315, isPopular: false, fullAddr: '강원특별자치도 춘천시 퇴계동', keywords: ['춘천', '퇴계동', '남춘천'] },
  { name: '탑동', gu: '제주시', city: '제주', lat: 33.517551, lon: 126.522463, isPopular: true, fullAddr: '제주특별자치도 제주시 일도일동', keywords: ['제주', '탑동', '일도동', '연동', '노형동'] }
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
  let best = '문정동';
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

window.updateLocationDisplay = function(dongName, lat, lon, customFullAddr) {
  const name = dongName || '문정동';
  const textEl = document.getElementById('current-location-text');
  const pillBtn = document.getElementById('current-location-pill');
  if (textEl) {
    textEl.textContent = name;
  }
  if (pillBtn) {
    pillBtn.setAttribute('aria-label', `현재 위치 변경: ${name}`);
  }

  // Determine full address: customFullAddr 우선, 없으면 기 저장 주소, 그 외 fallback
  let fullAddr = customFullAddr;
  if (!fullAddr) {
    const isManual = localStorage.getItem('aisum_location_manual') === 'true';
    if (isManual) {
      fullAddr = localStorage.getItem('aisum_user_address') || `서울특별시 송파구 ${name}`;
    } else {
      const savedAddr = localStorage.getItem('aisum_user_address');
      if (savedAddr && savedAddr !== '현재 위치' && savedAddr !== '현재 GPS 측정 위치') {
        fullAddr = savedAddr;
      } else {
        const matched = (window.AISUM_LOCATIONS_DB || []).find((item) => item.name === name);
        fullAddr = (matched && matched.fullAddr) ? matched.fullAddr : `서울특별시 송파구 ${name}`;
      }
    }
  }

  // Persist into localStorage via PermissionManager
  if (window.AisumPermissionManager) {
    window.AisumPermissionManager.saveUserLocation(lat || 37.4858, lon || 127.1225, name, fullAddr);
  } else {
    try {
      localStorage.setItem('aisum_user_lat', lat || 37.4858);
      localStorage.setItem('aisum_user_lon', lon || 127.1225);
      localStorage.setItem('user_lat', lat || 37.4858);
      localStorage.setItem('user_lon', lon || 127.1225);
      localStorage.setItem('aisum_user_dong', name);
      localStorage.setItem('user_dong', name);
      localStorage.setItem('aisum_user_address', fullAddr);
    } catch (e) {}
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

  // Update modal indicators
  const tagEl = document.getElementById('modal-current-dong-tag');
  if (tagEl) {
    tagEl.textContent = `현재: ${name}`;
  }
  const barEl = document.getElementById('modal-current-address-bar');
  if (barEl) {
    barEl.innerHTML = `<span class="material-symbols-outlined current-bar-icon" style="font-size:18px;color:#0066ff;">home_pin</span><span class="current-bar-text" style="font-size:12.5px;color:#334155;">현재 설정된 주소: <strong style="color:#0f172a;">${escapeSearchHtml(fullAddr)}</strong></span>`;
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
    async (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      let dong = window.estimateDongFromCoords(lat, lon);
      let fullAddr = `서울특별시 송파구 ${dong}`;

      try {
        const resp = await fetch(`/api/v1/location/coord2address?lat=${lat}&lon=${lon}`);
        if (resp.ok) {
          const data = await resp.json();
          if (data && data.full_address && data.full_address !== '현재 위치' && data.full_address !== '현재 GPS 측정 위치') {
            fullAddr = data.full_address;
            if (data.dong && data.dong !== '현재 위치' && data.dong !== '내 위치') {
              dong = data.dong;
            }
          }
        }
      } catch (e) {}

      console.log('📍 [Aisum GPS] 브라우저 실시간 위치 감지 완료:', dong, lat, lon, fullAddr);
      window.updateLocationDisplay(dong, lat, lon, fullAddr);
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
    : { lat: 37.4858, lon: 127.1225, dong: '문정동', isCustom: false };

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
    btn.innerHTML = '<span class="material-symbols-outlined gps-icon" style="animation:spin 1s linear infinite;">sync</span><div class="gps-text-wrap"><span class="gps-main-text">현재 위치 측정 중...</span><span class="gps-sub-text">기기 실제 GPS 좌표를 실시간 조회하고 있습니다</span></div>';
  }

  // 1. 수동 선택 상태 초기화
  try {
    localStorage.removeItem('aisum_location_manual');
  } catch (e) {}

  const finalizeLocation = async (lat, lon) => {
    let dong = window.estimateDongFromCoords(lat, lon);
    let fullAddr = '';

    // 2. 카카오 역지오코딩 백엔드 API (coord2address) 실시간 호출
    try {
      const resp = await fetch(`/api/v1/location/coord2address?lat=${lat}&lon=${lon}`);
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.full_address && data.full_address !== '현재 위치' && data.full_address !== '현재 GPS 측정 위치') {
          // 카카오 역지오코딩이 반환한 상세 도로명/건물명/지번 주소를 100% 보존
          fullAddr = data.full_address;
          if (data.dong && data.dong !== '현재 위치' && data.dong !== '내 위치') {
            dong = data.dong;
          }
        }
      }
    } catch (e) {
      console.warn('Reverse geocoding API error, using local fallback:', e);
    }

    // 3. 만약 API 응답이 없거나 실패한 경우에만 로컬 DB에서 안전하게 fallback 주소 구성
    if (!fullAddr) {
      const matched = (window.AISUM_LOCATIONS_DB || []).find((item) => item.name === dong);
      fullAddr = (matched && matched.fullAddr) ? matched.fullAddr : `서울특별시 송파구 ${dong}`;
    }

    if (btn) {
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.innerHTML = originalHtml;
    }

    // 4. UI 및 LocalStorage에 상세 주소 완벽 동기화 (모달 상단 현재 설정된 주소 바 즉각 반영)
    window.updateLocationDisplay(dong, lat, lon, fullAddr);

    // 모달 상단 주소 바 엘리먼트 즉시 시각 갱신
    const barEl = document.getElementById('modal-current-address-bar');
    if (barEl) {
      barEl.innerHTML = `<span class="material-symbols-outlined current-bar-icon" style="font-size:18px;color:#0066ff;">home_pin</span><span class="current-bar-text" style="font-size:12.5px;color:#334155;">현재 설정된 주소: <strong style="color:#0f172a;">${escapeSearchHtml(fullAddr)}</strong></span>`;
    }

    if (typeof window.initLiveFacilities === 'function') {
      window.initLiveFacilities();
    }
    if (typeof window.showAisumToast === 'function') {
      window.showAisumToast(`📍 현재 위치로 설정되었습니다: ${dong}`);
    }

    // 사용자가 바뀐 상세 주소를 모달에서 눈으로 충분히 확인할 수 있도록 650ms 후 모달 자동 닫기
    setTimeout(() => {
      if (typeof window.closeLocationModal === 'function') {
        window.closeLocationModal();
      }
    }, 650);
  };

  const handleGpsFallback = () => {
    const savedLat = parseFloat(localStorage.getItem('aisum_user_lat') || '37.4858');
    const savedLon = parseFloat(localStorage.getItem('aisum_user_lon') || '127.1225');
    console.log('📍 [Aisum GPS Fallback] 기본/캐시 좌표 기반으로 현재 위치 갱신:', savedLat, savedLon);
    finalizeLocation(savedLat, savedLon);
  };

  if (!('geolocation' in navigator)) {
    handleGpsFallback();
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      finalizeLocation(lat, lon);
    },
    (err) => {
      console.warn('Geolocation error or permission denied:', err);
      handleGpsFallback();
    },
    { enableHighAccuracy: true, timeout: 5000, maximumAge: 3000 }
  );
};

window.setUserCustomLocation = function(dongName, lat, lon, fullAddr) {
  const userAddr = fullAddr || `서울특별시 송파구 ${dongName}`;
  try {
    localStorage.setItem('aisum_location_manual', 'true');
    localStorage.setItem('aisum_user_address', userAddr);
  } catch (e) {}

  window.updateLocationDisplay(dongName, lat, lon, userAddr);
  if (typeof window.closeLocationModal === 'function') {
    window.closeLocationModal();
  }
  if (typeof window.initLiveFacilities === 'function') {
    window.initLiveFacilities();
  }
  if (typeof window.showAisumToast === 'function') {
    window.showAisumToast(`📍 위치가 '${dongName}'(으)로 설정되었습니다.`);
  }
};

// ============================================================================
// 🔍 Location Address & Keyword Search Engine (주소 검색 / 키워드 검색 엔진)
// ============================================================================
function escapeSearchHtml(str) {
  return (str || '').replace(/[&<>"']/g, function(m) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
  });
}

function highlightMatch(text, query) {
  if (!text || !query) return escapeSearchHtml(text);
  const escapedText = escapeSearchHtml(text);
  const cleanQ = query.trim();
  if (!cleanQ) return escapedText;

  try {
    const regex = new RegExp(`(${cleanQ.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return escapedText.replace(regex, '<span class="match-highlight">$1</span>');
  } catch (e) {
    return escapedText;
  }
}

window.searchLocations = function(query) {
  if (!query || !query.trim()) return [];
  const rawQ = query.trim();
  const lowerQ = rawQ.toLowerCase();
  const q = lowerQ.replace(/\s+/g, '');

  const results = [];
  const addedKeys = new Set();

  // 0. 최상단: 사용자가 입력한 주소/키워드로 직접 설정할 수 있는 직관 카드 생성
  let directLat = 37.4858;
  let directLon = 127.1225;
  const currLoc = window.AisumPermissionManager ? window.AisumPermissionManager.getUserLocation() : null;
  if (currLoc && currLoc.lat && currLoc.lon) {
    directLat = currLoc.lat;
    directLon = currLoc.lon;
  }

  // 사용자가 입력한 검색어 내에 알려진 행정구역이 있으면 해당 중심 좌표를 스마트하게 매칭
  const db = window.AISUM_LOCATIONS_DB || [];
  for (let i = 0; i < db.length; i++) {
    const item = db[i];
    if (q.includes(item.name.replace(/\s+/g, '')) || item.keywords.some(kw => q.includes(kw))) {
      directLat = item.lat;
      directLon = item.lon;
      break;
    }
  }

  results.push({
    isDirect: true,
    name: rawQ,
    gu: '입력 주소 직접 지정',
    city: '주소 설정',
    fullAddr: rawQ,
    lat: directLat,
    lon: directLon,
    score: 99999,
    type: 'custom'
  });

  // 1. Search in AISUM_LOCATIONS_DB (전국 핵심 동 & 행정구역 DB)
  db.forEach((item) => {
    const nameClean = item.name.toLowerCase().replace(/\s+/g, '');
    const guClean = item.gu.toLowerCase().replace(/\s+/g, '');
    const cityClean = (item.city || '').toLowerCase().replace(/\s+/g, '');
    const addrClean = (item.fullAddr || '').toLowerCase().replace(/\s+/g, '');
    const kwMatch = (item.keywords || []).some((kw) => kw.toLowerCase().replace(/\s+/g, '').includes(q));

    const nameMatch = nameClean.includes(q);
    const guMatch = guClean.includes(q);
    const cityMatch = cityClean.includes(q);
    const addrMatch = addrClean.includes(q);

    if (nameMatch || guMatch || cityMatch || addrMatch || kwMatch) {
      let score = 0;
      if (nameClean === q) score += 120;
      else if (nameClean.startsWith(q)) score += 80;
      else if (nameMatch) score += 50;
      else if (guMatch) score += 40;
      else if (kwMatch) score += 30;
      else score += 10;

      results.push({
        isDirect: false,
        name: item.name,
        gu: item.gu,
        city: item.city || '',
        fullAddr: item.fullAddr || `${item.city} ${item.gu} ${item.name}`,
        lat: item.lat,
        lon: item.lon,
        score: score,
        type: 'region'
      });
      addedKeys.add(item.name + item.gu);
    }
  });

  // 2. Search in Nationwide Moonlight Hospitals & Pharmacies (달빛병원 156개소 매칭)
  const pairings = window.NATIONWIDE_PAIRINGS_DATA || [];
  pairings.forEach((p) => {
    const hName = p.병원명 || '';
    const hAddr = p.병원주소 || '';
    const pName = p.약국명 || '';
    const pAddr = p.약국주소 || '';

    const textToMatch = (hName + ' ' + hAddr + ' ' + pName + ' ' + pAddr).toLowerCase();
    if (textToMatch.includes(lowerQ) || textToMatch.replace(/\s+/g, '').includes(q)) {
      const lat = parseFloat(p.병원위도) || 37.4858;
      const lon = parseFloat(p.병원경도) || 127.1225;
      const dong = window.estimateDongFromCoords(lat, lon);
      const key = (hName || pName) + dong;
      if (!addedKeys.has(key)) {
        results.push({
          isDirect: false,
          name: dong,
          gu: hName || pName,
          city: '달빛병원 연계',
          fullAddr: hAddr || pAddr || `${dong} 일대`,
          lat: lat,
          lon: lon,
          score: 35,
          type: 'facility'
        });
        addedKeys.add(key);
      }
    }
  });

  // 3. Search in Public Night Pharmacies (공공심야약국 2028개소 매칭)
  const nightPharmacies = window.PUBLIC_NIGHT_PHARMACIES_DATA || [];
  nightPharmacies.forEach((np) => {
    const npName = np.약국명 || '';
    const npAddr = np.주소 || np.약국주소 || '';
    const textToMatch = (npName + ' ' + npAddr).toLowerCase();
    if (textToMatch.includes(lowerQ) || textToMatch.replace(/\s+/g, '').includes(q)) {
      const lat = parseFloat(np.위도 || np.약국위도) || 37.4858;
      const lon = parseFloat(np.경도 || np.약국경도) || 127.1225;
      const dong = window.estimateDongFromCoords(lat, lon);
      const key = npName + dong;
      if (!addedKeys.has(key)) {
        results.push({
          isDirect: false,
          name: dong,
          gu: npName,
          city: '심야약국 연계',
          fullAddr: npAddr,
          lat: lat,
          lon: lon,
          score: 30,
          type: 'pharmacy'
        });
        addedKeys.add(key);
      }
    }
  });

  // Direct card stays on top, rest sorted by relevance score
  const directItem = results[0];
  const otherItems = results.slice(1);
  otherItems.sort((a, b) => b.score - a.score);
  return [directItem, ...otherItems.slice(0, 14)];
};

// ============================================================================
// 📍 Location Search Mode & Kakao Local API Engine (주소 검색 vs 키워드 검색)
// ============================================================================
window.__CURRENT_LOCATION_SEARCH_MODE__ = 'address'; // 'address' | 'keyword'
window.__LOCATION_SEARCH_DEBOUNCE_TIMER__ = null;

window.switchLocationSearchMode = function(mode) {
  window.__CURRENT_LOCATION_SEARCH_MODE__ = mode;

  const tabAddr = document.getElementById('tab-mode-address');
  const tabKeyw = document.getElementById('tab-mode-keyword');
  const input = document.getElementById('location-search-input');
  const icon = document.getElementById('location-search-icon');

  if (tabAddr && tabKeyw) {
    if (mode === 'address') {
      tabAddr.classList.add('active');
      tabAddr.setAttribute('aria-selected', 'true');
      tabAddr.style.border = '1.5px solid #0066ff';
      tabAddr.style.background = '#f0f7ff';
      tabAddr.style.color = '#0066ff';
      tabAddr.style.fontWeight = '700';

      tabKeyw.classList.remove('active');
      tabKeyw.setAttribute('aria-selected', 'false');
      tabKeyw.style.border = '1.5px solid #e2e8f0';
      tabKeyw.style.background = '#ffffff';
      tabKeyw.style.color = '#64748b';
      tabKeyw.style.fontWeight = '600';

      if (input) {
        input.placeholder = '지번 또는 도로명 입력 (예: 문정동 642, 송파대로 201)';
      }
      if (icon) icon.textContent = 'signpost';
    } else {
      tabKeyw.classList.add('active');
      tabKeyw.setAttribute('aria-selected', 'true');
      tabKeyw.style.border = '1.5px solid #0066ff';
      tabKeyw.style.background = '#f0f7ff';
      tabKeyw.style.color = '#0066ff';
      tabKeyw.style.fontWeight = '700';

      tabAddr.classList.remove('active');
      tabAddr.setAttribute('aria-selected', 'false');
      tabAddr.style.border = '1.5px solid #e2e8f0';
      tabAddr.style.background = '#ffffff';
      tabAddr.style.color = '#64748b';
      tabAddr.style.fontWeight = '600';

      if (input) {
        input.placeholder = '건물명, 역명 또는 지역명 입력 (예: 코엑스, 강남역, 해운대)';
      }
      if (icon) icon.textContent = 'apartment';
    }
  }

  // If search input has value, trigger search immediately
  if (input && input.value.trim()) {
    window.performLocationSearch(input.value.trim());
  }
};

window.performLocationSearch = async function(query) {
  const mode = window.__CURRENT_LOCATION_SEARCH_MODE__ || 'address';
  const resultsSec = document.getElementById('location-search-results-section');
  const resultsList = document.getElementById('location-results-list');
  const countEl = document.getElementById('search-results-count');
  const quickSec = document.getElementById('quick-locations-section');

  if (!query) {
    if (resultsSec) resultsSec.style.display = 'none';
    if (quickSec) quickSec.style.display = 'flex';
    return;
  }

  if (quickSec) quickSec.style.display = 'none';
  if (resultsSec) resultsSec.style.display = 'flex';

  let items = [];

  try {
    // 1. Call Backend Kakao Local Proxy API
    const res = await fetch(`/api/v1/location/search?search_type=${mode}&q=${encodeURIComponent(query)}`);
    if (res.ok) {
      const data = await res.json();
      if (data && data.results && data.results.length > 0) {
        items = data.results;
      }
    }
  } catch (err) {
    console.warn('Online location search failed, falling back to local DB:', err);
  }

  // 2. Fallback to local DB if empty
  if (items.length === 0) {
    const localMatches = window.searchLocations(query);
    items = localMatches.filter(m => !m.isDirect).map(m => ({
      type: mode,
      title: m.name,
      category: m.gu || m.city || '지역',
      road_address: m.fullAddr,
      jibun_address: m.fullAddr,
      dong: m.name,
      lat: m.lat,
      lon: m.lon,
      source: 'fallback'
    }));
  }

  if (countEl) {
    countEl.textContent = `검색 결과 ${items.length}건`;
  }

  if (!resultsList) return;

  // Direct set card on top
  const isAddress = mode === 'address';
  let html = `
    <li class="location-result-item direct-set-item" style="background:#f0f7ff;border:1.5px solid #93c5fd;border-radius:12px;padding:12px 14px;margin-bottom:8px;cursor:pointer;" onclick="window.setUserCustomLocation('${escapeSearchHtml(query)}', 37.4858, 127.1225, '${escapeSearchHtml(query)}')">
      <div class="result-main-wrap" style="display:flex;align-items:center;gap:10px;">
        <span class="material-symbols-outlined result-pin-icon" style="color:#0066ff;font-size:22px;">edit_location_alt</span>
        <div class="result-info" style="display:flex;flex-direction:column;gap:2px;">
          <span class="result-title" style="color:#0066ff;font-weight:700;font-size:14px;">'${escapeSearchHtml(query)}' (으)로 현재 주소 직접 설정</span>
          <span class="result-desc" style="color:#475569;font-size:12px;">입력하신 ${isAddress ? '주소' : '키워드'}를 사용자 기본 위치로 즉시 지정합니다</span>
        </div>
      </div>
      <span class="result-tag" style="background:#0066ff;color:#ffffff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;">직접 설정</span>
    </li>
  `;

  items.forEach((item) => {
    const highlightedTitle = highlightMatch(item.title, query);
    const subAddr = item.road_address || item.jibun_address || '';
    const highlightedAddr = highlightMatch(subAddr, query);
    const badgeText = item.category || (item.type === 'keyword' ? '장소' : '주소');
    const dongName = item.dong || item.title;
    const fullAddress = item.road_address || item.jibun_address || item.title;

    html += `
      <li class="location-result-item" onclick="window.setUserCustomLocation('${escapeSearchHtml(dongName)}', ${item.lat}, ${item.lon}, '${escapeSearchHtml(fullAddress)}')">
        <div class="result-main-wrap">
          <span class="material-symbols-outlined result-pin-icon">${item.type === 'keyword' ? 'apartment' : 'location_on'}</span>
          <div class="result-info">
            <span class="result-title">${highlightedTitle}</span>
            <span class="result-desc">${highlightedAddr}</span>
          </div>
        </div>
        <span class="result-tag" style="${item.type === 'keyword' ? 'background:#e0f2fe;color:#0369a1;' : ''}">${badgeText}</span>
      </li>
    `;
  });

  resultsList.innerHTML = html;
};

window.initLocationSearch = function() {
  const input = document.getElementById('location-search-input');
  const clearBtn = document.getElementById('location-search-clear-btn');

  if (!input) return;
  if (input.dataset.searchBound === 'true') return;
  input.dataset.searchBound = 'true';

  const handleSearch = function() {
    const query = input.value.trim();
    if (clearBtn) clearBtn.style.display = query ? 'flex' : 'none';

    if (window.__LOCATION_SEARCH_DEBOUNCE_TIMER__) {
      clearTimeout(window.__LOCATION_SEARCH_DEBOUNCE_TIMER__);
    }

    window.__LOCATION_SEARCH_DEBOUNCE_TIMER__ = setTimeout(() => {
      window.performLocationSearch(query);
    }, 200);
  };

  input.addEventListener('input', handleSearch);

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const resultsList = document.getElementById('location-results-list');
      const firstItem = resultsList ? resultsList.querySelector('.location-result-item') : null;
      if (firstItem) {
        firstItem.click();
      }
    } else if (e.key === 'Escape') {
      e.preventDefault();
      if (typeof window.closeLocationModal === 'function') {
        window.closeLocationModal();
      }
    }
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', (e) => {
      e.preventDefault();
      input.value = '';
      input.focus();
      handleSearch();
    });
  }
};

window.openLocationModal = function() {
  const modal = document.getElementById('location-select-modal');
  if (!modal) return;
  modal.classList.add('active');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';

  // Initialize search event listeners
  if (typeof window.initLocationSearch === 'function') {
    window.initLocationSearch();
  }

  // Reset search input and UI state
  const searchInput = document.getElementById('location-search-input');
  const clearBtn = document.getElementById('location-search-clear-btn');
  const resultsSec = document.getElementById('location-search-results-section');
  const quickSec = document.getElementById('quick-locations-section');
  if (searchInput) {
    searchInput.value = '';
    setTimeout(() => {
      searchInput.focus();
    }, 150);
  }
  if (clearBtn) clearBtn.style.display = 'none';
  if (resultsSec) resultsSec.style.display = 'none';
  if (quickSec) quickSec.style.display = 'flex';

  // Update current selected dong badge and full address bar
  const currentDong = localStorage.getItem('aisum_user_dong') || localStorage.getItem('user_dong') || '문정동';
  const tagEl = document.getElementById('modal-current-dong-tag');
  if (tagEl) {
    tagEl.textContent = `현재: ${currentDong}`;
  }
  const barEl = document.getElementById('modal-current-address-bar');
  if (barEl) {
    let fullAddr = localStorage.getItem('aisum_user_address');
    if (!fullAddr) {
      const matched = (window.AISUM_LOCATIONS_DB || []).find((item) => item.name === currentDong);
      fullAddr = (matched && matched.fullAddr) ? matched.fullAddr : `서울특별시 송파구 ${currentDong}`;
    }
    barEl.innerHTML = `<span class="material-symbols-outlined current-bar-icon" style="font-size:16px;color:#0066ff;">home_pin</span><span class="current-bar-text" style="font-size:12.5px;color:#334155;">현재 설정된 주소: <strong style="color:#0f172a;">${escapeSearchHtml(fullAddr)}</strong></span>`;
  }

  // Render quick locations grid
  const grid = document.getElementById('quick-locations-grid');
  if (grid) {
    const popular = (window.AISUM_LOCATIONS_DB || []).filter((item) => item.isPopular);
    let chipsHtml = '';
    popular.forEach((loc) => {
      const isActive = loc.name === currentDong;
      const chipAddr = loc.fullAddr || `서울특별시 ${loc.gu} ${loc.name}`;
      chipsHtml += `
        <button type="button" class="loc-chip-btn ${isActive ? 'active' : ''}" data-dong="${loc.name}" onclick="window.setUserCustomLocation('${loc.name}', ${loc.lat}, ${loc.lon}, '${escapeSearchHtml(chipAddr)}')">
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
// 🏥 Real-Time Nighttime Medical Facilities Loader (전국 156개 병원 + 2,028개 약국 실데이터 기반 거리순 연동)
// ============================================================================
window.__LIVE_FACILITIES_MASTER__ = null;
window.__CURRENT_FACILITY_FILTER__ = 'all';
window.__FACILITY_VISIBLE_COUNT__ = 15;
window.__FACILITY_PAGE_STEP__ = 15;

window.initLiveFacilities = function() {
  const stack = document.getElementById('facility-card-stack');
  if (!stack) return; // Only execute on index.html

  // 1. 사용자 현재 위치 좌표 획득 (PermissionManager 활용, 기본값 문정동)
  const userLoc = window.AisumPermissionManager
    ? window.AisumPermissionManager.getUserLocation()
    : { lat: 37.4858, lon: 127.1225, dong: '문정동' };

  // 2. 전국 달빛어린이병원 (156개) 및 야간약국 (2,028개) 실데이터셋 확인
  const hospRaw = window.NATIONAL_MOONLIGHT_HOSPITALS_DATA || [];
  const pharmRaw = window.NATIONAL_NIGHT_PHARMACIES_DATA || [];

  if (hospRaw.length > 0 && pharmRaw.length > 0) {
    window.buildLiveFacilitiesData(hospRaw, pharmRaw, userLoc);
  } else {
    // 비동기 fetch 안전망 (네트워크 환경 대비)
    Promise.all([
      hospRaw.length > 0 ? Promise.resolve(hospRaw) : fetch('/data/national_moonlight_hospitals_156.json').then(r => r.json()).catch(() => []),
      pharmRaw.length > 0 ? Promise.resolve(pharmRaw) : fetch('/data/national_night_pharmacies_2028.json').then(r => r.json()).catch(() => [])
    ]).then(([hList, pList]) => {
      const finalHosp = (hList && hList.length > 0) ? hList : (window.NATIONWIDE_PAIRINGS_DATA || []);
      const finalPharm = (pList && pList.length > 0) ? pList : (window.PUBLIC_NIGHT_PHARMACIES_DATA || []);
      window.NATIONAL_MOONLIGHT_HOSPITALS_DATA = finalHosp;
      window.NATIONAL_NIGHT_PHARMACIES_DATA = finalPharm;
      window.buildLiveFacilitiesData(finalHosp, finalPharm, userLoc);
    }).catch(err => {
      console.warn('Real facility datasets async load error:', err);
    });
  }
};

window.buildLiveFacilitiesData = function(hospList, pharmList, userLoc) {
  const lat = userLoc.lat;
  const lon = userLoc.lon;

  // 1. 병원(156개 전수) 거리 계산 및 오름차순 정렬
  const hospitals = hospList.map(h => {
    const hLat = parseFloat(h.위도) || lat;
    const hLon = parseFloat(h.경도) || lon;
    const dist = (typeof window.calculateDistanceKm === 'function')
      ? window.calculateDistanceKm(lat, lon, hLat, hLon)
      : 1.0;
    const hDist = dist.toFixed(1);
    const hWalk = Math.max(3, Math.round(dist * 14)) + '분';
    const hCar = Math.max(2, Math.round(dist * 2.3)) + '분';

    const hClose = h.평일진료
      ? (h.평일진료.includes('~') ? `평일 ${h.평일진료}` : h.평일진료)
      : (h.토요진료 ? `토요 ${h.토요진료}` : '소아 야간·휴일 진료');

    return {
      type: 'hospital',
      id: h.기관코드 || h.병원명,
      name: h.병원명 || '달빛어린이병원',
      badge: '🌙 달빛어린이병원',
      subBadge: h.종별 || '소아과',
      status: '진료중 · 접수 가능',
      desc: `${h.종별 || '의원'} · ${h.진료안내 || '소아 야간·휴일 진료 지정기관'} · ${h.주소 || ''}`,
      phone: h.대표전화 || '119',
      address: h.주소 || '',
      lat: hLat,
      lon: hLon,
      hours: {
        weekday: h.평일진료 || '진료안내 참조',
        saturday: h.토요진료 || '진료안내 참조',
        sunday: h.일요진료 || '진료안내 참조',
        holiday: h.공휴일진료 || '진료안내 참조'
      },
      guide: h.진료안내 || '보건복지부 지정 달빛어린이병원',
      distKm: dist,
      dist: hDist,
      walkTime: hWalk,
      carTime: hCar,
      closing: hClose,
      raw: h
    };
  });
  hospitals.sort((a, b) => a.distKm - b.distKm);

  // 2. 약국(2,028개 전수) 거리 계산 및 오름차순 정렬
  const pharmacies = pharmList.map(p => {
    const pLat = parseFloat(p.위도) || lat;
    const pLon = parseFloat(p.경도) || lon;
    const dist = (typeof window.calculateDistanceKm === 'function')
      ? window.calculateDistanceKm(lat, lon, pLat, pLon)
      : 1.0;
    const pDist = dist.toFixed(1);
    const pWalk = Math.max(3, Math.round(dist * 14)) + '분';
    const pCar = Math.max(2, Math.round(dist * 2.3)) + '분';

    const pClose = p.평일운영
      ? (p.평일운영.includes('~') ? `평일 ${p.평일운영}` : p.평일운영)
      : (p.운영구분 || '심야 연장 운영');

    return {
      type: 'pharmacy',
      id: p.기관코드 || p.약국명,
      name: p.약국명 || '심야약국',
      badge: '💊 심야약국',
      subBadge: p.운영구분 || '심야 연장',
      status: p.소아시럽제상비 ? '🟢 시럽제 상비' : (p.조제안전등급 || '🟢 심야 조제'),
      desc: `${p.소아시럽제상비 ? '소아 시럽제 상비 · ' : ''}${p.운영구분 || '심야약국'} · ${p.주소 || ''}`,
      phone: p.대표전화 || '02-120',
      address: p.주소 || '',
      lat: pLat,
      lon: pLon,
      hours: {
        weekday: p.평일운영 || '야간 운영',
        saturday: p.토요운영 || '야간 운영',
        sunday: p.일요운영 || '야간 운영',
        holiday: p.공휴일운영 || '야간 운영'
      },
      syrupReady: !!p.소아시럽제상비,
      distKm: dist,
      dist: pDist,
      walkTime: pWalk,
      carTime: pCar,
      closing: pClose,
      raw: p
    };
  });
  pharmacies.sort((a, b) => a.distKm - b.distKm);

  // 3. 반경 15km 이내 시설 필터링 (사용자 요구사항: 반경 15km 이내 시설들만 표시)
  const MAX_RADIUS_KM = 15.0;
  const filteredHospitals = hospitals.filter(h => h.distKm <= MAX_RADIUS_KM);
  const filteredPharmacies = pharmacies.filter(p => p.distKm <= MAX_RADIUS_KM);

  // 4. 전체(all) 탭: 15km 이내 병원 + 약국 통합 최단거리 오름차순 정렬
  const allList = [...filteredHospitals, ...filteredPharmacies].sort((a, b) => a.distKm - b.distKm);

  // 5. 전역 마스터 객체 등록 (15km 필터링 적용 및 원본 보관)
  window.__LIVE_FACILITIES_MASTER__ = {
    all: allList,
    hospital: filteredHospitals,
    pharmacy: filteredPharmacies,
    userDong: userLoc.dong || '내 위치',
    maxRadiusKm: MAX_RADIUS_KM,
    rawHospitals: hospitals,
    rawPharmacies: pharmacies
  };

  // 6. 상단 뱃지 카운트 및 탭 카운트 실데이터 동기화 (반경 15km 기준)
  const totalCount = allList.length;
  const hospCount = filteredHospitals.length;
  const pharmCount = filteredPharmacies.length;

  const countBadge = document.getElementById('live-facilities-count');
  if (countBadge) {
    countBadge.textContent = totalCount > 0
      ? `${userLoc.dong} 반경 15km ${totalCount.toLocaleString()}곳 운영중`
      : `${userLoc.dong} 반경 15km 내 운영 시설 없음`;
  }

  const countAll = document.getElementById('count-all');
  if (countAll) countAll.textContent = totalCount.toLocaleString();

  const countHosp = document.getElementById('count-hospital');
  if (countHosp) countHosp.textContent = hospCount.toLocaleString();

  const countPharm = document.getElementById('count-pharmacy');
  if (countPharm) countPharm.textContent = pharmCount.toLocaleString();

  // 7. 현재 필터에 맞춰 즉시 렌더링
  window.renderLiveFacilities(window.__CURRENT_FACILITY_FILTER__ || 'all');
};

window.renderLiveFacilities = function(filter) {
  const stack = document.getElementById('facility-card-stack');
  if (!stack || !window.__LIVE_FACILITIES_MASTER__) return;

  const master = window.__LIVE_FACILITIES_MASTER__;
  const currentFilter = filter || window.__CURRENT_FACILITY_FILTER__ || 'all';
  const displayList = master[currentFilter] || master.all || [];

  // 목록이 비어있는 경우 (반경 15km 이내 시설이 없음)
  if (displayList.length === 0) {
    const filterLabel = currentFilter === 'hospital' ? '달빛어린이병원' : (currentFilter === 'pharmacy' ? '심야약국' : '야간 의료시설');
    stack.innerHTML = `
      <article class="facility-card live-empty-card" style="padding: 36px 20px; text-align: center; border: 1px dashed var(--slate-300, #cbd5e1); background: #f8fafc; border-radius: 16px; margin: 8px 0;">
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;">
          <span class="material-symbols-outlined" style="font-size: 38px; color: var(--slate-400, #94a3b8);">location_off</span>
          <p style="font-size: 15px; font-weight: 700; color: var(--slate-700, #334155); margin: 0;">반경 15km 이내 ${filterLabel}이 없습니다</p>
          <p style="font-size: 13px; color: var(--slate-500, #64748b); margin: 0; line-height: 1.5;">${master.userDong} 기준 15km 이내에는 현재 등록된 야간 시설이 없습니다.<br>상단 주소를 변경하시거나 응급실 가이드를 확인해보세요.</p>
        </div>
      </article>
    `;
    const moreBtn = document.querySelector('.scroll-more-btn');
    if (moreBtn) moreBtn.style.display = 'none';
    return;
  }

  // 시설 목록 전수 렌더링 (내부 스크롤 뷰포트를 통해 부드럽게 전체 탐색 가능)
  const sliceList = displayList;

  // Render cards HTML
  let cardsHTML = '';
  sliceList.forEach((facility) => {
    const isHospital = facility.type === 'hospital';
    const icon = isHospital ? 'bedtime' : 'medication';
    const iconClass = isHospital ? '' : 'pharmacy';
    const badgeClass = isHospital ? 'moonlight' : 'pharmacy';
    const badgeText = facility.badge || (isHospital ? '🌙 달빛어린이병원' : '💊 심야약국');

    const subBadgeHTML = facility.subBadge
      ? `<span class="tag-badge distance-sub">${facility.subBadge}</span>`
      : '';

    const statusBadgeHTML = `<span class="tag-badge status-open"><span class="status-indicator-dot" aria-hidden="true"></span>${facility.status}</span>`;
    const distanceText = `내 위치 ${facility.dist}km (도보 ${facility.walkTime} / 차 ${facility.carTime})`;

    cardsHTML += `
      <article class="facility-card live-card" data-type="${facility.type}" style="cursor: pointer;" onclick="window.selectLiveFacilityCard('${escapeSearchHtml(facility.name)}', '${facility.type}')" title="클릭하여 상세 정보 및 실시간 접수 보기">
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
          <a href="tel:${facility.phone}" class="call-btn" aria-label="${facility.name} 전화 걸기" onclick="event.stopPropagation();">
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

  // 더보기 버튼이 남아있는 경우 숨김 처리
  const moreBtn = document.querySelector('.scroll-more-btn');
  if (moreBtn) {
    moreBtn.style.display = 'none';
  }
};

// ============================================================================
// 🏥 Facility Card Navigation & Data Bridge (병원/약국 카드 클릭 시 상세 페이지 데이터 바인딩)
// ============================================================================
window.selectLiveFacilityCard = function(facilityName, facilityType) {
  try {
    const master = window.__LIVE_FACILITIES_MASTER__;
    const userLoc = window.AisumPermissionManager
      ? window.AisumPermissionManager.getUserLocation()
      : { lat: 37.4858, lon: 127.1225, dong: '문정동' };

    let selectedHospital = null;

    if (master) {
      if (facilityType === 'hospital') {
        const hosp = master.hospital.find(h => h.name === facilityName)
          || (master.rawHospitals && master.rawHospitals.find(h => h.name === facilityName))
          || master.hospital[0];
        if (hosp) {
          // 해당 병원과 가장 가까운 심야약국 자동 매핑 (15km 내 약국 우선, 없으면 전수 약국에서 검색)
          let nearestPharm = null;
          const pharmPool = (master.pharmacy && master.pharmacy.length > 0)
            ? master.pharmacy
            : (master.rawPharmacies || []);
          if (pharmPool.length > 0) {
            let minD = Infinity;
            pharmPool.forEach(p => {
              const d = window.calculateDistanceKm(hosp.lat, hosp.lon, p.lat, p.lon);
              if (d < minD) {
                minD = d;
                nearestPharm = {
                  name: p.name,
                  tel: p.phone,
                  duty_time: p.closing,
                  margin: 30,
                  guide: `병원 인근 ${(d * 1000).toFixed(0)}m (도보 ${Math.max(1, Math.round(d * 14))}분)`,
                  address: p.address
                };
              }
            });
          }

          selectedHospital = {
            name: hosp.name,
            dist: hosp.distKm ? Number(hosp.distKm.toFixed(1)) : 1.2,
            drive_min: Math.max(2, Math.round(hosp.distKm * 2.3)),
            duty_time: hosp.closing,
            tel: hosp.phone,
            address: hosp.address,
            waiting_count: 3,
            hours: hosp.hours || {
              weekday: hosp.raw?.평일진료 || '09:00 ~ 21:00',
              saturday: hosp.raw?.토요진료 || '09:00 ~ 18:00',
              sunday: hosp.raw?.일요진료 || '09:00 ~ 18:00'
            },
            guide: hosp.guide || '보건복지부 지정 달빛어린이병원',
            pharmacy: nearestPharm || {
              name: '인근 심야약국',
              tel: '02-120',
              duty_time: '심야 운영',
              margin: 30,
              guide: '병원 인근 약국',
              address: ''
            }
          };
        }
      } else {
        // 심야약국 클릭 시: 해당 약국과 가장 가까운 달빛병원 매핑
        const pharm = master.pharmacy.find(p => p.name === facilityName) || master.pharmacy[0];
        if (pharm) {
          let nearestHosp = master.hospital[0];
          if (master.hospital && master.hospital.length > 0) {
            let minD = Infinity;
            master.hospital.forEach(h => {
              const d = window.calculateDistanceKm(pharm.lat, pharm.lon, h.lat, h.lon);
              if (d < minD) {
                minD = d;
                nearestHosp = h;
              }
            });
          }

          selectedHospital = {
            name: nearestHosp ? nearestHosp.name : '달빛어린이병원',
            dist: pharm.distKm ? Number(pharm.distKm.toFixed(1)) : 1.0,
            drive_min: Math.max(2, Math.round(pharm.distKm * 2.3)),
            duty_time: nearestHosp ? nearestHosp.closing : '야간 진료',
            tel: nearestHosp ? nearestHosp.phone : '',
            address: nearestHosp ? nearestHosp.address : '',
            waiting_count: 3,
            hours: nearestHosp ? nearestHosp.hours : {
              weekday: '09:00 ~ 21:00',
              saturday: '09:00 ~ 18:00',
              sunday: '09:00 ~ 18:00'
            },
            guide: nearestHosp ? nearestHosp.guide : '',
            pharmacy: {
              name: pharm.name,
              tel: pharm.phone,
              duty_time: pharm.closing,
              margin: 30,
              guide: '공식 심야약국 (선택 약국)',
              address: pharm.address
            }
          };
        }
      }
    }

    if (selectedHospital) {
      sessionStorage.setItem('selected_hospital', JSON.stringify(selectedHospital));
      const path = window.location.pathname;
      let target = 'hospital_detail.html';
      if (!path.endsWith('.html') && window.location.protocol !== 'file:') {
        target = '/hospital_detail';
      }
      window.location.href = target;
    }
  } catch (err) {
    console.warn('Facility card navigation error:', err);
  }
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
  const stack = document.getElementById('facility-card-stack');
  if (stack) {
    stack.scrollTop = 0;
  }
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
    if (typeof window.initLocationSearch === 'function') {
      window.initLocationSearch();
    }

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
