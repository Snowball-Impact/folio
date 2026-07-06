"""Home page search/tag/sort panel (folio_browse_panel container)."""

CSS = """
/* ── Browse Panel ── */
.folio-search-container {
    align-items: flex-end;
    display: flex;
    justify-content: space-between;
    margin-bottom: 18px;
}

.folio-search-title {
    color: var(--folio-navy);
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.02em;
}

.folio-search-subtitle {
    color: var(--folio-muted);
    font-size: 0.85rem;
    line-height: 1.45;
    margin-top: 3px;
    word-break: keep-all;
}

.folio-search-count {
    color: var(--folio-muted);
    font-size: 0.88rem;
    font-weight: 700;
    padding-bottom: 2px;
}

.st-key-folio_browse_panel {
    background: #eaf1ff !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    margin: 28px 0 24px !important;
    padding: 26px 28px 24px !important;
}

.st-key-folio_browse_panel > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.st-key-folio_browse_panel .stTextInput > div > div > input {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 10px !important;
    min-height: 46px;
    padding: 12px 16px !important;
}

.st-key-folio_browse_panel .stTextInput > div > div > input:focus {
    background: var(--folio-surface) !important;
    border-color: var(--folio-blue) !important;
    box-shadow: 0 0 0 3px rgba(20, 89, 200, 0.1) !important;
}

.st-key-folio_browse_panel [data-testid="stHorizontalBlock"] {
    align-items: flex-end;
    gap: 14px !important;
}

.st-key-folio_browse_panel .stButton > button {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    color: var(--folio-muted);
    font-size: 0.84rem;
    font-weight: 600;
    min-height: 38px;
    padding: 0 14px;
}

.st-key-folio_browse_panel .stFormSubmitButton > button[kind="primaryFormSubmit"] {
    background: var(--folio-blue) !important;
    border-color: var(--folio-blue) !important;
    color: #ffffff !important;
    min-height: 46px !important;
}

.st-key-folio_browse_panel .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
    background: #0e42a8 !important;
    border-color: #0e42a8 !important;
    color: #ffffff !important;
}

.st-key-folio_browse_panel .stFormSubmitButton > button[kind="secondaryFormSubmit"] {
    background: transparent !important;
    border-color: transparent !important;
    color: var(--folio-muted) !important;
    padding-inline: 8px !important;
}

.st-key-folio_browse_panel .stButton > button:hover {
    background: var(--folio-subtle);
    border-color: #b8d0f0;
    color: var(--folio-blue);
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .st-key-folio_browse_panel {
        margin: 22px 0 18px !important;
        padding: 22px 18px 20px !important;
    }

    .folio-search-container {
        align-items: flex-start;
    }
}
"""
