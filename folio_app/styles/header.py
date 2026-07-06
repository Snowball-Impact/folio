"""Sticky top navigation header: brand, nav buttons, login button, menu popover."""

CSS = """
/* ── Header (light) ──
   The header has exactly two real (in-flow) children: the brand
   group (logo + invisible "홈으로 이동" hit-target) and the login
   button / menu popover. Plain flexbox (row + space-between +
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
    padding: 0 20px !important;
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
.st-key-folio_header .stButton,
.st-key-folio_header [data-testid="stPopover"] {
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

/* Header nav buttons (dark bg) */
.st-key-folio_header .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: rgba(200, 215, 255, 0.75) !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    min-height: 34px !important;
    padding: 5px 10px !important;
    transform: none !important;
    transition: background 0.14s, color 0.14s !important;
}

.st-key-folio_header .stButton > button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    transform: none !important;
}

/* Active nav button — rendered as disabled, styled as selected */
.st-key-folio_header .stButton > button:disabled {
    background: rgba(255, 255, 255, 0.12) !important;
    border: none !important;
    color: #ffffff !important;
    cursor: default !important;
    font-weight: 700 !important;
    opacity: 1 !important;
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

/* Login button (logged-out state) -- an ordinary flex item now,
   vertically centered by the header's own align-items:center. */
.st-key-folio_header .st-key-nav_Login button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: rgba(225, 234, 255, 0.86) !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    height: 36px !important;
    line-height: 1 !important;
    min-height: 36px !important;
    padding: 6px 2px !important;
    position: relative;
}

.st-key-folio_header .st-key-nav_Login button:hover {
    background: transparent !important;
    color: #ffffff !important;
    transform: none !important;
}

.st-key-folio_header .st-key-nav_Login button::after {
    background: rgba(255, 255, 255, 0.72);
    bottom: 3px;
    content: "";
    height: 1px;
    left: 50%;
    position: absolute;
    transform: translateX(-50%) scaleX(0);
    transition: transform 0.16s ease;
    width: calc(100% - 4px);
}

.st-key-folio_header .st-key-nav_Login button:hover::after {
    transform: translateX(-50%) scaleX(1);
}

/* Menu popover trigger (logged-in state) -- also an ordinary flex
   item, same as the login button above. */
.st-key-folio_header [data-testid="stPopover"] > button,
.st-key-folio_header button[data-testid="stPopoverButton"],
.st-key-folio_header [data-testid="stPopoverButton"] > button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: #ffffff !important;
    font-size: 1.4rem !important;
    font-weight: 400 !important;
    height: 36px !important;
    line-height: 1 !important;
    min-height: 36px !important;
    min-width: 36px !important;
    padding: 4px 0 !important;
    transform: none !important;
    transition: color 0.15s ease, opacity 0.15s ease !important;
    width: 36px !important;
}

.st-key-folio_header [data-testid="stPopover"] > button *,
.st-key-folio_header button[data-testid="stPopoverButton"] *,
.st-key-folio_header [data-testid="stPopoverButton"] > button * {
    color: #ffffff !important;
    fill: currentColor !important;
}

.st-key-folio_header [data-testid="stPopover"] > button:hover,
.st-key-folio_header button[data-testid="stPopoverButton"]:hover,
.st-key-folio_header [data-testid="stPopoverButton"] > button:hover {
    background: transparent !important;
    color: #ffffff !important;
    opacity: 1;
}

/* Hide dropdown arrow from popover trigger in header. Streamlit 1.58
   wraps the button's label and arrow in an extra div, so the arrow
   is two levels down, not a direct child of the button. */
.st-key-folio_header [data-testid="stPopoverButton"] > div > div:last-child {
    display: none !important;
}
"""
