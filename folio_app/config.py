from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_anon_key: str
    app_url: str

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_anon_key)

    @property
    def login_redirect_url(self) -> str:
        separator = "&" if "?" in self.app_url else "?"
        return f"{self.app_url}{separator}page=Login&verified=1"


def get_settings() -> Settings:
    return Settings(
        supabase_url=os.getenv("SUPABASE_URL", "").strip(),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", "").strip(),
        app_url=os.getenv("APP_URL", "http://localhost:8501").strip(),
    )
