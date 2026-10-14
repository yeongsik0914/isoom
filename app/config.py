"""Application configuration and credentials loader.

Handles environment variables, Windows Registry fallback for API keys,
and Firebase Admin SDK singleton client initialization.
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


def _scan_windows_registry_for_key(target_patterns: list[str]) -> Optional[str]:
    """Scans HKCU and HKLM Windows registry for keys if environment variable is not yet visible in shell."""
    if sys.platform != "win32":
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


def resolve_gemini_api_key() -> Optional[str]:
    """Resolves GEMINI_API_KEY from os.environ, .env, or Windows Registry."""
    candidates = ["GEMINI_API_KEY", "GOOGLE_API_KEY"]
    for key in candidates:
        val = os.getenv(key)
        if val and len(val.strip()) > 5:
            return val.strip()

    return _scan_windows_registry_for_key(["GEMINI", "GOOGLE_API_KEY"])


def resolve_firebase_key_path() -> Optional[str]:
    """Finds serviceAccountKey.json path by checking candidates and Windows Registry."""
    env_path = os.getenv("FIREBASE_KEY_PATH")
    candidates = [
        env_path,
        r"C:\AI-Native-Agent\key\serviceAccountKey.json",
        r"C:\AI-Native-Agent\key\serviceAccountKey.json.json",
        str(PROJECT_ROOT / "serviceAccountKey.json"),
        "serviceAccountKey.json",
        "../serviceAccountKey.json",
        r"E:\FIREBASE_API_KEY\serviceAccountKey.json",
    ]

    for p in candidates:
        if p and os.path.exists(p):
            return str(Path(p).resolve())

    # Fallback to Windows Registry scan
    reg_val = _scan_windows_registry_for_key(["FIREBASE_KEY_PATH", "FIREBASE_KEY", "FIREBASE_SERVICE_ACCOUNT"])
    if reg_val and os.path.exists(reg_val):
        return str(Path(reg_val).resolve())

    return None


def resolve_firestore_database_id(key_path: Optional[str] = None) -> Optional[str]:
    """Resolves Firestore database ID from FIRESTORE_DATABASE_ID env or auto-detects from GCP project."""
    env_db = os.getenv("FIRESTORE_DATABASE_ID")
    if env_db:
        return env_db.strip()

    # If key_path is valid, attempt auto-detect via FirestoreAdminClient
    target_key = key_path or resolve_firebase_key_path()
    if target_key and os.path.exists(target_key):
        try:
            from google.cloud import firestore_admin_v1
            from google.oauth2 import service_account

            creds = service_account.Credentials.from_service_account_file(target_key)
            admin_client = firestore_admin_v1.FirestoreAdminClient(credentials=creds)
            parent = f"projects/{creds.project_id}"
            resp = admin_client.list_databases(parent=parent)
            db_names = [db.name.split("/")[-1] for db in resp.databases]
            if "(default)" in db_names:
                return "(default)"
            if db_names:
                return db_names[0]
        except Exception:
            pass

    return "data-test01"


class Settings:
    """Application runtime settings."""

    def __init__(self) -> None:
        self.project_root: Path = PROJECT_ROOT
        self.data_go_api_key: Optional[str] = resolve_public_data_api_key()
        self.gemini_api_key: Optional[str] = resolve_gemini_api_key()
        self.firebase_key_path: Optional[str] = resolve_firebase_key_path()
        self.firestore_database_id: Optional[str] = resolve_firestore_database_id(self.firebase_key_path)
        self.gemini_triage_model: str = os.getenv("GEMINI_TRIAGE_MODEL", "gemini-3.8-flash")
        self.gemini_logistics_model: str = os.getenv("GEMINI_LOGISTICS_MODEL", "gemini-3.5-flash-lite")

    def has_public_api_key(self) -> bool:
        return bool(self.data_go_api_key)

    def has_firebase_key(self) -> bool:
        return bool(self.firebase_key_path and os.path.exists(self.firebase_key_path))


# Singleton instance
settings = Settings()

# Lazy Firebase Admin initialization
_firestore_client = None


def get_firestore_client():
    """Returns singleton Firebase Cloud Firestore client with dynamic key resolution."""
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client

    import firebase_admin
    from firebase_admin import credentials, firestore

    key_path = settings.firebase_key_path or resolve_firebase_key_path()
    if not key_path or not os.path.exists(key_path):
        raise FileNotFoundError(
            f"Firebase service account key not found at {key_path}. "
            "Please ensure FIREBASE_KEY_PATH is set in .env or serviceAccountKey.json is placed in C:\\AI-Native-Agent\\key."
        )

    settings.firebase_key_path = key_path

    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

    db_id = settings.firestore_database_id or resolve_firestore_database_id(key_path)
    if db_id and db_id != "(default)":
        _firestore_client = firestore.client(database_id=db_id)
    else:
        _firestore_client = firestore.client()

    return _firestore_client
