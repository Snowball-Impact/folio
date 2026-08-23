"""Global CSS for the FOLIO app, split into one module per UI area.

Each sibling module exposes a `CSS` string with the raw rules for its
area (no <style> wrapper). apply_global_styles() concatenates them in
a fixed order and injects the result once via st.html().
"""

import streamlit as st

from folio_app.styles import (
    about,
    about_vision,
    auth,
    browse_panel,
    buttons_inputs,
    cards,
    detail_comments,
    detail_page,
    detail_visual,
    gallery_rail,
    header,
    header_notifications,
    hero,
    hero_footer,
    notifications,
    onboarding,
    portfolio,
    powerbi,
    profile,
    project_card_cover,
    project_form,
    reference,
    shared,
    streamlit_overrides,
    tokens,
)

_SECTIONS = (
    tokens,
    streamlit_overrides,
    header,
    header_notifications,
    hero,
    hero_footer,
    about,
    about_vision,
    buttons_inputs,
    browse_panel,
    cards,
    project_card_cover,
    gallery_rail,
    shared,
    auth,
    notifications,
    onboarding,
    project_form,
    portfolio,
    powerbi,
    reference,
    detail_page,
    detail_visual,
    detail_comments,
    profile,
)


def apply_global_styles() -> None:
    # st.html sends style-only content to Streamlit's event container instead
    # of the main layout, so reruns do not briefly remove the global CSS.
    css = "\n".join(section.CSS for section in _SECTIONS)
    st.html(f"<style>\n{css}\n</style>")
