from __future__ import annotations

from typing import Any

import streamlit as st


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


def navigate(page: str, **params: Any) -> None:
    """Navigate without a browser-level reload, preserving Streamlit session state."""
    st.query_params.clear()
    st.query_params["page"] = page if page in ROUTABLE_PAGES else "Home"
    for key, value in params.items():
        if value not in (None, ""):
            st.query_params[key] = value
    st.rerun()
