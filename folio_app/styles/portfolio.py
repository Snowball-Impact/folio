"""My Portfolio page item cards (portfolio_item_<id> containers)."""

CSS = """
/* ── Portfolio item cards ── */
.folio-portfolio-card {
    align-items: stretch;
    background: var(--folio-surface);
    border: 0;
    border-radius: 0;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 4px;
    max-width: 100%;
    min-width: 0;
    padding: 12px 12px 16px;
    width: 100%;
}

[class*="st-key-portfolio_item_"] {
    background: var(--folio-surface);
    border-color: var(--folio-border) !important;
    border-radius: 14px !important;
    box-sizing: border-box !important;
    margin-bottom: 14px;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: clip;
    padding: 16px 18px !important;
    width: 100% !important;
}

[class*="st-key-portfolio_item_"] [data-testid="stHorizontalBlock"],
[class*="st-key-portfolio_item_"] [data-testid="stColumn"],
[class*="st-key-portfolio_item_"] [data-testid="stElementContainer"] {
    box-sizing: border-box !important;
    max-width: 100% !important;
    min-width: 0 !important;
}

.folio-portfolio-card-main {
    min-width: 0;
}

.folio-portfolio-card-footer {
    align-items: flex-start;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-width: 100%;
    min-width: 0;
    width: 100%;
    overflow: hidden;
}

.folio-portfolio-card-footer .folio-tags {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 6px;
    margin: 0;
    width: 100%;
    min-width: 0;
    box-sizing: border-box;
}

.folio-portfolio-card-title {
    color: var(--folio-navy);
    font-size: 0.98rem;
    font-weight: 700;
    margin: 0 0 5px;
    word-break: keep-all;
}

.folio-portfolio-card-liner {
    color: var(--folio-muted);
    font-size: 0.86rem;
    line-height: 1.5;
    margin: 0 0 8px;
    word-break: keep-all;
}

.folio-portfolio-card-meta {
    align-items: center;
    color: var(--folio-muted);
    display: flex;
    flex-wrap: wrap;
    font-size: 0.82rem;
    gap: 12px;
    justify-content: flex-start;
    margin: 0;
}

.folio-portfolio-card-meta span {
    align-items: center;
    display: inline-flex;
    gap: 4px;
}

.folio-portfolio-card-meta svg {
    fill: none;
    height: 16px;
    stroke: currentColor;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-width: 1.8;
    width: 16px;
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .folio-portfolio-card {
        gap: 12px;
    }

    .folio-portfolio-card-footer {
        align-items: flex-start;
    }

    .folio-portfolio-card-footer .folio-tags,
    .folio-portfolio-card-meta {
        justify-content: flex-start;
    }

    [class*="st-key-portfolio_item_"] [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }

    [class*="st-key-portfolio_item_"] [data-testid="stColumn"] {
        width: 100% !important;
    }

    [class*="st-key-portfolio_item_"] [data-testid="stColumn"]:last-child {
        margin-top: 10px;
    }

    [class*="st-key-portfolio_item_"] [data-testid="stColumn"]:last-child [data-testid="stVerticalBlock"] {
        display: flex;
        flex-direction: row;
        gap: 8px;
    }

    [class*="st-key-portfolio_item_"] [data-testid="stColumn"]:last-child [data-testid="stElementContainer"] {
        flex: 1;
    }
}
"""
