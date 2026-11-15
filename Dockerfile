# ==============================================================================
# 🐳 아이숨 (isoom) - Google Cloud Run Production Dockerfile
# 경량 Python 3.11 슬림 베이스 & Multi-tenant Serverless 컨테이너
# ==============================================================================
FROM python:3.11-slim

# 파이썬 출력 버퍼링 비활성화 (Cloud Logging 실시간 스트리밍 최적화)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

# 시스템 필수 유틸리티 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 비루트(non-root) 서비스 사용자 생성
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /usr/sbin/nologin --create-home appuser

# 파이썬 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 전체 소스 복사 및 권한 설정
COPY --chown=appuser:appgroup . .

USER appuser

# Cloud Run 기본 포트 8080 오픈
EXPOSE 8080

# 컨테이너 헬스체크
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

# Python 애플리케이션 실행 (Cloud Run PORT 환경변수 동적 바인딩)
CMD ["python", "main.py"]
