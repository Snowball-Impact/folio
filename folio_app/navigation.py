from __future__ import annotations

from typing import Any

import streamlit as st
import streamlit.components.v1 as components


ROUTABLE_PAGES = {
    "Home",
    "About",
    "Gallery",
    "Reference",
    "Power BI",
    "Login",
    "Sign Up",
    "Submit",
    "My Page",
    "My Portfolio",
    "Notifications",
    "Policy",
    "Profile",
}

EDIT_PROJECT_QUERY_PARAM = "edit_project_id"
SESSION_ROUTE_PAGE_KEY = "folio_route_page"
SESSION_ROUTE_PARAMS_KEY = "folio_route_params"
SESSION_ROUTE_URL_KEY = "folio_route_url"
SESSION_ROUTE_SOURCE_PAGE_KEY = "folio_route_source_page"


def _normalized_params(params: dict[str, Any]) -> dict[str, str]:
    return {key: str(value) for key, value in params.items() if value not in (None, "")}


def _query_string(page: str, params: dict[str, str]) -> str:
    from urllib.parse import urlencode

    return urlencode({"page": page, **params})


def current_route_page() -> str:
    query_page = st.query_params.get("page") or "Home"
    staged_page = st.session_state.get(SESSION_ROUTE_PAGE_KEY)
    source_page = st.session_state.get(SESSION_ROUTE_SOURCE_PAGE_KEY)
    if staged_page in ROUTABLE_PAGES:
        if query_page == source_page or query_page == staged_page:
            return staged_page
        st.session_state.pop(SESSION_ROUTE_PAGE_KEY, None)
        st.session_state.pop(SESSION_ROUTE_PARAMS_KEY, None)
        st.session_state.pop(SESSION_ROUTE_SOURCE_PAGE_KEY, None)
    page = query_page
    return page if page in ROUTABLE_PAGES else "Home"


def set_route(page: str, **params: Any) -> str:
    """Stage an in-app route without forcing a query-param rerun."""
    normalized_page = page if page in ROUTABLE_PAGES else "Home"
    normalized_params = _normalized_params(params)
    st.session_state[SESSION_ROUTE_SOURCE_PAGE_KEY] = st.query_params.get("page") or "Home"
    st.session_state[SESSION_ROUTE_PAGE_KEY] = normalized_page
    st.session_state[SESSION_ROUTE_PARAMS_KEY] = normalized_params
    st.session_state[SESSION_ROUTE_URL_KEY] = "?" + _query_string(normalized_page, normalized_params)
    return normalized_page


def navigate(page: str, **params: Any) -> None:
    """Navigate without a browser-level reload, preserving Streamlit session state."""
    normalized_page = page if page in ROUTABLE_PAGES else "Home"
    st.session_state[SESSION_ROUTE_PAGE_KEY] = normalized_page
    st.session_state[SESSION_ROUTE_PARAMS_KEY] = _normalized_params(params)
    st.session_state[SESSION_ROUTE_SOURCE_PAGE_KEY] = normalized_page
    st.session_state.pop(SESSION_ROUTE_URL_KEY, None)
    st.query_params.clear()
    st.query_params["page"] = normalized_page
    for key, value in params.items():
        if value not in (None, ""):
            st.query_params[key] = value
    st.rerun()


def sync_staged_route_url() -> None:
    target_url = st.session_state.pop(SESSION_ROUTE_URL_KEY, "")
    if not target_url:
        return

    components.html(
        f"""
        <script>
        (function() {{
            var target = {target_url!r};
            var parentWindow = window.parent;
            if (parentWindow.location.search !== target) {{
                parentWindow.history.pushState(null, "", target);
            }}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )
