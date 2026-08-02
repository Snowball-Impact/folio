"""Detail hero footer action styling."""

CSS = """
/* Hero footer actions styling */
.st-key-folio_hero_footer_actions {
    margin-top: -20px;
    margin-bottom: 21px;
    position: relative;
    z-index: 2;
}

.st-key-folio_hero_footer_actions > div {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-top: none;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 10px 24px rgba(11, 31, 63, 0.05);
    padding: 10px 42px 12px;
    transform: translateY(-3px);
}

.st-key-folio_hero_footer_actions .st-key-detail_footer_row[data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 5px !important;
    flex-wrap: nowrap !important;
    min-height: 36px;
    width: 100%;
}

.st-key-folio_hero_footer_actions .st-key-detail_footer_row [data-testid="stElementContainer"] {
    margin: 0 !important;
}

.st-key-folio_hero_footer_actions .st-key-detail_footer_row[data-testid="stHorizontalBlock"] > [data-testid="stElementContainer"]:first-child {
    flex: 1 1 auto !important;
    min-width: 0;
}

.st-key-folio_hero_footer_actions .st-key-detail_footer_row[data-testid="stHorizontalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stIFrame"]) {
    flex: 0 0 0 !important;
    height: 0 !important;
    min-height: 0 !important;
    min-width: 0 !important;
    overflow: hidden;
    width: 0 !important;
}

.st-key-folio_hero_footer_actions .st-key-detail_footer_row [data-testid="stElementContainer"],
.st-key-folio_hero_footer_actions .st-key-detail_footer_row .stButton,
.st-key-folio_hero_footer_actions .st-key-detail_footer_row [data-testid="stMarkdownContainer"] {
    align-items: center;
    display: flex;
    justify-content: flex-start;
    margin: 0 !important;
    min-height: 36px;
    width: auto;
}

.st-key-folio_hero_footer_actions .st-key-detail_footer_row [data-testid="stCustomComponentV1"],
.st-key-folio_hero_footer_actions .st-key-detail_footer_row iframe {
    display: block;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden;
    width: 0 !important;
}

.st-key-folio_hero_footer_actions .folio-detail-action-group {
    align-items: center;
    display: inline-flex;
    gap: 5px;
    height: 36px;
    justify-content: flex-end;
    white-space: nowrap;
}

.st-key-folio_hero_footer_actions .folio-detail-action-chip,
.st-key-folio_hero_footer_actions .folio-detail-share-button {
    align-items: center;
    background: #ffffff;
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-blue);
    display: inline-flex;
    font-size: 12px;
    font-weight: 700;
    height: 32px;
    justify-content: center;
    line-height: 1;
    min-width: 58px;
    padding: 0 10px;
    white-space: nowrap;
}

.st-key-folio_hero_footer_actions .folio-detail-action-chip.is-public {
    background: #e7f6f2;
    border-color: #d2eee8;
    color: #087568;
}

.st-key-folio_hero_footer_actions .folio-detail-action-chip.is-private {
    background: #edf0f5;
    border-color: #d8dee9;
    color: #65748a;
}

.st-key-folio_hero_footer_actions .folio-detail-share-button {
    cursor: pointer;
    gap: 5px;
    min-width: 88px;
    transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease;
}

.st-key-folio_hero_footer_actions .folio-detail-share-button:hover {
    background: #eef3fd;
    border-color: rgba(20, 89, 200, 0.35);
}

.st-key-folio_hero_footer_actions .folio-detail-share-button svg {
    height: 14px;
    width: 14px;
}

.st-key-folio_hero_footer_actions .folio-detail-summary {
    min-height: 36px;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action {
    align-items: center;
    display: flex;
    height: 36px;
    justify-content: flex-start;
    margin: 0;
    transform: none;
    width: auto;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action .stButton {
    display: flex;
    justify-content: flex-start;
    width: auto !important;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action button {
    height: 32px;
    margin: 0 !important;
    min-height: 32px !important;
    min-width: 88px;
    width: auto !important;
}

/* Like button appearance -- consolidated here since detail_like_action
   only ever renders nested inside folio_hero_footer_actions. */
.st-key-folio_hero_footer_actions .st-key-detail_like_action button {
    align-items: center;
    background: #ffffff;
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-blue);
    display: inline-flex;
    font-size: 12px;
    font-weight: 700;
    justify-content: center;
    padding: 0 10px;
    transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action button:hover {
    background: #eef3fd;
    border-color: rgba(20, 89, 200, 0.35);
    box-shadow: none;
    transform: none;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action [data-testid="stTooltipHoverTarget"] {
    display: flex;
    justify-content: flex-start;
    width: auto !important;
}

@media (max-width: 768px) {
    .st-key-folio_hero_footer_actions {
        margin-bottom: 18px;
        margin-top: -18px;
    }

    .st-key-folio_hero_footer_actions > div {
        padding: 10px 16px 12px;
    }

    .st-key-folio_hero_footer_actions .st-key-detail_footer_row[data-testid="stHorizontalBlock"] {
        align-items: flex-start;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }

    .st-key-folio_hero_footer_actions .st-key-detail_footer_row[data-testid="stHorizontalBlock"] > [data-testid="stElementContainer"]:first-child {
        flex: 1 1 100% !important;
        width: 100% !important;
    }

    .st-key-folio_hero_footer_actions .folio-detail-summary,
    .st-key-folio_hero_footer_actions .folio-detail-meta-row {
        align-items: flex-start;
        flex-direction: column;
        gap: 6px;
        width: 100%;
    }

    .st-key-folio_hero_footer_actions .folio-detail-meta-item {
        padding: 0;
        width: 100%;
    }

    .st-key-folio_hero_footer_actions .folio-detail-meta-item small,
    .st-key-folio_hero_footer_actions .folio-detail-meta-item strong {
        white-space: normal;
        word-break: keep-all;
    }

    .st-key-folio_hero_footer_actions .folio-detail-meta-item::after {
        display: none;
    }

    .st-key-folio_hero_footer_actions .folio-detail-action-group {
        flex-wrap: wrap;
        height: auto;
        justify-content: flex-start;
        white-space: normal;
    }

    .st-key-folio_hero_footer_actions .folio-detail-action-chip,
    .st-key-folio_hero_footer_actions .folio-detail-share-button {
        min-width: 0;
    }

    .st-key-folio_hero_footer_actions .st-key-detail_like_action,
    .st-key-folio_hero_footer_actions .st-key-detail_like_action .stButton {
        height: auto;
        justify-content: flex-start;
    }

    .st-key-folio_hero_footer_actions .st-key-detail_like_action button {
        min-width: 0;
    }
}
"""
