#!/usr/bin/env bash
# ==============================================================================
# 🚀 아이숨 (Aisum) - Google Cloud Run 원클릭 프로덕션 배포 스크립트
# .env 파일의 핵심 API Key들을 자동 로드하여 Cloud Run에 안전하게 주입·배포합니다.
# ==============================================================================

set -e

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${GREEN}  🌙 아이숨 (Aisum) - Google Cloud Run 배포 파이프라인 시작${NC}"
echo -e "${BLUE}==============================================================================${NC}"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 1. .env 파일 검증
if [ ! -f ".env" ]; then
  echo -e "${RED}[오류] .env 파일이 존재하지 않습니다. 프로젝트 루트에 .env 파일을 생성해주세요.${NC}"
  exit 1
fi

echo -e "${GREEN}[1/5] .env 파일에서 API Key 로드 중...${NC}"

# .env 파일에서 주석 제외하고 환경변수 읽기
export $(grep -v '^#' .env | grep -v '^\s*$' | xargs)

# 변수 매핑 및 검증
DATA_GO_KEY="${DATA_GO_API_KEY:-$DATA_GO_KR_API_KEY}"
GEMINI_KEY="${GEMINI_API_KEY}"
KAKAO_KEY="${KAKAO_REST_API_KEY}"
DB_ID="${FIRESTORE_DATABASE_ID:-isoom}"

if [ -z "$DATA_GO_KEY" ]; then
  echo -e "${YELLOW}[경고] DATA_GO_API_KEY가 비어 있습니다. 공공데이터 실시간 연동이 제한될 수 있습니다.${NC}"
fi

if [ -z "$GEMINI_KEY" ]; then
  echo -e "${YELLOW}[경고] GEMINI_API_KEY가 비어 있습니다. AI 트리아제 기능이 제한될 수 있습니다.${NC}"
fi

if [ -z "$KAKAO_KEY" ]; then
  echo -e "${YELLOW}[경고] KAKAO_REST_API_KEY가 비어 있습니다. 카카오 주소 역지오코딩이 제한될 수 있습니다.${NC}"
fi

echo -e "  • DATA_GO_API_KEY: ${DATA_GO_KEY:0:8}..."
echo -e "  • GEMINI_API_KEY: ${GEMINI_KEY:0:8}..."
echo -e "  • KAKAO_REST_API_KEY: ${KAKAO_KEY:0:8}..."
echo -e "  • FIRESTORE_DATABASE_ID: $DB_ID"

# 2. Firebase serviceAccountKey.json 탐색 및 번들링 준비
echo -e "\n${GREEN}[2/5] Firebase 서비스 계정 키 파일 점검 중...${NC}"
KEY_PATH="${FIREBASE_KEY_PATH}"
if [ -z "$KEY_PATH" ] || [ ! -f "$KEY_PATH" ]; then
  CANDIDATE_PATHS=(
    "serviceAccountKey.json"
    "../serviceAccountKey.json"
    "$HOME/Desktop/Project/serviceAccountKey.json"
  )
  for p in "${CANDIDATE_PATHS[@]}"; do
    if [ -f "$p" ]; then
      KEY_PATH="$p"
      break
    fi
  done
fi

if [ -f "$KEY_PATH" ]; then
  echo -e "  • 서비스 계정 키 발견: $KEY_PATH"
  # 컨테이너 빌드를 위해 프로젝트 루트에 안전 복사
  cp "$KEY_PATH" ./serviceAccountKey.json
  echo -e "  • 빌드용 키 복사 완료 (./serviceAccountKey.json)"
else
  echo -e "${YELLOW}[안내] 로컬 serviceAccountKey.json 파일이 없습니다. Cloud Run IAM 무키(ADC) 인증 모드로 진행합니다.${NC}"
fi

# 3. 정적 자산 및 PWA 매니페스트 동기화 점검
echo -e "\n${GREEN}[3/5] PWA 정적 자산(manifest, sw.js, icons) 동기화 점검...${NC}"
mkdir -p app/static/img app/static/css app/templates
cp frontend/manifest.json app/static/manifest.json 2>/dev/null || true
cp frontend/sw.js app/static/sw.js 2>/dev/null || true
cp -r frontend/img/* app/static/img/ 2>/dev/null || true
cp frontend/templates/*.html app/templates/ 2>/dev/null || true
cp frontend/css/style.css app/static/css/style.css 2>/dev/null || true
echo -e "  • PWA 및 템플릿 동기화 완료"

# 4. gcloud CLI 설치 및 인증 확인
echo -e "\n${GREEN}[4/5] Google Cloud CLI (gcloud) 상태 확인...${NC}"
if ! command -v gcloud &> /dev/null; then
  echo -e "${YELLOW}[알림] 'gcloud' 명령어가 설치되어 있지 않거나 PATH에 등록되지 않았습니다.${NC}"
  echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
  echo -e "💡 Google Cloud SDK 설치 안내:"
  echo -e "   macOS (Homebrew): brew install --cask google-cloud-sdk"
  echo -e "   설치 후: gcloud auth login && gcloud config set project [GCP_PROJECT_ID]"
  echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
  echo -e "아래 배포 명령어를 수동으로 실행하시거나 gcloud 설치 후 본 스크립트를 다시 실행하십시오:"
  echo ""
  echo "gcloud run deploy isoom-service \\"
  echo "  --project \$CURRENT_PROJECT \\"
  echo "  --source . \\"
  echo "  --region asia-northeast3 \\"
  echo "  --platform managed \\"
  echo "  --allow-unauthenticated \\"
  echo "  --port 8080 \\"
  echo "  --memory 1Gi \\"
  echo "  --cpu 1 \\"
  echo "  --set-env-vars=\"DATA_GO_API_KEY=\$DATA_GO_KEY,DATA_GO_KR_API_KEY=\$DATA_GO_KEY,GEMINI_API_KEY=\$GEMINI_KEY,KAKAO_REST_API_KEY=\$KAKAO_KEY,FIRESTORE_DATABASE_ID=\$DB_ID,FIREBASE_KEY_PATH=/app/serviceAccountKey.json,APP_ENV=production\""
  echo ""
  exit 0
fi

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || true)
echo -e "  • 현재 선택된 GCP 프로젝트: ${GREEN}$CURRENT_PROJECT${NC}"

if [ -z "$CURRENT_PROJECT" ] || [ "$CURRENT_PROJECT" == "(unset)" ]; then
  echo -e "${RED}[오류] 활성화된 GCP 프로젝트가 없습니다.${NC}"
  echo -e "다음 명령어로 프로젝트를 설정해주세요: gcloud config set project [프로젝트ID]"
  exit 1
fi

# 5. Cloud Run 서비스 빌드 & 배포 실행
SERVICE_NAME="isoom-service"
REGION="asia-northeast3" # 서울 리전

echo -e "\n${GREEN}[5/5] Cloud Run 서비스 배포 실행 ($SERVICE_NAME, $REGION)...${NC}"

ENV_VARS="DATA_GO_API_KEY=$DATA_GO_KEY"
ENV_VARS="$ENV_VARS,DATA_GO_KR_API_KEY=$DATA_GO_KEY"
ENV_VARS="$ENV_VARS,GEMINI_API_KEY=$GEMINI_KEY"
ENV_VARS="$ENV_VARS,KAKAO_REST_API_KEY=$KAKAO_KEY"
ENV_VARS="$ENV_VARS,FIRESTORE_DATABASE_ID=$DB_ID"
ENV_VARS="$ENV_VARS,FIREBASE_KEY_PATH=/app/serviceAccountKey.json"
ENV_VARS="$ENV_VARS,APP_ENV=production"

gcloud run deploy "$SERVICE_NAME" \
  --project "$CURRENT_PROJECT" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="$ENV_VARS"

echo -e "\n${GREEN}==============================================================================${NC}"
echo -e "${GREEN}  🎉 아이숨 (Aisum) Cloud Run PWA 배포가 성공적으로 완료되었습니다!${NC}"
echo -e "${GREEN}==============================================================================${NC}"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)' 2>/dev/null || true)
if [ -n "$SERVICE_URL" ]; then
  echo -e "🌐 서비스 접속 URL: ${BLUE}$SERVICE_URL${NC}"
  echo -e "📱 스마트폰 카메라로 접속하여 '홈 화면에 추가'를 통해 네이티브 PWA 앱으로 사용 가능합니다."
fi
