from dataclasses import dataclass
import os

from dotenv import load_dotenv
import streamlit as st


load_dotenv()


def _read_setting(name: str, default: str = "") -> str:
    """Read local environment values first, then Streamlit Cloud secrets."""
    environment_value = os.getenv(name)
    if environment_value is not None:
        return environment_value.strip()

    try:
        secret_value = st.secrets.get(name)
    except (FileNotFoundError, KeyError):
        secret_value = None

    if secret_value is None:
        return default.strip()
    return str(secret_value).strip()


def _read_first_setting(*names: str, default: str = "") -> str:
    for name in names:
        value = _read_setting(name)
        if value:
            return value
    return default.strip()


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str
    app_url: str
    cookie_password: str

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    @property
    def login_redirect_url(self) -> str:
        separator = "&" if "?" in self.app_url else "?"
        return f"{self.app_url}{separator}page=Login&verified=1"


def get_settings() -> Settings:
    return Settings(
        supabase_url=_read_setting("SUPABASE_URL"),
        supabase_key=_read_first_setting(
            "SUPABASE_PUBLISHABLE_KEY",
            "SUPABASE_ANON_KEY",
        ),
        app_url=_read_setting("APP_URL", "http://localhost:8501"),
        cookie_password=_read_setting(
            "COOKIE_PASSWORD",
            "folio-local-dev-cookie-password",
        ),
    )
