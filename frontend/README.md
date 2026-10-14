# 👶 아이숨 (Aisum) 프론트엔드 모바일 웹 애플리케이션 (Frontend Workspace)

> **디렉터리 위치**: `frontend/`  
> **기반 규격**: [AISUM_STITCH_DESIGN_REPORT.md](../AISUM_STITCH_DESIGN_REPORT.md)  
> **디자인 시스템**: Calm Harbor (Modern Healthcare Clean Light Theme)  
> **기술 스택**: Semantic HTML5, Vanilla CSS3, Modern ES6+ JavaScript  

---

## 📂 폴더 구조 (Folder Architecture)

```
frontend/
├── index.html              # 아이숨 메인 홈 화면 (SPA 진입점)
├── css/
│   └── style.css           # Calm Harbor 디자인 토큰 및 반응형 Vanilla CSS
├── js/
│   └── main.js             # 클라이언트 인터랙션 및 향후 SSE 챗봇 연동 모듈
├── assets/                 # 정적 그래픽 에셋 (아이콘, 일러스트)
│   ├── icons/
│   └── images/
└── README.md               # 본 문서
```

---

## 🚀 로컬 실행 및 확인 방법

1. **로컬 파일 브라우징**:
   - 브라우저(Chrome, Edge 등)에서 [index.html](index.html)을 직접 열어 확인합니다.
2. **FastAPI 서버 연동 브라우징**:
   - `python main.py` 실행 후 `http://localhost:8000/home` 접속.
