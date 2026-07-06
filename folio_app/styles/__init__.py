"""Global CSS for the FOLIO app, split into one module per UI area.

Each sibling module exposes a `CSS` string with the raw rules for its
area (no <style> wrapper). apply_global_styles() concatenates them in
a fixed order and injects the result once via st.html().
"""

import streamlit as st

from folio_app.styles import (
    auth,
    browse_panel,
    buttons_inputs,
    cards,
    detail_page,
    header,
    hero,
    onboarding,
    portfolio,
    profile,
    project_form,
    shared,
    tokens,
)

_SECTIONS = (
    tokens,
    header,
    hero,
    buttons_inputs,
    browse_panel,
    cards,
    shared,
    auth,
    onboarding,
    project_form,
    portfolio,
    detail_page,
    profile,
)


def apply_global_styles() -> None:
    # st.html sends style-only content to Streamlit's event container instead
    # of the main layout, so reruns do not briefly remove the global CSS.
    css = "\n".join(section.CSS for section in _SECTIONS)
    st.html(f"<style>\n{css}\n</style>")
