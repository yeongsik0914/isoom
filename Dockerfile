# ==============================================================================
# 🐳 아이숨 (Aisum) - Google Cloud Run Production Dockerfile
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

# 파이썬 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 전체 소스 복사
COPY . .

# Cloud Run 기본 포트 8080 오픈
EXPOSE 8080

# Python 애플리케이션 실행 (Cloud Run PORT 환경변수 동적 바인딩)
CMD ["python", "main.py"]
