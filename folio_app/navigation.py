from __future__ import annotations

from typing import Any

import streamlit as st


ROUTABLE_PAGES = {
    "Home",
    "Gallery",
    "Login",
    "Sign Up",
    "Submit",
    "My Page",
    "My Portfolio",
    "Profile",
}


def navigate(page: str, **params: Any) -> None:
    """Navigate without a browser-level reload, preserving Streamlit session state."""
    st.query_params.clear()
    st.query_params["page"] = page if page in ROUTABLE_PAGES else "Home"
    for key, value in params.items():
        if value not in (None, ""):
            st.query_params[key] = value
    st.rerun()
