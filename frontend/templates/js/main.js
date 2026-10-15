/**
 * 👶 아이숨 (Aisum) - 프론트엔드 모달 다이얼로그 & 인터랙션 제어 스크립트 (Vanilla JS)
 * - 크로스 브라우징 듀얼 로더 중복 실행 방지 (Idempotent Guard)
 * - 어떤 버튼(히어로 CTA, 증상 칩, 병원 카드 등)을 클릭하면 모달 팝업 오픈
 * - 모달 오픈 시 배경 어두운 반투명 오버레이 처리
 * - 하단 '취소' 및 '확인' 버튼, 오버레이 클릭 시 모달 닫기
 * - 증상 입력 페이지(input.html) 인풋 인터랙션 및 엔터키 입력 처리
 */

if (!window.__AISUM_INITIALIZED__) {
  window.__AISUM_INITIALIZED__ = true;

  document.addEventListener('DOMContentLoaded', () => {
    console.log('👶 아이숨 (Aisum) 모바일 웹 화면이 Safari/Chrome 호환 모드로 로드되었습니다.');

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

    // 3. Trigger Open: 병원 카드 클릭 시 모달 열기 (전화 버튼 제외)
    facilityCards.forEach((card) => {
      card.addEventListener('click', (e) => {
        if (e.target.closest('.call-btn') || e.target.closest('a[href^="tel:"]')) {
          return; // 전화 걸기는 기본 동작 유지
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
          // file:// 열람 환경과 http:// 서버 환경 모두 안전하게 호환 이동
          const targetUrl = window.location.pathname.endsWith('.html') ? 'result.html' : 'result';
          window.location.href = targetUrl;
        }
      });
    }
  });
}
