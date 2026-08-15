"""Power BI news page styles."""

CSS = """
.folio-powerbi-hero-shell {
    margin-top: -8px;
}

.folio-powerbi-hero {
    background: linear-gradient(135deg, #fff8dc 0%, #ffffff 48%, #eaf7f4 100%);
    border: 1px solid rgba(214, 176, 50, 0.32);
    border-radius: 8px;
    display: grid;
    gap: 20px;
    grid-template-columns: minmax(0, 1fr) auto;
    min-height: 230px;
    margin: 0 0 18px;
    padding: 30px 34px;
}

.folio-powerbi-eyebrow {
    color: #806100;
    font-size: 0.78rem;
    font-weight: 900;
    letter-spacing: 0.1em;
    margin: 0 0 10px;
    text-transform: uppercase;
}

.folio-powerbi-hero h1 {
    color: var(--folio-navy);
    font-size: 2.05rem;
    font-weight: 850;
    letter-spacing: 0;
    line-height: 1.22;
    margin: 0;
}

.folio-powerbi-hero p {
    color: var(--folio-muted);
    font-size: 1rem;
    line-height: 1.72;
    margin: 12px 0 0;
    max-width: 720px;
    word-break: keep-all;
}

.folio-powerbi-hero-cta {
    align-items: center;
    background: var(--folio-blue);
    border: 1px solid var(--folio-blue);
    border-radius: 8px;
    color: #ffffff !important;
    display: inline-flex;
    font-size: 0.92rem;
    font-weight: 400;
    justify-content: center;
    line-height: 1;
    margin-top: 20px;
    min-height: 42px;
    padding: 0 16px;
    text-decoration: none !important;
}

.folio-powerbi-hero-cta:hover {
    background: #0f49a8;
    border-color: #0f49a8;
    color: #ffffff !important;
    text-decoration: none !important;
}

.folio-powerbi-hero-visual {
    align-items: center;
    display: flex;
    justify-content: center;
    min-width: 240px;
}

.folio-powerbi-hero-visual img {
    display: block;
    height: auto;
    max-height: 170px;
    max-width: 390px;
    object-fit: contain;
    width: auto;
}

.folio-powerbi-expander-title {
    color: var(--folio-navy);
}

.folio-powerbi-release-row {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    margin: 3px 0;
}

.folio-powerbi-release-row summary {
    align-items: center;
    cursor: pointer;
    display: grid;
    gap: 10px;
    grid-template-columns: auto 38px 128px minmax(0, 1fr) auto;
    justify-content: space-between;
    min-height: 34px;
    padding: 4px 10px;
}

.folio-powerbi-release-row summary::-webkit-details-marker {
    display: none;
}

.folio-powerbi-release-row summary::before {
    color: var(--folio-muted);
    content: ">";
    flex: 0 0 auto;
    font-size: 18px;
    line-height: 1;
    transform: rotate(0deg);
    transition: transform 0.14s ease;
}

.folio-powerbi-release-row[open] summary::before {
    transform: rotate(90deg);
}

.folio-powerbi-release-row .folio-powerbi-expander-title {
    font-size: 0.92rem;
    font-weight: 850;
    min-width: 0;
    text-align: left;
}

.folio-powerbi-row-label {
    align-items: center;
    background: #f7faff;
    border: 1px solid rgba(20, 89, 200, 0.18);
    border-radius: 999px;
    color: #315783;
    display: inline-flex;
    font-size: 0.74rem;
    font-weight: 850;
    justify-content: center;
    line-height: 1;
    padding: 5px 8px;
    width: 128px;
    white-space: nowrap;
}

.folio-powerbi-row-index {
    color: var(--folio-muted);
    font-size: 0.78rem;
    font-weight: 850;
    text-align: right;
}

.folio-powerbi-release-body {
    border-top: 1px solid rgba(220, 229, 247, 0.82);
    padding: 6px 12px 7px 30px;
}

.folio-powerbi-summary-list {
    color: #263f63;
    display: grid;
    gap: 3px;
    font-size: 0.88rem;
    line-height: 1.42;
    list-style-position: outside;
    margin: 0 0 3px 18px;
    padding: 0;
    word-break: keep-all;
}

.folio-powerbi-summary-list li {
    padding-left: 2px;
}

.folio-powerbi-link {
    align-items: center;
    background: #eaf2ff;
    border: 1px solid rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-blue) !important;
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 850;
    flex: 0 0 auto;
    min-height: 24px;
    padding: 0 8px;
    text-decoration: none !important;
}

.folio-powerbi-link:hover {
    background: #dceaff;
    border-color: rgba(20, 89, 200, 0.42);
    text-decoration: none !important;
}

.folio-powerbi-page-indicator {
    align-items: center;
    color: var(--folio-muted);
    display: flex;
    font-size: 0.86rem;
    font-weight: 850;
    justify-content: center;
    min-height: 36px;
}

.st-key-powerbi_news_prev button,
.st-key-powerbi_news_next button {
    align-items: center !important;
    background: transparent !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 999px !important;
    box-shadow: none !important;
    color: var(--folio-navy) !important;
    display: inline-flex !important;
    font-family: Arial, sans-serif !important;
    font-size: 18px !important;
    font-weight: 850 !important;
    height: 32px !important;
    justify-content: center !important;
    line-height: 1 !important;
    margin: 2px auto 0 !important;
    min-height: 32px !important;
    padding: 0 !important;
    width: 32px !important;
}

.st-key-powerbi_news_prev button p,
.st-key-powerbi_news_next button p {
    color: var(--folio-navy) !important;
    font-family: Arial, sans-serif !important;
    font-size: 18px !important;
    font-weight: 850 !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.st-key-powerbi_news_prev button:hover,
.st-key-powerbi_news_next button:hover {
    background: #eaf2ff !important;
    border-color: rgba(20, 89, 200, 0.28) !important;
    transform: none !important;
}

.folio-powerbi-empty {
    background: rgba(255, 255, 255, 0.74);
    border: 1px dashed var(--folio-border);
    border-radius: 8px;
    color: var(--folio-muted);
    font-size: 0.95rem;
    padding: 18px;
}

@media (max-width: 820px) {
    .folio-powerbi-hero {
        grid-template-columns: 1fr;
        padding: 24px 20px;
    }

    .folio-powerbi-hero-visual {
        justify-content: flex-start;
        min-width: 0;
    }

    .folio-powerbi-hero-visual img {
        max-height: 120px;
        max-width: 320px;
    }
}
"""
