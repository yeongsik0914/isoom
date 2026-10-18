/**
 * 🌙 아이숨 (Aisum) - 전역 테마 관리자 (Theme Manager)
 * - 라이트(화이트) 모드, 다크 모드, OS 시스템 설정 동기화 3-Way 지원
 * - localStorage 'aisum_theme' 영구 보관 & FOUC 0ms 즉시 하이드레이션
 */
(function() {
  'use strict';

  var THEME_KEY = 'aisum_theme';

  var AisumThemeManager = {
    // 1. 현재 저장된 테마 가져오기 ('light' | 'dark' | 'system')
    getTheme: function() {
      try {
        return localStorage.getItem(THEME_KEY) || 'light';
      } catch (e) {
        return 'light';
      }
    },

    // 2. 실제 유효 테마 계산 ('light' | 'dark')
    getEffectiveTheme: function(theme) {
      var current = theme || this.getTheme();
      if (current === 'system') {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          return 'dark';
        }
        return 'light';
      }
      return current;
    },

    // 3. 테마 적용
    applyTheme: function(theme) {
      var current = theme || this.getTheme();
      var effective = this.getEffectiveTheme(current);

      document.documentElement.setAttribute('data-theme', effective);

      // Meta theme-color 동기화 (모바일 주소창/상태표시줄 색상)
      var metaTheme = document.querySelector('meta[name="theme-color"]');
      if (metaTheme) {
        metaTheme.setAttribute('content', effective === 'dark' ? '#0f172a' : '#0066ff');
      }

      // 커스텀 이벤트 발송 (다른 컴포넌트 동기화용)
      try {
        var evt = new CustomEvent('aisum-theme-change', {
          detail: { theme: current, effectiveTheme: effective }
        });
        window.dispatchEvent(evt);
      } catch (e) {}

      return effective;
    },

    // 4. 테마 설정 및 영구 저장
    setTheme: function(newTheme) {
      if (newTheme !== 'light' && newTheme !== 'dark' && newTheme !== 'system') {
        newTheme = 'light';
      }
      try {
        localStorage.setItem(THEME_KEY, newTheme);
      } catch (e) {}

      var effective = this.applyTheme(newTheme);

      // 설정 화면 표출 갱신 (열려있을 때)
      if (typeof window.updateThemeDisplay === 'function') {
        window.updateThemeDisplay(newTheme);
      }

      return effective;
    },

    // 5. 시스템 환경 변경 감지 리스너 등록
    watchSystemTheme: function() {
      if (!window.matchMedia) return;
      var media = window.matchMedia('(prefers-color-scheme: dark)');
      var self = this;
      var listener = function() {
        if (self.getTheme() === 'system') {
          self.applyTheme('system');
        }
      };
      if (media.addEventListener) {
        media.addEventListener('change', listener);
      } else if (media.addListener) {
        media.addListener(listener);
      }
    },

    // 6. 초기화
    init: function() {
      this.applyTheme();
      this.watchSystemTheme();
    }
  };

  // 전역 노출
  window.AisumThemeManager = AisumThemeManager;

  // 스크립트 로드 즉시 테마 적용 (FOUC 0ms 방지)
  AisumThemeManager.init();
})();
