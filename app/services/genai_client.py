"""Shared Google GenAI client factory using GCP Vertex AI ADC only (no API key)."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)


def is_vertex_adc_enabled() -> bool:
    """Returns True unless Vertex AI usage is explicitly disabled via env."""
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").strip().lower()
    return use_vertex not in {"false", "0", "no"}


def get_vertex_project_id(default_project: Optional[str] = None) -> Optional[str]:
    """Resolves GCP project ID from env vars or ADC default project without hardcoded personal defaults."""
    for key in ("GOOGLE_CLOUD_PROJECT", "GCP_PROJECT", "GCLOUD_PROJECT"):
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()
    if default_project and default_project.strip():
        return default_project.strip()
    return None


def resolve_adc_credentials() -> Tuple[Optional[Any], Optional[str]]:
    """Loads Google Application Default Credentials and associated project ID."""
    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        try:
            credentials, default_project = google.auth.default()
            return credentials, get_vertex_project_id(default_project)
        except DefaultCredentialsError:
            return None, get_vertex_project_id()
    except Exception:
        return None, get_vertex_project_id()


def is_genai_configured() -> bool:
    """Returns True when Vertex AI ADC credentials (or Cloud Run runtime) and project ID are ready."""
    if not is_vertex_adc_enabled():
        return False
    credentials, project_id = resolve_adc_credentials()
    has_creds = credentials is not None or bool(os.getenv("K_SERVICE"))
    return has_creds and bool(project_id)


def build_genai_client(agent_label: str = "GenAI") -> Optional[Any]:
    """Initializes a `google.genai.Client` strictly via GCP Vertex AI ADC."""
    if not is_vertex_adc_enabled():
        logger.info(f"[{agent_label}] GOOGLE_GENAI_USE_VERTEXAI is disabled; running in fallback mode.")
        return None

    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError, RefreshError
    except Exception as e:
        logger.warning(f"[{agent_label}] Failed to import google.auth for ADC: {e}")
        return None

    try:
        _, default_project = google.auth.default()
    except DefaultCredentialsError as e:
        logger.warning(
            f"[{agent_label}] GCP ADC credentials not found ({e}). "
            "Run `gcloud auth application-default login` locally or attach a Cloud Run service account."
        )
        return None
    except RefreshError as e:
        logger.warning(
            f"[{agent_label}] GCP ADC token expired ({e}). Run `gcloud auth application-default login`."
        )
        return None
    except Exception as e:
        logger.warning(f"[{agent_label}] Unexpected error loading GCP ADC credentials: {e}")
        return None

    project_id = get_vertex_project_id(default_project)
    if not project_id:
        logger.warning(
            f"[{agent_label}] Vertex AI ADC credentials loaded, but GOOGLE_CLOUD_PROJECT / GCP_PROJECT is unset."
        )
        return None

    try:
        import google.genai as genai

        location = (os.getenv("GOOGLE_CLOUD_LOCATION") or "global").strip()
        client = genai.Client(vertexai=True, project=project_id, location=location)
        logger.info(
            f"[{agent_label}] Initialized Vertex AI ADC Client (Project: {project_id}, Region: {location})"
        )
        return client
    except Exception as e:
        logger.warning(f"[{agent_label}] Failed to initialize Vertex AI ADC Client: {e}")
        return None
