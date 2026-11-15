"""Authentication & session access verification utilities for isoom."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

logger = logging.getLogger(__name__)

# Process-local fallback secret for development/testing only when SESSION_SECRET is unset
_EPHEMERAL_SESSION_SECRET = secrets.token_hex(32)


def _is_production() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() == "production"


def _get_session_secret() -> str:
    secret = os.getenv("SESSION_SECRET", "").strip()
    if secret:
        return secret
    if _is_production():
        logger.warning(
            "[Auth] SESSION_SECRET is unset in production; using ephemeral per-process secret."
        )
    return _EPHEMERAL_SESSION_SECRET


def create_session_token(session_id: str) -> str:
    """Generates an HMAC-SHA256 token bound to `session_id`."""
    secret = _get_session_secret().encode("utf-8")
    return hmac.new(secret, session_id.encode("utf-8"), hashlib.sha256).hexdigest()


def is_valid_session_token(session_id: str, token: Optional[str]) -> bool:
    """Verifies an HMAC-SHA256 token for `session_id` in constant time."""
    if not token:
        return False
    expected = create_session_token(session_id)
    return hmac.compare_digest(expected, token.strip())


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.strip().split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None


def require_admin_token(
    authorization: Optional[str] = Header(default=None),
) -> Optional[str]:
    """Enforces Bearer token authentication for admin/sync endpoints when enabled.

    - In production (`APP_ENV=production`) or whenever `ADMIN_API_TOKEN` is configured,
      a matching `Authorization: Bearer <token>` header is mandatory.
    - In local development/test without `ADMIN_API_TOKEN`, requests are allowed cleanly.
    """
    configured_token = os.getenv("ADMIN_API_TOKEN", "").strip()
    if not configured_token:
        if _is_production():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="관리자 인증 토큰(ADMIN_API_TOKEN)이 서버에 설정되지 않았습니다.",
            )
        return None

    provided = _extract_bearer_token(authorization)
    if not provided:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 인증 토큰이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not hmac.compare_digest(configured_token, provided):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유효하지 않은 관리자 인증 토큰입니다.",
        )
    return "admin"


def verify_session_access(
    session_id: str,
    x_session_token: Optional[str] = Header(default=None, alias="X-Session-Token"),
    authorization: Optional[str] = Header(default=None),
) -> None:
    """Verifies ownership/admin access for session read/delete endpoints when enforced.

    Enforcement turns on automatically when `REQUIRE_SESSION_TOKEN=true` or `APP_ENV=production`.
    """
    require_token = (
        os.getenv("REQUIRE_SESSION_TOKEN", "").strip().lower() == "true"
        or _is_production()
    )
    if not require_token:
        return

    admin_token = os.getenv("ADMIN_API_TOKEN", "").strip()
    bearer = _extract_bearer_token(authorization)
    if admin_token and bearer and hmac.compare_digest(admin_token, bearer):
        return

    if is_valid_session_token(session_id, x_session_token):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효한 세션 접근 토큰(X-Session-Token)이 필요합니다.",
    )
