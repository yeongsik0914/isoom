/**
 * 🌙 아이숨 (Aisum) - 프론트엔드 인터랙션 스크립트 모듈 (Vanilla JS)
 * - 크로스 브라우징 듀얼 로더 중복 실행 방지 (Idempotent Guard)
 * - 향후 백엔드 SSE 스트리밍 (/api/v1/chat/stream) 및 실시간 병원 대기열 연동 모듈 탑재 위치
 */

if (!window.__AISUM_INITIALIZED__) {
  window.__AISUM_INITIALIZED__ = true;

  document.addEventListener('DOMContentLoaded', () => {
    // Pure UI Micro-interactions will be initialized here
    console.log('🌙 아이숨 (Aisum) 모바일 웹 프론트엔드가 Safari/Chrome 호환 모드로 성공적으로 로드되었습니다.');
  });
}
