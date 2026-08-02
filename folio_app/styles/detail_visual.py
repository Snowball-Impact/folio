"""Project detail visual/result panel, including embedded dashboard sizing."""

CSS = """
.st-key-project_detail_visual {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 16px !important;
    box-sizing: border-box !important;
    box-shadow: none !important;
    margin-bottom: 18px !important;
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 22px !important;
    width: 100% !important;
}

.folio-visual-heading {
    border-bottom: 1px solid var(--folio-border);
    margin: 0 auto 18px;
    max-width: 900px;
    padding-bottom: 14px;
}

.folio-visual-heading h2 {
    color: var(--folio-navy);
    font-size: 20px;
    font-weight: 800;
    margin: 0;
}

.folio-visual-heading p {
    color: var(--folio-muted);
    font-size: 13px;
    line-height: 1.45;
    margin: 4px 0 0;
    word-break: keep-all;
}

.st-key-project_detail_visual [data-testid="stVerticalBlock"] {
    box-sizing: border-box;
    gap: 12px;
    max-width: 100%;
    min-width: 0;
    width: 100%;
}

.st-key-project_detail_visual [data-testid="stElementContainer"],
.st-key-project_detail_visual [data-testid="stCustomComponentV1"],
.st-key-project_detail_visual .stLinkButton {
    box-sizing: border-box !important;
    max-width: 900px !important;
    min-width: 0 !important;
    width: 100% !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

.st-key-project_detail_visual iframe {
    box-sizing: border-box;
    border-radius: 12px;
    display: block;
    max-width: 100%;
    overflow: hidden;
    width: 100%;
}

.st-key-project_detail_visual [data-testid="stCaptionContainer"] {
    color: var(--folio-muted);
    font-size: 12px;
    line-height: 1.45;
}

.st-key-project_detail_visual .stLinkButton > a {
    background: #ffffff !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    color: var(--folio-navy) !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    min-height: 34px !important;
    transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease !important;
    width: 100% !important;
}

.st-key-project_detail_visual .stLinkButton > a:hover {
    background: rgba(20, 89, 200, 0.05) !important;
    border-color: rgba(20, 89, 200, 0.35) !important;
    color: var(--folio-blue) !important;
}

@media (max-width: 768px) {
    .st-key-project_detail_visual {
        border-radius: 12px !important;
        padding: 18px 16px !important;
    }

    /* Streamlit reserves component height with both height and flex-basis.
       Mobile embeds need both reset so the 16:9 iframe does not leave a
       520px blank reservation below the dashboard. */
    .st-key-project_detail_visual [data-testid="stElementContainer"]:has(> iframe[data-testid="stIFrame"]),
    .st-key-project_detail_visual [data-testid="stCustomComponentV1"] {
        flex: 0 0 auto !important;
        flex-basis: auto !important;
        height: auto !important;
        min-height: 0 !important;
    }

    .st-key-project_detail_visual [data-testid="stElementContainer"]:has(> iframe[data-testid="stIFrame"]) {
        aspect-ratio: 16 / 9;
        overflow: hidden !important;
    }

    .st-key-project_detail_visual iframe {
        aspect-ratio: 16 / 9;
        height: auto !important;
        min-height: 0 !important;
    }
}
"""
