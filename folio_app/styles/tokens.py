"""Design tokens and global page-level resets."""

CSS = """
/* ── Design Tokens ── */
:root {
    --folio-navy:   #0b1f3f;
    --folio-blue:   #1459c8;
    --folio-mint:   #0a9485;
    --folio-bg:     #f4f7fd;
    --folio-surface:#ffffff;
    --folio-border: #dce5f7;
    --folio-muted:  #5c6f8a;
    --folio-subtle: #eef3fd;
}

/* ── Global ── */
.stApp {
    background: var(--folio-bg);
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

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
    display: none !important;
}

/* Hiding the iframe alone isn't enough: its wrapping element-container
   is still a top-level flex child of the main content block, so even
   empty it still consumes one `gap` unit above/below it. When logged
   in, the cookie manager syncs (read + write), rendering this wrapper
   twice, which doubled the visible gap above the header. Removing the
   wrapper itself (not just its iframe) takes it out of the flex flow
   entirely so it stops contributing gap at all. */
div:has(> iframe[title*="CookieManager"]),
div:has(> iframe[src*="cookie_manager"]),
[data-testid="stElementContainer"]:has(> div > iframe[title*="CookieManager"]),
[data-testid="stElementContainer"]:has(> div > iframe[src*="cookie_manager"]) {
    display: none !important;
}

.block-container {
    max-width: 1280px;
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

h1, h2, h3 {
    color: var(--folio-navy);
    letter-spacing: -0.01em;
}

/* ── Footer ── */
.folio-footer {
    border-top: 1px solid var(--folio-border);
    color: var(--folio-muted);
    font-size: 0.82rem;
    margin-top: 52px;
    padding: 22px 0;
    text-align: center;
}
"""
