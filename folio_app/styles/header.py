"""Sticky top navigation header: brand, right-aligned nav buttons."""

CSS = """
/* ── Header (light) ──
   The header has exactly two real (in-flow) children: the brand
   group (logo + invisible "홈으로 이동" hit-target) and the right
   nav group. Plain flexbox (row + space-between +
   align-items:center) lays them out and vertically centers them --
   deliberately NOT position:absolute + top:50%/margin:auto, which
   was tried first and kept breaking: percentage-based `top` needs a
   *definite* containing-block height to resolve against, and this
   header only ever has `min-height` (an explicit `height` collapses
   it to 0 once there's no in-flow content -- Streamlit's own
   auto-sizing for vertical blocks fights a hard height down to the
   zero content height even with `!important`), so the "definite
   height" percentages need was never reliably there and the exact
   pixel result silently drifted based on unrelated markup elsewhere
   on the page. Keeping both children as ordinary flex items sidesteps
   the whole problem: align-items:center doesn't need a percentage. */
.st-key-folio_header {
    background: var(--folio-navy) !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.22) !important;
    color: rgba(200, 215, 255, 0.85) !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 0 !important;
    min-height: 64px !important;
    padding: 0 42px !important;
    position: sticky;
    top: 0;
    z-index: 999;
}

/* Streamlit sets an explicit pixel width (matching the header's full
   content width) on stElementContainer/stLayoutWrapper/.stButton/
   stPopover regardless of context, which would otherwise stretch
   both flex items to fill the row and squeeze each other out.
   Constrain them back to their own content size instead.
   (stLayoutWrapper is the direct-child wrapper st.container()
   produces around the brand group in Streamlit 1.58 -- it replaced
   stVerticalBlockBorderWrapper for this position, so both are
   listed in case a future version reintroduces the older one.) */
.st-key-folio_header > [data-testid="stElementContainer"],
.st-key-folio_header > [data-testid="stVerticalBlockBorderWrapper"],
.st-key-folio_header > [data-testid="stLayoutWrapper"],
.st-key-folio_header .stButton {
    flex: 0 0 auto !important;
    width: auto !important;
}

/* Zero out internal gaps/padding/borders so Streamlit's own vertical
   rhythm and container chrome don't add unwanted space inside the
   header. stMarkdownContainer needs the same reset (Streamlit 1.58
   gives it a -1rem bottom margin for line-height compensation). */
.st-key-folio_header [data-testid="stVerticalBlock"],
.st-key-folio_header [data-testid="stElementContainer"],
.st-key-folio_header [data-testid="stMarkdown"],
.st-key-folio_header [data-testid="stMarkdownContainer"] {
    gap: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.st-key-folio_header [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.st-key-folio_header [data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 0 !important;
}

/* Force button text visible/sized on dark header -- Streamlit wraps
   button text in p/div/span, and those inner elements carry their
   own explicit color/font-size that wins over what's set on the
   button itself, so both need to be forced together. */
.st-key-folio_header button p,
.st-key-folio_header button div,
.st-key-folio_header button span {
    color: inherit !important;
    font-size: inherit !important;
}

.st-key-folio_header_nav {
    align-items: center !important;
    display: flex !important;
    flex: 0 1 auto !important;
    flex-direction: row !important;
    gap: 18px !important;
    justify-content: flex-end !important;
    min-width: 0 !important;
    width: auto !important;
}

.st-key-folio_header_nav [data-testid="stVerticalBlock"] {
    align-items: center !important;
    display: flex !important;
    flex-direction: row !important;
    gap: 18px !important;
    justify-content: flex-end !important;
}

.st-key-folio_header_nav [data-testid="stElementContainer"] {
    flex: 0 0 auto !important;
    width: auto !important;
}

.st-key-folio_header_nav [data-testid="stElementContainer"] + [data-testid="stElementContainer"] {
    margin-left: 18px !important;
}

/* Header nav buttons (dark bg) */
.st-key-folio_header_nav .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: rgba(225, 234, 255, 0.82) !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    height: 36px !important;
    line-height: 1 !important;
    min-height: 36px !important;
    padding: 6px 0 !important;
    position: relative;
    transform: none !important;
    transition: background 0.14s, color 0.14s !important;
    white-space: nowrap !important;
}

.st-key-folio_header_nav .stButton > button:hover {
    background: transparent !important;
    color: #ffffff !important;
    transform: none !important;
}

.st-key-folio_header_nav .stButton > button::after {
    background: rgba(255, 255, 255, 0.72);
    bottom: 3px;
    content: "";
    height: 1px;
    left: 50%;
    position: absolute;
    transform: translateX(-50%) scaleX(0);
    transition: transform 0.16s ease;
    width: 100%;
}

.st-key-folio_header_nav .stButton > button:hover::after {
    transform: translateX(-50%) scaleX(1);
}

/* Active nav button — rendered as disabled, styled as selected */
.st-key-folio_header_nav .stButton > button:disabled {
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    cursor: default !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

.st-key-folio_header_nav .stButton > button:disabled::after {
    transform: translateX(-50%) scaleX(1);
}

/* Brand group: logo + invisible "홈으로 이동" hit-target, stacked in
   one small relative wrapper. Both are exactly 34px tall, so the
   overlay only needs top:0 -- no centering math required since the
   two heights match exactly. */
.st-key-folio_header_brand {
    height: 34px;
    position: relative;
}

.folio-header-logo {
    align-items: center;
    display: flex;
    height: 34px;
    width: fit-content;
}

.folio-header-logo img {
    display: block;
    height: 24px;
    object-fit: contain;
    width: auto;
}

.st-key-folio_header .st-key-nav_brand_home {
    height: 34px;
    left: 0;
    position: absolute;
    top: 0;
    width: 76px;
    z-index: 1;
}

.st-key-folio_header .st-key-nav_brand_home button {
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    height: 34px !important;
    min-height: 34px !important;
    padding: 0 !important;
    width: 76px !important;
}

.st-key-folio_header .st-key-nav_brand_home button p,
.st-key-folio_header .st-key-nav_brand_home button div,
.st-key-folio_header .st-key-nav_brand_home button span {
    color: transparent !important;
}

.st-key-folio_header .st-key-nav_brand_home button:hover {
    background: transparent !important;
    transform: none !important;
}

@media (max-width: 640px) {
    .st-key-folio_header {
        align-items: stretch !important;
        flex-direction: column !important;
        gap: 8px !important;
        justify-content: center !important;
        min-height: 92px !important;
        padding: 0 14px !important;
    }

    .st-key-folio_header_brand {
        height: 28px;
    }

    .folio-header-logo,
    .st-key-folio_header .st-key-nav_brand_home,
    .st-key-folio_header .st-key-nav_brand_home button {
        height: 28px !important;
    }

    .folio-header-logo img {
        height: 22px;
    }

    .st-key-folio_header_nav [data-testid="stVerticalBlock"] {
        gap: 12px !important;
        justify-content: flex-start !important;
        overflow-x: auto !important;
        scrollbar-width: none;
        width: 100% !important;
    }

    .st-key-folio_header_nav {
        gap: 12px !important;
        overflow-x: auto !important;
        scrollbar-width: none;
        width: 100% !important;
    }

    .st-key-folio_header_nav::-webkit-scrollbar,
    .st-key-folio_header_nav [data-testid="stVerticalBlock"]::-webkit-scrollbar {
        display: none;
    }

    .st-key-folio_header_nav [data-testid="stElementContainer"] + [data-testid="stElementContainer"] {
        margin-left: 12px !important;
    }

    .st-key-folio_header_nav .stButton > button {
        font-size: 0.82rem !important;
        height: 30px !important;
        min-height: 30px !important;
    }
}

@media (max-width: 420px) {
    .st-key-folio_header {
        padding: 0 12px !important;
    }

    .folio-header-logo img {
        height: 22px;
    }

    .st-key-folio_header_nav [data-testid="stVerticalBlock"] {
        gap: 9px !important;
    }

    .st-key-folio_header_nav {
        gap: 9px !important;
    }

    .st-key-folio_header_nav [data-testid="stElementContainer"] + [data-testid="stElementContainer"] {
        margin-left: 9px !important;
    }

    .st-key-folio_header_nav .stButton > button {
        font-size: 0.76rem !important;
    }
}
"""
