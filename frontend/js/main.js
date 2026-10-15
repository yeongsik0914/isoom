/**
 * 👶 아이숨 (Aisum) - 프론트엔드 모달 다이얼로그 제어 스크립트
 * - 어떤 버튼(히어로 CTA, 증상 칩, 병원 카드 등)을 클릭하면 모달 팝업 오픈
 * - 모달 오픈 시 배경 어두운 반투명 오버레이 처리
 * - 하단 '취소' 및 '확인' 버튼, 오버레이 클릭 시 모달 닫기
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('👶 아이숨 (Aisum) 웹 화면이 로드되었습니다.');

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

  // 5. Modal Action: '확인' 버튼 클릭 시 모달 닫기
  if (modalConfirmBtn) {
    modalConfirmBtn.addEventListener('click', (e) => {
      e.preventDefault();
      closeModal();
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

  // 8. Symptom Input Page Logic (입력 필드 인터랙션)
  const symptomInput = document.getElementById('symptom-input');
  const floatingLabel = document.getElementById('floating-label');
  const inputClearBtn = document.getElementById('input-clear-btn');
  const confirmInputBtn = document.getElementById('confirm-input-btn');

  if (symptomInput) {
    symptomInput.addEventListener('input', () => {
      const val = symptomInput.value.trim();
      if (val.length > 0) {
        if (floatingLabel) floatingLabel.style.display = 'block';
        if (inputClearBtn) inputClearBtn.style.display = 'inline-flex';
      } else {
        if (floatingLabel) floatingLabel.style.display = 'none';
        if (inputClearBtn) inputClearBtn.style.display = 'none';
      }
    });

    if (inputClearBtn) {
      inputClearBtn.addEventListener('click', (e) => {
        e.preventDefault();
        symptomInput.value = '';
        if (floatingLabel) floatingLabel.style.display = 'none';
        inputClearBtn.style.display = 'none';
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
        console.log('입력된 증상 프롬프트:', text);
      }
    });
  }
});

