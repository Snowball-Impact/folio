"""Reference library page styles."""

CSS = """
.folio-reference-hero-shell {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 16px;
    color: var(--folio-navy);
    display: grid;
    gap: 18px;
    grid-template-columns: minmax(0, 1.1fr) minmax(420px, 0.72fr);
    margin: 24px 0 22px;
    min-height: 220px;
    padding: 28px 42px 34px;
}

.folio-reference-hero-copy {
    align-items: flex-start;
    display: flex;
    flex: 1 1 auto;
    flex-direction: column;
    gap: 12px;
    min-width: 0;
}

.folio-reference-hero-copy .folio-page-hero-eyebrow {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    line-height: 1;
    margin: 0;
}

.folio-reference-hero-copy h1.folio-reference-hero-title {
    color: var(--folio-navy);
    font-size: 2.45rem;
    font-weight: 800;
    letter-spacing: 0;
    line-height: 1.22;
    margin: 0;
    max-width: none;
    text-wrap: nowrap;
    white-space: nowrap;
    word-break: keep-all;
}

.folio-reference-hero-copy h1.folio-reference-hero-title .folio-reference-hero-count {
    color: var(--folio-blue);
    display: inline-block;
    min-width: 1.8ch;
}

.folio-reference-hero-title-text {
    color: var(--folio-navy);
}

.folio-reference-hero-copy p {
    color: var(--folio-muted);
    font-size: 0.98rem;
    line-height: 1.65;
    margin: 0;
    max-width: 460px;
    word-break: keep-all;
}

.folio-reference-hero-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 16px;
}

.folio-reference-hero-tab {
    align-items: center;
    background: #f7faff;
    border: 1px solid rgba(147, 170, 207, 0.56);
    border-radius: 999px;
    color: #18345f !important;
    display: inline-flex;
    font-size: 14px;
    font-weight: 800;
    min-height: 34px;
    padding: 0 13px;
    text-decoration: none !important;
    transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease;
}

.folio-reference-hero-tab:hover,
.folio-reference-hero-tab.is-active {
    background: #eaf2ff;
    border-color: var(--folio-blue);
    color: var(--folio-blue) !important;
}

.folio-reference-hero-visual {
    align-items: flex-end;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 0;
    min-width: 0;
}

.folio-reference-hero-logo {
    align-items: center;
    display: flex;
    flex: 1 1 auto;
    justify-content: flex-end;
    min-height: 148px;
    width: 100%;
}

.folio-reference-hero-logo img.folio-reference-logo-image {
    display: block;
    height: auto;
    max-height: 170px;
    max-width: 390px;
    object-fit: contain;
    width: auto;
}

.folio-reference-hero-logo img.folio-reference-logo-image-datastudio,
.folio-reference-hero-logo img.folio-reference-logo-image-tableau {
    max-height: 152px;
}

.folio-reference-hero-logo img.folio-reference-logo-image-streamlit {
    max-height: 136px;
}

@media (max-width: 1180px) {
    .folio-reference-hero-copy h1.folio-reference-hero-title {
        text-wrap: balance;
        white-space: normal;
    }
}

.folio-reference-grid {
    display: grid;
    gap: 20px;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    margin: 14px 0 44px;
}

.folio-reference-card-slot {
    min-width: 0;
}

.folio-reference-card-slot.is-hidden {
    display: none;
}

.folio-reference-grid .folio-home-card {
    min-height: 0;
}

.folio-reference-grid .folio-home-card:hover {
    box-shadow: 0 22px 48px rgba(11, 31, 63, 0.18);
    transform: translateY(-4px);
}

.folio-reference-loading-sentinel,
.folio-reference-end {
    color: var(--folio-muted);
    font-size: 13px;
    margin: 6px 0 12px;
    min-height: 32px;
    text-align: center;
}

.st-key-reference_load_more_tableau button,
.st-key-reference_load_more_powerbi button,
.st-key-reference_load_more_datastudio button,
.st-key-reference_load_more_streamlit button {
    background: #ffffff !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 8px !important;
    color: var(--folio-blue) !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    min-height: 40px !important;
    margin: 0 0 46px !important;
}

.st-key-reference_load_more_tableau button:hover,
.st-key-reference_load_more_powerbi button:hover,
.st-key-reference_load_more_datastudio button:hover,
.st-key-reference_load_more_streamlit button:hover {
    background: #eaf2ff !important;
    border-color: var(--folio-blue) !important;
}

.st-key-folio_header_nav .st-key-nav_Reference,
.st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] {
    flex: 0 0 auto !important;
    width: auto !important;
}

.st-key-folio_header_nav .st-key-nav_Reference {
    margin-left: 18px !important;
    margin-right: 18px !important;
}

.st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] {
    margin-left: 0 !important;
    margin-right: 0 !important;
}

.st-key-folio_header_nav .st-key-nav_Reference .stPopover > button,
.st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] > button,
.st-key-folio_header_nav .st-key-nav_Reference button {
    align-items: center !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    color: rgba(225, 234, 255, 0.82) !important;
    display: inline-flex !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    gap: 4px !important;
    height: 36px !important;
    line-height: 1 !important;
    min-height: 36px !important;
    padding: 6px 0 !important;
    position: relative !important;
    transform: none !important;
    transition: color 0.14s !important;
    white-space: nowrap !important;
    width: auto !important;
}

.st-key-folio_header_nav .st-key-nav_Reference .stPopover > button:hover,
.st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] > button:hover,
.st-key-folio_header_nav .st-key-nav_Reference button:hover {
    background: transparent !important;
    color: #fff !important;
    transform: none !important;
}

.st-key-folio_header_nav .st-key-nav_Reference .stPopover > button::after,
.st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] > button::after {
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

.st-key-folio_header_nav .st-key-nav_Reference .stPopover > button:hover::after,
.st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] > button:hover::after {
    transform: translateX(-50%) scaleX(1);
}

.st-key-folio_header_nav .st-key-nav_Reference svg {
    color: currentColor !important;
    fill: currentColor !important;
    height: 16px !important;
    opacity: 0.7 !important;
    width: 16px !important;
}

@media (max-width: 860px) {
    .folio-reference-hero-shell {
        grid-template-columns: 1fr;
        min-height: 180px;
        padding: 24px 8px 34px;
    }

    .folio-reference-hero-copy {
        align-items: center;
        text-align: center;
        width: 100%;
    }

    .folio-reference-hero-copy h1.folio-reference-hero-title {
        font-size: 1.9rem;
        text-wrap: balance;
        white-space: normal;
    }

    .folio-reference-hero-copy p {
        text-align: center;
    }

    .folio-reference-hero-visual {
        min-height: 0;
    }

    .folio-reference-hero-logo {
        min-height: 96px;
    }

    .folio-reference-hero-tabs {
        justify-content: center;
    }

    .folio-reference-hero-logo img.folio-reference-logo-image {
        max-height: 120px;
        max-width: 320px;
        width: auto;
    }

    .folio-reference-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .st-key-folio_header_nav .st-key-nav_Reference,
    .st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    .st-key-folio_header_nav .st-key-nav_Reference .stPopover > button,
    .st-key-folio_header_nav .st-key-nav_Reference [data-testid="stPopover"] > button,
    .st-key-folio_header_nav .st-key-nav_Reference button {
        font-size: 0.82rem !important;
        height: 30px !important;
        min-height: 30px !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
    }
}
"""
