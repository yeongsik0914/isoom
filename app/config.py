"""Application configuration and credentials loader.

Handles environment variables, Windows Registry fallback for non-GCP public API keys,
and GCP Application Default Credentials (ADC) client initialization.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env file from project root if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _is_development() -> bool:
    return os.getenv("APP_ENV", "development").strip().lower() == "development"


def _scan_windows_registry_for_key(target_patterns: list[str]) -> Optional[str]:
    """Scans HKCU and HKLM Windows registry in local development when env vars are missing."""
    if sys.platform != "win32" or not _is_development():
        return None

    try:
        import winreg

        registry_targets = [
            (winreg.HKEY_CURRENT_USER, r"Environment"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
        ]

        for root_key, sub_path in registry_targets:
            try:
                with winreg.OpenKey(root_key, sub_path) as hkey:
                    num_values = winreg.QueryInfoKey(hkey)[1]
                    for i in range(num_values):
                        name, val, _ = winreg.EnumValue(hkey, i)
                        name_upper = name.upper()
                        if any(pattern in name_upper for pattern in target_patterns):
                            val_str = str(val).strip()
                            if len(val_str) > 5:
                                return val_str
            except Exception:
                continue
    except Exception:
        pass

    return None


def resolve_public_data_api_key() -> Optional[str]:
    """Resolves DATA_GO_API_KEY from os.environ, .env, or Windows Registry."""
    candidates = [
        "DATA_GO_API_KEY",
        "DATA_GO_KR_API_KEY",
        "DATA_GO_KEY",
        "PUBLIC_DATA_KEY",
        "PUBLIC_DATA_API_KEY",
        "EGEN_API_KEY",
        "KASI_API_KEY",
        "SERVICE_KEY",
    ]
    for key in candidates:
        val = os.getenv(key)
        if val and len(val.strip()) > 5:
            return val.strip()

    # Fallback to registry
    return _scan_windows_registry_for_key(["DATA_GO", "EGEN", "KASI", "PUBLIC_DATA", "SERVICE_KEY"])


def resolve_gcp_project_id() -> Optional[str]:
    """Resolves GCP project ID from environment variables or ADC default project."""
    for key in ("GOOGLE_CLOUD_PROJECT", "GCP_PROJECT", "GCLOUD_PROJECT"):
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()

    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        try:
            _, default_project = google.auth.default()
            if default_project and default_project.strip():
                return default_project.strip()
        except DefaultCredentialsError:
            pass
    except Exception:
        pass

    return None


def has_gcp_adc_credentials() -> bool:
    """Returns True when GCP Application Default Credentials (or Cloud Run runtime) are available."""
    if os.getenv("K_SERVICE"):
        return True
    try:
        import google.auth
        from google.auth.exceptions import DefaultCredentialsError

        try:
            creds, _ = google.auth.default()
            return creds is not None
        except DefaultCredentialsError:
            return False
    except Exception:
        return False


def resolve_firestore_database_id(
    project_id: Optional[str] = None,
    credentials: Optional[object] = None,
    detect_via_adc: bool = False,
) -> str:
    """Resolves Firestore database ID from env or (when requested) via ADC FirestoreAdminClient."""
    env_db = os.getenv("FIRESTORE_DATABASE_ID")
    if env_db and env_db.strip():
        return env_db.strip()

    if detect_via_adc and project_id:
        try:
            from google.cloud import firestore_admin_v1

            admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=credentials)
            parent = f"projects/{project_id}"
            resp = admin_client.list_databases(parent=parent)
            db_names = [db.name.split("/")[-1] for db in resp.databases]
            if "(default)" in db_names:
                return "(default)"
            if db_names:
                return db_names[0]
        except Exception:
            pass

    return "(default)"


class Settings:
    """Application runtime settings."""

    def __init__(self) -> None:
        self.project_root: Path = PROJECT_ROOT
        self.app_env: str = os.getenv("APP_ENV", "development").strip().lower()
        self.data_go_api_key: Optional[str] = resolve_public_data_api_key()
        self.gcp_project_id: Optional[str] = resolve_gcp_project_id()
        self.gcp_location: str = (os.getenv("GOOGLE_CLOUD_LOCATION") or "global").strip()
        self.firestore_database_id: str = resolve_firestore_database_id()
        self.gemini_triage_model: str = os.getenv("GEMINI_TRIAGE_MODEL", "gemini-3.8-flash")
        self.gemini_logistics_model: str = os.getenv("GEMINI_LOGISTICS_MODEL", "gemini-3.5-flash-lite")

    def has_public_api_key(self) -> bool:
        return bool(self.data_go_api_key)

    def has_gcp_adc(self) -> bool:
        return has_gcp_adc_credentials()


# Singleton instance
settings = Settings()

# Lazy Firebase Admin initialization
_firestore_client = None


def get_firestore_client():
    """Returns singleton Cloud Firestore client authenticated strictly via GCP ADC."""
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client

    import firebase_admin
    import google.auth
    from firebase_admin import firestore
    from google.auth.exceptions import DefaultCredentialsError

    credentials = None
    project_id = settings.gcp_project_id
    if not os.getenv("K_SERVICE"):
        try:
            credentials, default_project = google.auth.default()
            project_id = project_id or default_project
        except DefaultCredentialsError as e:
            raise RuntimeError(
                "GCP Application Default Credentials (ADC) not found for Firestore. "
                "Run `gcloud auth application-default login` locally or attach a Cloud Run service account."
            ) from e
    else:
        try:
            credentials, default_project = google.auth.default()
            project_id = project_id or default_project
        except Exception:
            pass

    if not firebase_admin._apps:
        if project_id:
            firebase_admin.initialize_app(options={"projectId": project_id})
        else:
            firebase_admin.initialize_app()

    db_id = os.getenv("FIRESTORE_DATABASE_ID", "").strip()
    if not db_id:
        if settings.firestore_database_id and settings.firestore_database_id != "(default)":
            db_id = settings.firestore_database_id
        else:
            db_id = resolve_firestore_database_id(
                project_id=project_id,
                credentials=credentials,
                detect_via_adc=True,
            )
            settings.firestore_database_id = db_id

    if db_id and db_id != "(default)":
        _firestore_client = firestore.client(database_id=db_id)
    else:
        _firestore_client = firestore.client()

    return _firestore_client
