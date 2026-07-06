"""Render the real header component in both auth states side by side.

Lets you compare logged-in vs logged-out header layout without a real
Supabase login: monkeypatches folio_app.components.layout.get_current_user
so render_header() takes the branch you ask for via ?mode=logged_in or
?mode=logged_out (default).

Usage:
    streamlit run tools/probe_header_auth_states.py --server.port 8504
    # then diff computed styles/rects between:
    #   http://localhost:8504/?mode=logged_out
    #   http://localhost:8504/?mode=logged_in
"""

from unittest.mock import patch

import streamlit as st

from folio_app.styles import apply_global_styles
from folio_app.components import layout

apply_global_styles()

mode = st.query_params.get("mode", "logged_out")
fake_user = {"id": "test-user-id", "email": "test@example.com"}

with patch(
    "folio_app.components.layout.get_current_user",
    return_value=fake_user if mode == "logged_in" else None,
):
    layout.render_header(initial_page="Home")

st.write(f"mode = {mode}")
