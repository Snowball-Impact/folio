import streamlit as st
from supabase import Client, create_client

from folio_app.config import get_settings


SESSION_CLIENT_KEY = "folio_supabase_client"
SESSION_CLIENT_CONFIG_KEY = "folio_supabase_client_config"


def get_supabase_client() -> Client | None:
    settings = get_settings()
    if not settings.is_supabase_configured:
        return None

    config_key = (settings.supabase_url, settings.supabase_anon_key)
    client = st.session_state.get(SESSION_CLIENT_KEY)
    if client is None or st.session_state.get(SESSION_CLIENT_CONFIG_KEY) != config_key:
        client = create_client(settings.supabase_url, settings.supabase_anon_key)
        st.session_state[SESSION_CLIENT_KEY] = client
        st.session_state[SESSION_CLIENT_CONFIG_KEY] = config_key
    return client


def clear_supabase_client() -> None:
    st.session_state.pop(SESSION_CLIENT_KEY, None)
    st.session_state.pop(SESSION_CLIENT_CONFIG_KEY, None)


def recover_from_expired_jwt(exc: Exception) -> bool:
    message = str(exc)
    if "JWT expired" not in message and "PGRST303" not in message:
        return False

    client = get_supabase_client()
    settings = get_settings()
    if client is not None and settings.supabase_anon_key:
        client.postgrest.auth(settings.supabase_anon_key)

    st.session_state.pop("folio_access_token", None)
    st.session_state.pop("folio_refresh_token", None)
    st.session_state.pop("folio_user", None)
    st.session_state["folio_clear_browser_auth"] = True
    return True
