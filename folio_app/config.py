from dataclasses import dataclass
import os
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
import streamlit as st


load_dotenv()


def _read_setting(name: str, default: str = "") -> str:
    """Read local environment values first, then Streamlit Cloud secrets."""
    environment_value = os.getenv(name)
    if environment_value is not None and environment_value.strip():
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


def _read_secret_section(section: str, *names: str) -> str:
    try:
        values = st.secrets.get(section, {})
    except (FileNotFoundError, KeyError):
        return ""

    if not hasattr(values, "get"):
        return ""
    for name in names:
        value = values.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str
    app_url: str
    cookie_password: str
    ga_measurement_id: str
    supabase_service_role_key: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "FOLIO"
    smtp_use_tls: bool = True
    thumbnail_storage_bucket: str = "project-thumbnails"
    chrome_binary_path: str = ""
    chromedriver_path: str = ""

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)

    @property
    def is_email_notifications_configured(self) -> bool:
        return bool(
            self.supabase_url
            and self.supabase_service_role_key
            and self.smtp_host
            and self.smtp_from_email
        )

    @property
    def missing_supabase_settings(self) -> tuple[str, ...]:
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_key:
            missing.append("SUPABASE_PUBLISHABLE_KEY")
        return tuple(missing)

    @property
    def login_redirect_url(self) -> str:
        return _append_query_params(self.app_url, "page=Login&verified=1")

    @property
    def password_reset_redirect_url(self) -> str:
        return _append_query_params(self.app_url, "page=Login&reset=1")


def _append_query_params(base_url: str, query_params: str) -> str:
    parsed = urlsplit(base_url)
    path = parsed.path or "/"
    query = f"{parsed.query}&{query_params}" if parsed.query else query_params
    return urlunsplit((parsed.scheme, parsed.netloc, path, query, parsed.fragment))


def get_settings() -> Settings:
    supabase_url = _read_setting("SUPABASE_URL") or _read_secret_section(
        "supabase",
        "SUPABASE_URL",
        "url",
    )
    supabase_key = _read_first_setting(
        "SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    ) or _read_secret_section(
        "supabase",
        "SUPABASE_PUBLISHABLE_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
        "publishable_key",
        "anon_key",
        "key",
    )
    return Settings(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        app_url=_read_setting("APP_URL", "http://localhost:8501"),
        cookie_password=_read_setting(
            "COOKIE_PASSWORD",
            "folio-local-dev-cookie-password",
        ),
        ga_measurement_id=_read_setting("GA_MEASUREMENT_ID"),
        supabase_service_role_key=_read_setting("SUPABASE_SERVICE_ROLE_KEY")
        or _read_secret_section("supabase", "SUPABASE_SERVICE_ROLE_KEY", "service_role_key"),
        smtp_host=_read_setting("SMTP_HOST") or _read_secret_section("smtp", "SMTP_HOST", "host"),
        smtp_port=_read_int_setting("SMTP_PORT", 587),
        smtp_username=_read_setting("SMTP_USERNAME") or _read_secret_section("smtp", "SMTP_USERNAME", "username"),
        smtp_password=_read_setting("SMTP_PASSWORD") or _read_secret_section("smtp", "SMTP_PASSWORD", "password"),
        smtp_from_email=_read_setting("SMTP_FROM_EMAIL") or _read_secret_section("smtp", "SMTP_FROM_EMAIL", "from_email"),
        smtp_from_name=_read_setting("SMTP_FROM_NAME") or _read_secret_section("smtp", "SMTP_FROM_NAME", "from_name") or "FOLIO",
        smtp_use_tls=_read_bool_setting("SMTP_USE_TLS", True),
        thumbnail_storage_bucket=_read_setting("THUMBNAIL_STORAGE_BUCKET", "project-thumbnails")
        or _read_secret_section("supabase", "thumbnail_storage_bucket"),
        chrome_binary_path=_read_setting("CHROME_BINARY_PATH"),
        chromedriver_path=_read_setting("CHROMEDRIVER_PATH"),
    )


def _read_int_setting(name: str, default: int) -> int:
    value = _read_setting(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _read_bool_setting(name: str, default: bool) -> bool:
    value = _read_setting(name)
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
