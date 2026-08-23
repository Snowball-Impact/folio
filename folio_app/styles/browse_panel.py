"""Home page search/tag/sort panel (folio_browse_panel container)."""

CSS = """
/* ── Browse Panel ── */
.folio-search-container {
    align-items: center;
    display: grid;
    grid-template-columns: 36px minmax(0, 1fr) 36px;
    margin-bottom: 12px;
    min-height: 36px;
    position: relative;
    text-align: center;
}

.folio-search-heading {
    grid-column: 2;
    min-width: 0;
}

.st-key-folio_browse_panel .folio-search-title {
    color: var(--folio-navy);
    font-size: 32px !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    line-height: 1.25 !important;
    margin: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
}

.st-key-folio_browse_panel .folio-search-title-count {
    color: var(--folio-blue);
    display: inline-block;
    font-size: 1.08em;
    font-weight: 900;
    min-width: 2.2ch;
    text-align: right;
}

.st-key-folio_browse_panel {
    background: #f3f7ff !important;
    border: 1px solid rgba(188, 207, 236, 0.58) !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    margin: 28px 0 0 !important;
    padding: 26px 42px 24px !important;
}

.folio-home-loading-panel {
    background: #f3f7ff;
    border: 1px solid rgba(188, 207, 236, 0.58);
    border-radius: 12px;
    margin: 28px 0 0;
    padding: 30px 42px 28px;
    text-align: center;
}

.folio-home-loading-panel h1 {
    color: var(--folio-navy);
    font-size: 30px !important;
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    line-height: 1.25 !important;
    margin: 0 0 8px !important;
}

.folio-home-loading-panel p {
    color: var(--folio-muted);
    font-size: 0.94rem;
    margin: 0 0 22px;
}

.folio-home-loading-search,
.folio-home-loading-tags span,
.folio-home-loading-rail strong,
.folio-home-loading-rail span {
    animation: folio-loading-pulse 1.35s ease-in-out infinite;
    background: linear-gradient(90deg, #e6eefb 0%, #f8fbff 48%, #e6eefb 100%);
    background-size: 220% 100%;
}

.folio-home-loading-search {
    border: 1px solid var(--folio-border);
    border-radius: 10px;
    height: 42px;
    margin: 0 auto 16px;
    max-width: 920px;
}

.folio-home-loading-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
}

.folio-home-loading-tags span {
    border-radius: 999px;
    display: inline-flex;
    height: 32px;
    width: 92px;
}

.folio-home-loading-rail {
    margin-top: 22px;
}

.folio-home-loading-rail strong {
    border-radius: 999px;
    display: block;
    height: 24px;
    margin: 0 auto 14px;
    width: min(360px, 72%);
}

.folio-home-loading-rail div {
    display: grid;
    gap: 14px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.folio-home-loading-rail span {
    border: 1px solid rgba(188, 207, 236, 0.58);
    border-radius: 8px;
    display: block;
    min-height: 132px;
}

@keyframes folio-loading-pulse {
    0% {
        background-position: 120% 0;
    }
    100% {
        background-position: -120% 0;
    }
}

.st-key-folio_browse_panel > [data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

.st-key-folio_browse_panel .stTextInput div[data-baseweb="input"] {
    align-items: center !important;
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 10px !important;
    box-sizing: border-box !important;
    display: flex !important;
    height: 42px !important;
    min-height: 42px !important;
}

.st-key-folio_browse_panel .stTextInput > div > div > input {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
    height: 40px !important;
    line-height: 40px !important;
    min-height: 40px !important;
    padding: 0 16px !important;
}

.st-key-folio_browse_panel .stTextInput div[data-baseweb="input"]:focus-within {
    background: var(--folio-surface) !important;
    border-color: var(--folio-blue) !important;
    box-shadow: 0 0 0 3px rgba(20, 89, 200, 0.1) !important;
}

.st-key-folio_browse_panel [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 10px !important;
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

.st-key-folio_browse_panel [data-testid="stForm"] > div {
    gap: 10px !important;
}

.st-key-home_platform_filters {
    margin: 0 0 2px;
    padding: 0 2px;
}

.st-key-home_platform_filters .stRadio > div {
    align-items: center;
    column-gap: 18px;
    flex-wrap: wrap;
    row-gap: 4px;
}

.st-key-home_platform_filters .stRadio label {
    align-items: center;
    color: var(--folio-navy);
    display: inline-flex;
    font-size: 0.84rem;
    font-weight: 700;
    min-height: 24px;
    padding: 0;
}

.st-key-home_platform_filters .stRadio label:has(input:checked) {
    color: var(--folio-blue);
}

.st-key-home_platform_filters .stRadio p {
    align-items: center;
    display: inline-flex;
    font-size: inherit !important;
    font-weight: inherit !important;
    line-height: 18px !important;
    margin: 0 !important;
    min-height: 18px;
    white-space: nowrap;
}

.st-key-folio_browse_panel .folio-popular-tag-label {
    align-items: center;
    background: rgba(20, 89, 200, 0.08);
    border: 1px solid rgba(20, 89, 200, 0.14);
    border-radius: 999px;
    box-sizing: border-box;
    color: #1459c8;
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 800;
    height: 32px;
    justify-content: center;
    line-height: 1;
    padding: 0 12px;
    white-space: nowrap;
    width: 100%;
}

.st-key-folio_browse_panel .stFormSubmitButton > button[kind="primaryFormSubmit"] {
    background: var(--folio-blue) !important;
    border-color: var(--folio-blue) !important;
    color: #ffffff !important;
    min-height: 42px !important;
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
        margin: 22px 0 9px !important;
        padding: 22px 18px 20px !important;
    }

    .folio-home-loading-panel {
        margin: 22px 0 9px;
        padding: 24px 18px 22px;
    }

    .folio-home-loading-panel h1 {
        font-size: 18px !important;
        line-height: 1.45 !important;
    }

    .folio-home-loading-rail div {
        grid-template-columns: 1fr;
    }

    .folio-home-loading-rail span:nth-child(n+2) {
        display: none;
    }

    .folio-search-container {
        align-items: flex-start;
    }

    .st-key-folio_browse_panel .folio-search-title {
        font-size: 15px !important;
        line-height: 1.45 !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: normal !important;
    }

    .folio-popular-tag-label {
        margin-top: 2px;
        width: auto;
    }

    .st-key-folio_browse_panel [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }

    .st-key-folio_browse_panel [data-testid="stColumn"] {
        width: 100% !important;
    }
}
"""
