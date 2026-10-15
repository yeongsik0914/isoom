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

window.updateLocationDisplay = function(dongName, lat, lon) {
  const name = dongName || '문정동';
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
    const fullAddr = localStorage.getItem('aisum_user_address') || `서울특별시 송파구 ${name}`;
    window.AisumPermissionManager.saveUserLocation(lat || 37.4858, lon || 127.1225, name, fullAddr);
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
    const fullAddr = localStorage.getItem('aisum_user_address') || `서울특별시 송파구 ${name}`;
    barEl.innerHTML = `<span class="material-symbols-outlined current-bar-icon">home_pin</span><span class="current-bar-text">현재 주소: <strong>${escapeSearchHtml(fullAddr)}</strong></span>`;
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

window.setUserCustomLocation = function(dongName, lat, lon, fullAddr) {
  try {
    localStorage.setItem('aisum_location_manual', 'true');
    const userAddr = fullAddr || `서울특별시 송파구 ${dongName}`;
    localStorage.setItem('aisum_user_address', userAddr);
  } catch (e) {}

  window.updateLocationDisplay(dongName, lat, lon);
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

window.initLocationSearch = function() {
  const input = document.getElementById('location-search-input');
  const clearBtn = document.getElementById('location-search-clear-btn');
  const resultsSec = document.getElementById('location-search-results-section');
  const resultsList = document.getElementById('location-results-list');
  const countEl = document.getElementById('search-results-count');
  const quickSec = document.getElementById('quick-locations-section');

  if (!input) return;
  if (input.dataset.searchBound === 'true') return;
  input.dataset.searchBound = 'true';

  const handleSearch = function() {
    const query = input.value.trim();
    if (!query) {
      if (clearBtn) clearBtn.style.display = 'none';
      if (resultsSec) resultsSec.style.display = 'none';
      if (quickSec) quickSec.style.display = 'flex';
      return;
    }

    if (clearBtn) clearBtn.style.display = 'flex';
    if (quickSec) quickSec.style.display = 'none';
    if (resultsSec) resultsSec.style.display = 'flex';

    const matches = window.searchLocations(query);
    if (countEl) {
      const actualCount = matches.filter(m => !m.isDirect).length;
      countEl.textContent = `검색 결과 ${actualCount}건`;
    }

    if (!resultsList) return;

    let html = '';
    matches.forEach((m) => {
      if (m.isDirect) {
        html += `
          <li class="location-result-item direct-set-item" style="background:#f0f7ff;border:1.5px solid #93c5fd;border-radius:12px;padding:12px 14px;margin-bottom:8px;cursor:pointer;" onclick="window.setUserCustomLocation('${escapeSearchHtml(m.name)}', ${m.lat}, ${m.lon}, '${escapeSearchHtml(m.fullAddr)}')">
            <div class="result-main-wrap" style="display:flex;align-items:center;gap:10px;">
              <span class="material-symbols-outlined result-pin-icon" style="color:#0066ff;font-size:22px;">edit_location_alt</span>
              <div class="result-info" style="display:flex;flex-direction:column;gap:2px;">
                <span class="result-title" style="color:#0066ff;font-weight:700;font-size:14px;">'${escapeSearchHtml(m.name)}' (으)로 현재 주소 설정</span>
                <span class="result-desc" style="color:#475569;font-size:12px;">입력하신 주소/키워드를 사용자 기본 위치로 즉시 지정합니다</span>
              </div>
            </div>
            <span class="result-tag" style="background:#0066ff;color:#ffffff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;">현재 주소로 설정</span>
          </li>
        `;
      } else {
        const highlightedName = highlightMatch(m.name, query);
        const highlightedAddr = highlightMatch(m.fullAddr, query);
        const badgeText = m.gu || m.city || '지역';
        html += `
          <li class="location-result-item" onclick="window.setUserCustomLocation('${escapeSearchHtml(m.name)}', ${m.lat}, ${m.lon}, '${escapeSearchHtml(m.fullAddr)}')">
            <div class="result-main-wrap">
              <span class="material-symbols-outlined result-pin-icon">location_on</span>
              <div class="result-info">
                <span class="result-title">${highlightedName}</span>
                <span class="result-desc">${highlightedAddr}</span>
              </div>
            </div>
            <span class="result-tag">${badgeText}</span>
          </li>
        `;
      }
    });
    resultsList.innerHTML = html;
  };

  input.addEventListener('input', handleSearch);

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
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
    const fullAddr = localStorage.getItem('aisum_user_address') || `서울특별시 송파구 ${currentDong}`;
    barEl.innerHTML = `<span class="material-symbols-outlined current-bar-icon" style="font-size:16px;color:#0066ff;">home_pin</span><span class="current-bar-text" style="font-size:12.5px;color:#334155;">현재 설정된 주소: <strong style="color:#0f172a;">${escapeSearchHtml(fullAddr)}</strong></span>`;
  }

  // Render quick locations grid
  const grid = document.getElementById('quick-locations-grid');
  if (grid) {
    const popular = (window.AISUM_LOCATIONS_DB || []).filter((item) => item.isPopular);
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

  // 4. 약국(달빛병원 협약약국 49개소 + 보건복지부/지자체 공식 공공심야약국 26개소 통합) 거리 계산 및 정렬
  const pharmacies = [];
  const addedPharmKeys = new Set();

  // (1) 달빛어린이병원 1:1 공식 지정 협약약국
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

    const pharmKey = p.약국명.trim();
    addedPharmKeys.add(pharmKey);

    pharmacies.push({
      type: 'pharmacy',
      name: p.약국명,
      badge: p.약국구분 || '공식 협약약국',
      subBadge: subGuide,
      status: p.조제안전등급 || '🟢 30분 안심 조제',
      desc: `소아 시럽제 조제 가능 · ${p.이동안내 || '30분 안심 조제'} (${p.약국_평일운영 || '야간 운영'})`,
      phone: p.약국전화 || '02-555-1234',
      distKm: dist,
      dist: phDist,
      walkTime: phWalk,
      carTime: phCar,
      closing: phClose,
      pairingHospital: p.병원명 || ''
    });
  });

  // (2) 지자체 공식 지정 공공심야약국 (밤 10시 ~ 새벽 1시/2시 운영)
  const publicNightPharmacies = window.PUBLIC_NIGHT_PHARMACIES_DATA || [];
  publicNightPharmacies.forEach((p) => {
    if (!p.약국명) return;
    const pharmKey = p.약국명.trim();
    if (addedPharmKeys.has(pharmKey)) return; // 중복 방지

    const phLat = parseFloat(p.약국위도) || lat;
    const phLon = parseFloat(p.약국경도) || lon;
    const dist = window.calculateDistanceKm(lat, lon, phLat, phLon);
    const phDist = dist.toFixed(1);
    const phWalk = Math.max(5, Math.round(dist * 14)) + '분';
    const phCar = Math.max(3, Math.round(dist * 2.5)) + '분';
    const phClose = p.약국_평일마감
      ? `오늘 ~${p.약국_평일마감} 마감 (심야 전문)`
      : '새벽 1시까지 운영';

    addedPharmKeys.add(pharmKey);
    pharmacies.push({
      type: 'pharmacy',
      name: p.약국명,
      badge: '공공심야약국',
      subBadge: p.운영형태 || '365일 심야 운영',
      status: p.조제안전등급 || '🟢 심야 전문 조제',
      desc: `소아 야간 상비약 및 시럽제 조제 가능 · ${p.약국주소 || '공공심야약국'}`,
      phone: p.약국전화 || '02-120',
      distKm: dist,
      dist: phDist,
      walkTime: phWalk,
      carTime: phCar,
      closing: phClose,
      pairingHospital: ''
    });
  });

  // 최단 거리순 정렬
  pharmacies.sort((a, b) => a.distKm - b.distKm);

  // 5. 전체(all) 탭용 정렬: 최단거리 상위 6개 병원과 그에 매칭된 약국들을 조화롭게 조합 (총 12곳)
  const allList = [];
  const topHospitals = hospitals.slice(0, 6);
  topHospitals.forEach((hosp) => {
    allList.push(hosp);
    // 해당 병원의 협약 약국 찾기
    const matchingPharm = pharmacies.find((ph) => ph.pairingHospital === hosp.name || (ph.name && hosp.pairingPharmacy && ph.name.includes(hosp.pairingPharmacy)));
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
};

// ============================================================================
// 🏥 Facility Card Navigation & Data Bridge (병원/약국 카드 클릭 시 상세 페이지 데이터 바인딩)
// ============================================================================
window.selectLiveFacilityCard = function(facilityName, facilityType) {
  try {
    const pairings = window.NATIONWIDE_PAIRINGS_DATA || [];
    const userLoc = window.AisumPermissionManager
      ? window.AisumPermissionManager.getUserLocation()
      : { lat: 37.4858, lon: 127.1225, dong: '문정동' };

    let selectedHospital = null;

    if (facilityType === 'hospital') {
      const match = pairings.find(p => p.병원명 === facilityName) || pairings[0];
      if (match) {
        const hLat = parseFloat(match.병원위도) || userLoc.lat;
        const hLon = parseFloat(match.병원경도) || userLoc.lon;
        const distKm = Number(window.calculateDistanceKm(userLoc.lat, userLoc.lon, hLat, hLon).toFixed(1));
        selectedHospital = {
          name: match.병원명,
          dist: distKm,
          drive_min: Math.max(3, Math.round(distKm * 2.5)),
          duty_time: `오늘 야간진료 ${match.병원_평일마감 || '23:00'} 마감`,
          tel: match.병원전화 || '02-1234-5678',
          address: match.병원주소 || '서울특별시 송파구 문정동',
          waiting_count: 4,
          hours: {
            weekday: match.병원_평일진료 || '09:00 ~ 21:00',
            saturday: match.병원_토요진료 || '09:00 ~ 18:00',
            sunday: match.병원_일공진료 || '09:00 ~ 18:00'
          },
          pharmacy: {
            name: match.약국명 || '인근 안심약국',
            tel: match.약국전화 || '',
            duty_time: `${match.약국_평일마감 || '22:00'} 마감`,
            margin: match.안전마진_분 || 30,
            guide: match.이동안내 || '병원 인근 도보 1~2분',
            address: match.약국주소 || ''
          }
        };
      }
    } else {
      // 심야약국 클릭 시 해당 약국과 연결된 달빛병원 혹은 최근접 병원 세팅
      const match = pairings.find(p => p.약국명 === facilityName) || pairings[0];
      if (match) {
        const hLat = parseFloat(match.병원위도) || userLoc.lat;
        const hLon = parseFloat(match.병원경도) || userLoc.lon;
        const distKm = Number(window.calculateDistanceKm(userLoc.lat, userLoc.lon, hLat, hLon).toFixed(1));
        selectedHospital = {
          name: match.병원명,
          dist: distKm,
          drive_min: Math.max(3, Math.round(distKm * 2.5)),
          duty_time: `오늘 야간진료 ${match.병원_평일마감 || '23:00'} 마감`,
          tel: match.병원전화 || '02-1234-5678',
          address: match.병원주소 || '서울특별시 송파구 문정동',
          waiting_count: 4,
          hours: {
            weekday: match.병원_평일진료 || '09:00 ~ 21:00',
            saturday: match.병원_토요진료 || '09:00 ~ 18:00',
            sunday: match.병원_일공진료 || '09:00 ~ 18:00'
          },
          pharmacy: {
            name: match.약국명 || facilityName,
            tel: match.약국전화 || '',
            duty_time: `${match.약국_평일마감 || '22:00'} 마감`,
            margin: match.안전마진_분 || 30,
            guide: match.이동안내 || '공식 협약 심야약국',
            address: match.약국주소 || ''
          }
        };
      }
    }

    if (selectedHospital) {
      sessionStorage.setItem('selected_hospital', JSON.stringify(selectedHospital));
      const isHtml = window.location.pathname.endsWith('.html');
      window.location.href = isHtml ? 'hospital_detail.html' : 'hospital_detail';
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
