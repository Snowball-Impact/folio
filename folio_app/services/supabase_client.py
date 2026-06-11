import streamlit as st
from supabase import Client, create_client

from folio_app.config import get_settings


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.is_supabase_configured:
        return None

    return create_client(settings.supabase_url, settings.supabase_anon_key)
