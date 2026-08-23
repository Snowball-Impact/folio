"""Global overrides for Streamlit's generated app shell and helper iframes."""

CSS = """
section[data-testid="stSidebar"],
header[data-testid="stHeader"],
footer[data-testid="stFooter"] {
    display: none;
}

/* Hide EncryptedCookieManager's invisible sync iframe. The
   auto-generated wrapper class this used to target (from Streamlit
   1.41) no longer matches under 1.58, so the iframe stopped being
   hidden -- its explicit height=0 doesn't stop its wrapping div from
   reserving inline line-height space (~25px) for it, which is what
   showed up as a gap above the header once logged in (that's the
   only state where this component actively re-syncs and its
   wrapper picks up real dimensions). Target it by title/src instead
   of the unstable generated class so this survives future upgrades. */
iframe[title*="CookieManager"],
iframe[src*="cookie_manager"] {
    border: 0 !important;
    height: 0 !important;
    min-height: 0 !important;
    width: 0 !important;
}

/* Hiding the iframe alone isn't enough: its wrapping element-container
   is still a top-level flex child of the main content block, so even
   empty it can consume one gap unit while the component initializes.
   Keep the wrapper mounted, but remove it from normal flow. */
.st-key-CookieManager-sync_cookies,
div:has(> iframe[title*="CookieManager"]),
div:has(> iframe[src*="cookie_manager"]),
[data-testid="stElementContainer"]:has(iframe[title*="CookieManager"]),
[data-testid="stElementContainer"]:has(iframe[src*="cookie_manager"]) {
    height: 0 !important;
    margin: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
    position: absolute !important;
    visibility: hidden !important;
    width: 0 !important;
}

/* Script-only components are rendered as zero-height iframes, but the
   Streamlit element wrapper around them can still contribute flex gap
   during a rerun. Keep those wrappers out of normal flow so route changes
   do not push the sticky header and first hero down for a few frames. */
iframe[height="0"],
iframe[style*="height: 0px"],
iframe[style*="height:0px"],
iframe[title="st.iframe"]:not([src]) {
    border: 0 !important;
    height: 0 !important;
    min-height: 0 !important;
    width: 0 !important;
}

div:has(> iframe[height="0"]),
div:has(> iframe[style*="height: 0px"]),
div:has(> iframe[style*="height:0px"]),
[data-testid="stElementContainer"]:has(iframe[title="st.iframe"]:not([src])),
[data-testid="stElementContainer"]:has(iframe[height="0"]),
[data-testid="stElementContainer"]:has(iframe[style*="height: 0px"]),
[data-testid="stElementContainer"]:has(iframe[style*="height:0px"]) {
    height: 0 !important;
    margin: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
    position: absolute !important;
    visibility: hidden !important;
    width: 0 !important;
}

.block-container {
    margin-left: auto !important;
    margin-right: auto !important;
    max-width: 1440px;
    min-height: 100vh;
    padding-top: 0 !important;
    /* section.stMain is a column flexbox with align-items:center, so
       without an explicit width this shrinks to whatever content has
       streamed in so far and re-centers (growing) as more arrives --
       that width change reflows wrapped text and reads as a vertical
       jump. Stretch it to full width from the first frame instead. */
    width: 100% !important;
    align-self: stretch !important;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
}

section.stMain {
    padding-top: 0 !important;
    scrollbar-gutter: stable;
    overflow-anchor: none;
}

.block-container,
[data-testid="stAppViewContainer"],
.stApp {
    overflow-anchor: none;
}
"""
