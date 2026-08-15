"""Design tokens and app-level base styles."""

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

h1, h2, h3 {
    color: var(--folio-navy);
    letter-spacing: -0.01em;
}

/* ── Footer ── */
.folio-footer {
    align-items: center;
    border-top: 1px solid var(--folio-border);
    color: var(--folio-muted);
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    gap: 16px;
    font-size: 13px;
    margin-top: 52px;
    padding: 22px 0;
}

.folio-footer-copy {
    justify-self: start;
    margin: 0;
    min-width: 0;
}

.folio-footer-links {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    justify-content: flex-end;
    justify-self: end;
    margin-top: 0;
    text-align: right;
}

.folio-footer-links a,
.folio-footer-links span,
.folio-footer-version {
    color: var(--folio-muted);
    font-size: 12px;
    text-decoration: none;
}

.folio-footer-version {
    font-weight: 700;
    justify-self: center;
    letter-spacing: 0;
    white-space: nowrap;
}

.folio-footer-links a:hover {
    color: var(--folio-blue);
    text-decoration: underline;
}

@media (max-width: 720px) {
    .folio-footer {
        grid-template-columns: 1fr;
        justify-items: center;
        text-align: center;
    }

    .folio-footer-links {
        justify-content: center;
        justify-self: center;
        text-align: center;
    }

    .folio-footer-copy,
    .folio-footer-version {
        justify-self: center;
    }
}

"""
