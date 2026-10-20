# 📱 [아이숨 (Aisum)] PWA 도입, QR코드 웹앱 연동 & Cloud Run 배포 기획안

> **문서 버전**: v1.0.0  
> **작성 일자**: 2026-10-17  
> **총괄 책임자**: 정영식 팀장 (시스템 아키텍처 및 프로덕트 리드)  
> **문서 목적**: 스마트폰 PWA(Progressive Web App) 설치 환경 구축, 설정 페이지 내 QR코드 모달 연동, 그리고 Google Cloud Run 배포 시 다중 API Key 보안 관리 아키텍처 수립

---

## 🎯 1. 기획 개요 및 배경

현재 아이숨(Aisum)은 모바일 뷰포트 중심의 웹 애플리케이션으로 개발되어 뛰어난 사용성을 갖추고 있습니다.  
이를 한 단계 도약시켜 **스마트폰에서 앱스토어 설치 없이 네이티브 앱처럼 동작하는 PWA(Progressive Web App)**로 전환하고, PC나 태블릿 사용자가 **설정 페이지의 QR코드를 카메라로 스캔하여 스마트폰으로 즉시 이어받아 사용**할 수 있는 경험을 제공합니다.

또한, 프로덕션 환경으로 **Google Cloud Run (Serverless Container)**을 채택하여 트래픽에 따른 0 to N 자동 확장(Auto-scaling)을 지원하되, 프로젝트에 사용되는 **다수의 핵심 API Key(Gemini, 공공데이터, 카카오, Firebase 등)를 안전하고 표준적인 방식으로 주입·관리하는 인프라 아키텍처**를 수립합니다.

---

## 📲 2. 설정페이지(`settings.html`) QR코드 카테고리 구현 설계

### 2.1 설정 화면 신규 카테고리 UI/UX 구조
`settings.html`의 '일반', '앱 알림', '사용자 지원' 섹션 사이에 **'모바일 기기 연결'** 그룹을 신설합니다.

```
[설정 (settings.html)]
├── 📁 일반 (자녀 정보 변경, 글자 크기)
├── 🔔 앱 알림
├── 📱 모바일 기기 연결 (신규 카테고리)
│   └── 🔳 스마트폰으로 앱 열기 (QR코드) ➔ [QR코드 모달 팝업]
├── 💬 사용자 지원 (공지사항, 1:1 문의)
└── ℹ️ 정보 (가이드북, 이용약관, 라이선스, 버전)
```

### 2.2 설정 화면 마크업 추가안
```html
<!-- ================================================================= -->
<!-- CATEGORY: 모바일 기기 연결 (PWA & QR 연동)                         -->
<!-- ================================================================= -->
<section class="settings-group" aria-labelledby="group-mobile-title">
  <div class="settings-group-header">
    <h2 class="settings-group-title" id="group-mobile-title">모바일 기기 연결</h2>
  </div>

  <!-- 스마트폰으로 앱 열기 (QR코드) -->
  <button type="button" class="settings-item-row" id="qr-code-row-btn" aria-label="스마트폰으로 앱 열기" onclick="openQrModal()">
    <div class="settings-item-left" style="display: flex; align-items: center; gap: 10px;">
      <span class="material-symbols-outlined" style="color: var(--primary); font-size: 20px;">qr_code_2</span>
      <span class="settings-item-label">스마트폰으로 앱 열기</span>
    </div>
    <div class="settings-item-right">
      <span class="settings-item-value accent">PWA 지원</span>
      <span class="material-symbols-outlined settings-item-chevron">chevron_right</span>
    </div>
  </button>
</section>
```

### 2.3 QR코드 팝업 모달 상세 설계
사용자가 클릭 시 바텀시트 또는 모달 팝업으로 현재 서버 도메인을 실시간 반영하는 QR 코드가 생성됩니다.

```
┌──────────────────────────────────────────────┐
│  📱 스마트폰으로 아이숨 열기                 ✕│
├──────────────────────────────────────────────┤
│                                              │
│         ┌──────────────────────┐             │
│         │                      │             │
│         │     [ QR CODE ]      │             │
│         │   (실시간 동적 생성)   │             │
│         │                      │             │
│         └──────────────────────┘             │
│                                              │
│  📷 스마트폰 기본 카메라로 위 QR코드를 비추면    │
│     아이숨 모바일 웹앱으로 즉시 연결됩니다.     │
│                                              │
│  ──────────────────────────────────────────  │
│  💡 홈 화면에 앱으로 추가하는 방법:             │
│  • iOS (Safari): 공유 버튼(⎋) ➔ '홈 화면에 추가' │
│  • Android (Chrome): 메뉴(⋮) ➔ '앱 설치'     │
│                                              │
│  [ 📲 바로 앱으로 설치하기 (PWA 지원 기기) ]   │
└──────────────────────────────────────────────┘
```

* **동적 URL 자동 바인딩**: 로컬 개발 시에는 `http://{로컬IP}:8000`, Cloud Run 배포 후에는 `https://{cloud-run-domain}.run.app`을 `window.location.origin`으로 자동 감지하여 QR 생성.
* **경량 QR 라이브러리 연동**: 번들 사이즈가 15KB 미만인 순수 바닐라 JS QR 생성기(`qrcodejs` CDN 또는 초경량 SVG 인라인 생성기)를 채택하여 0ms 렌더링.

---

## ⚡ 3. PWA (Progressive Web App) 풀스택 인프라 명세

### 3.1 웹 앱 매니페스트 (`frontend/manifest.json`)
홈 화면 아이콘, 스플래시 배경색, 브라우저 상단 주소창을 숨기는 `standalone` 모드를 선언합니다.

```json
{
  "name": "아이숨 - 소아 야간응급 매칭",
  "short_name": "아이숨",
  "description": "야간·휴일 소아청소년과 및 달빛어린이병원 안심 매칭 서비스",
  "start_url": "/index.html",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#10b981",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/img/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/img/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

### 3.2 서비스 워커 (`frontend/sw.js`) 캐싱 전략
네트워크가 불안정하거나 지하주차장 등 음영지역에서도 핵심 가이드가 열리도록 2계층 캐싱을 적용합니다:
1. **Cache-First (정적 자산)**: CSS, 폰트, 로고 이미지, 12대 응급처치 가이드 정적 파일.
2. **Network-First with Fallback (동적 데이터)**: 실시간 병상 조회(`/api/v1/emergency/*`)는 항상 최신 네트워크 우선, 오프라인 시 로컬 프리셋 표출.

### 3.3 HTML 헤더 PWA 필수 태그 삽입
```html
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#10b981" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
<meta name="apple-mobile-web-app-title" content="아이숨" />
<link rel="apple-touch-icon" href="/img/icon-192.png" />
```

---

## 🔐 4. Google Cloud Run 배포 & 다중 API Key 보안 관리 아키텍처

### 4.1 프로젝트 사용 API Key 및 인증 자격 현황
현재 아이숨에서 운영 중인 핵심 API Key는 총 4대 영역입니다:

| 구분 | 환경 변수명 | 용도 및 역할 | 보안 민감도 |
| :--- | :--- | :--- | :---: |
| **1. Google Gemini** | `GEMINI_API_KEY` | 소아 KTAS 168개 지침 Direct Grounding 트리아제 | 🔴 최상 (과금 직결) |
| **2. 공공데이터포털** | `DATA_GO_KR_API_KEY` | NMC 실시간 소아 병상, 특일정보, 의약품 API | 🟡 중 (무료/쿼터 제한) |
| **3. 카카오맵** | `KAKAO_REST_API_KEY` | 도로명/좌표 정밀 역지오코딩 & Static Map 프록시 | 🟡 중 (일 30만 무료) |
| **4. Firebase Admin** | `serviceAccountKey.json` | Cloud Firestore 실시간 병상 적재 및 세션 보존 | 🔴 최상 (GCP 전체 권한) |

---

### 4.2 Cloud Run에서의 API Key 관리 3대 전략 비교

#### 🥇 [전략 1 (권장 · 최우선)]: GCP Secret Manager + IAM 무키(Keyless) 인증 (엔터프라이즈 표준)
Google Cloud 환경의 최대 장점을 극대화하는 **가장 안전하고 우아한 방식**입니다.

1. **문자열 API Key (`GEMINI`, `DATA_GO`, `KAKAO`)**:
   - GCP Secret Manager에 각 키를 등록:
     ```bash
     gcloud secrets create gemini-api-key --data-file=-
     gcloud secrets create public-data-api-key --data-file=-
     gcloud secrets create kakao-rest-api-key --data-file=-
     ```
   - Cloud Run 배포 시 컨테이너 환경 변수로 직접 마운트:
     ```bash
     --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,DATA_GO_KR_API_KEY=public-data-api-key:latest,KAKAO_REST_API_KEY=kakao-rest-api-key:latest"
     ```
2. **Firebase/Firestore 인증 (`serviceAccountKey.json`) ➔ "무키(Keyless) ADC 인증"**:
   - **놀라운 핵심 포인트**: Cloud Run과 Firestore는 둘 다 Google Cloud 내부 서비스입니다!
   - 따라서 별도의 JSON 키 파일(`serviceAccountKey.json`)을 컨테이너 안에 넣을 필요가 **전혀 없습니다**.
   - Cloud Run의 기본 서비스 계정(`{project-number}-compute@developer.gserviceaccount.com`)에 **`roles/datastore.user` (Cloud Datastore 사용자)** 권한만 부여하면, 백엔드의 `google-cloud-firestore` SDK가 **Google ADC(Application Default Credentials)**를 통해 자동으로 무키 인증을 완료합니다.
   - 키 파일 분실/유출 위험이 **0%**가 되는 현업 최상위 모범 사례(Best Practice)입니다.

---

#### 🥈 [전략 2]: Secret Manager 볼륨 마운트 (기존 코드 100% 유지 방식)
만약 기존의 `serviceAccountKey.json` 파일 경로 기반 코드를 단 한 줄도 수정하고 싶지 않다면:
1. `serviceAccountKey.json` 파일 전체를 Secret Manager에 비밀로 등록:
   ```bash
   gcloud secrets create firebase-credentials --data-file=serviceAccountKey.json
   ```
2. Cloud Run 배포 시 컨테이너의 특정 디렉터리에 파일로 마운트:
   ```bash
   --set-secrets="/secrets/serviceAccountKey.json=firebase-credentials:latest" \
   --set-env-vars="FIREBASE_KEY_PATH=/secrets/serviceAccountKey.json"
   ```
3. 컨테이너 내부 `/secrets/serviceAccountKey.json`에 가상 파일로 자동 생성되므로 기존 `config.py`의 파일 체크 로직이 100% 정상 작동합니다.

---

#### 🥉 [전략 3]: Cloud Run 환경 변수 직접 주입 (`--set-env-vars`) (개발/테스트용)
테스트 환경이나 신속한 프로토타이핑 시 사용하는 방식입니다:
```bash
gcloud run deploy isoom-service \
  --set-env-vars="GEMINI_API_KEY=AIzaSy...,DATA_GO_KR_API_KEY=...,KAKAO_REST_API_KEY=...,PORT=8080"
```
* 장점: 가장 빠르고 간단함.
* 단점: Cloud Run 콘솔 화면에 키 값이 노출될 수 있어 상용 운영 시에는 전략 1을 강력 권장함.

---

## 🐳 5. 프로덕션 Dockerfile 명세 & 배포 파이프라인

### 5.1 최적화된 Multi-stage Dockerfile
Cloud Run은 컨테이너에 전달되는 환경변수 `PORT`(기본값 8080)를 수신 대기해야 합니다.

```dockerfile
# -------------------------------------------------------------
# Stage 1: 경량 Python 3.11 슬림 베이스
# -------------------------------------------------------------
FROM python:3.11-slim

# 파이썬 출력 버퍼링 비활성화 (Cloud Logging 실시간 스트리밍)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# 시스템 의존성 설치 (curl 등)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 전체 소스 복사
COPY . .

# Cloud Run 기본 포트 8080 오픈
EXPOSE 8080

# Uvicorn 실행 (PORT 환경변수 바인딩)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

### 5.2 Cloud Run 원클릭 빌드 & 배포 CLI 명령어
GCP CLI(`gcloud`)를 통해 소스 디렉터리에서 바로 빌드하고 배포할 수 있습니다:

```bash
# 1. Cloud Build를 사용한 컨테이너 이미지 빌드 & Cloud Run 배포
gcloud run deploy isoom-app \
  --source . \
  --region asia-northeast3 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,DATA_GO_KR_API_KEY=public-data-api-key:latest,KAKAO_REST_API_KEY=kakao-rest-api-key:latest" \
  --set-secrets="/secrets/serviceAccountKey.json=firebase-credentials:latest" \
  --set-env-vars="FIREBASE_KEY_PATH=/secrets/serviceAccountKey.json"
```

---

## 🗓️ 6. 단계별 구현 액션 플랜

| 단계 | 주요 작업 내용 | 대상 파일 | 소요 시간 |
| :---: | :--- | :--- | :---: |
| **Step 1** | `manifest.json` 생성 및 `icon-192`, `icon-512` PWA 에셋 배치 | `frontend/manifest.json`, `frontend/img/` | 15분 |
| **Step 2** | `sw.js` 서비스 워커 작성 및 HTML 헤더 PWA 태그 연동 | `frontend/sw.js`, `index.html`, `settings.html` | 20분 |
| **Step 3** | `settings.html` 내 '모바일 기기 연결' 카테고리 및 QR코드 모달 UI 구현 | `frontend/templates/settings.html`, `frontend/css/style.css` | 30분 |
| **Step 4** | 바닐라 JS 실시간 QR코드 렌더러 탑재 & URL 자동 감지 바인딩 | `frontend/js/main.js` 또는 `settings.html` | 20분 |
| **Step 5** | Cloud Run용 `Dockerfile` 및 `.dockerignore` 생성 | `Dockerfile`, `.dockerignore` | 15분 |
| **Step 6** | `main.py` 포트 바인딩 최적화 (`os.getenv("PORT", 8000)`) 및 헬스체크 검증 | `main.py`, `tests/` | 10분 |

---

> **요약 결론**:  
> 설정 페이지의 QR코드 카테고리는 **바닐라 JS 기반으로 즉시 구현이 가능**하며, 스마트폰 스캔 시 모바일 웹앱 PWA로 매끄럽게 연결됩니다.  
> Cloud Run 배포 시 API Key 보안은 **GCP Secret Manager**와 **IAM 무키(Keyless) ADC 인증**을 결합함으로써 보안성과 운영 편의성을 모두 갖춘 현업 최고 수준의 아키텍처로 완성할 수 있습니다.
