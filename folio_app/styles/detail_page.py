"""Project detail page: meta row, content sections, and the dashboard/attachment sidebar."""

CSS = """
/* ── Project Detail Page Styles ── */

.folio-detail-meta-row {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    width: auto;
}

.folio-detail-summary {
    align-items: center;
    display: flex;
    min-height: 36px;
    width: 100%;
}

.folio-detail-action-meta {
    align-items: center;
    display: flex;
    gap: 6px;
    justify-content: flex-end;
    min-height: 36px;
    width: 100%;
}

.folio-detail-action-chip {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-blue);
    display: inline-flex;
    font-size: 12px;
    font-weight: 700;
    height: 32px;
    justify-content: center;
    line-height: 1;
    min-width: 64px;
    padding: 0 12px;
    white-space: nowrap;
}

.folio-detail-action-chip.is-public { background: #e7f6f2; border-color: #d2eee8; color: #087568; }
.folio-detail-action-chip.is-private { background: #edf0f5; border-color: #d8dee9; color: #65748a; }

.folio-detail-meta-item {
    align-items: center;
    color: var(--folio-muted);
    display: inline-flex;
    font-size: 0.88rem;
    gap: 6px;
    line-height: 1.4;
    padding: 4px 12px;
    position: relative;
}

.folio-detail-meta-item small {
    color: #8a99b3;
    font-size: 0.72rem;
    font-weight: 700;
}

.folio-detail-meta-item strong {
    color: var(--folio-navy);
    font-size: 0.86rem;
    font-weight: 700;
}

.folio-detail-meta-item::after {
    content: "·";
    color: var(--folio-subtle);
    margin-left: 12px;
    position: absolute;
    right: -8px;
}

.folio-detail-meta-item:last-child::after {
    display: none;
}

.folio-detail-author {
    color: var(--folio-navy);
    font-weight: 700;
    font-size: 0.92rem;
    padding-left: 0;
}

/* Unified detail content */
.folio-detail-content-card {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 14px;
    overflow: hidden;
    padding: 8px 28px 18px;
}

.folio-detail-content-heading {
    border-bottom: 1px solid var(--folio-border);
    margin-left: auto;
    margin-right: auto;
    max-width: 900px;
    padding: 18px 0 14px;
}

.folio-detail-content-heading h2 {
    color: var(--folio-navy);
    font-size: 20px;
    font-weight: 800;
    margin: 0;
}

.folio-detail-section {
    border-bottom: 1px solid var(--folio-border);
    margin-left: auto;
    margin-right: auto;
    max-width: 900px;
    padding: 22px 0 24px;
}

.folio-detail-section:last-child { border-bottom: 0; }

.folio-detail-section-content {
    color: var(--folio-navy);
    font-size: 14px;
    line-height: 1.78;
    word-break: keep-all;
}

.folio-detail-section-content p {
    margin: 0 0 12px;
}

.folio-detail-section-content p:last-child {
    margin-bottom: 0;
}

.folio-detail-section-content p:empty {
    display: none;
}

.folio-detail-section-content h3,
.folio-detail-section-content h4,
.folio-detail-section-content h5 {
    color: var(--folio-navy);
    margin: 16px 0 8px;
}

.folio-detail-section-content ul,
.folio-detail-section-content ol {
    margin: 8px 0 12px;
    padding-left: 20px;
}

.folio-detail-section-content li {
    margin: 6px 0;
}

.folio-detail-section-content strong {
    color: var(--folio-navy);
    font-weight: 700;
}

.folio-detail-section-content em {
    color: var(--folio-muted);
    font-style: italic;
}

/* Sidebar section titles */
.folio-sidebar-section-title {
    color: var(--folio-navy);
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    margin: 0 0 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--folio-subtle);
}

.st-key-project_detail_sidebar,
.st-key-project_detail_visual {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 16px !important;
    box-sizing: border-box !important;
    box-shadow: none !important;
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 22px !important;
    width: 100% !important;
}

.st-key-project_detail_visual {
    margin-bottom: 18px !important;
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

.st-key-project_detail_sidebar [data-testid="stVerticalBlock"],
.st-key-project_detail_visual [data-testid="stVerticalBlock"] {
    box-sizing: border-box;
    gap: 12px;
    max-width: 100%;
    min-width: 0;
    width: 100%;
}

.st-key-project_detail_sidebar [data-testid="stElementContainer"],
.st-key-project_detail_sidebar [data-testid="stCustomComponentV1"],
.st-key-project_detail_sidebar .stLinkButton,
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

.folio-sidebar-heading {
    margin-bottom: 2px;
    padding-bottom: 12px;
}

.folio-sidebar-heading h2 {
    color: var(--folio-navy);
    font-size: 1.05rem;
    font-weight: 800;
    margin: 0;
}

.folio-sidebar-heading h3 {
    color: var(--folio-navy);
    font-size: 1.02rem;
    font-weight: 800;
    margin: 0;
}

.folio-sidebar-heading.folio-sidebar-resources {
    border-top: 1px solid var(--folio-border);
    margin-top: 10px;
    padding-top: 18px;
}

.st-key-project_detail_sidebar iframe,
.st-key-project_detail_visual iframe {
    box-sizing: border-box;
    border-radius: 12px;
    display: block;
    max-width: 100%;
    overflow: hidden;
    width: 100%;
}

.st-key-project_detail_sidebar [data-testid="stCaptionContainer"],
.st-key-project_detail_visual [data-testid="stCaptionContainer"] {
    color: var(--folio-muted);
    font-size: 12px;
    line-height: 1.45;
}

.st-key-project_detail_sidebar .stLinkButton > a,
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

.st-key-project_detail_sidebar .stLinkButton > a:hover,
.st-key-project_detail_visual .stLinkButton > a:hover {
    background: rgba(20, 89, 200, 0.05) !important;
    border-color: rgba(20, 89, 200, 0.35) !important;
    color: var(--folio-blue) !important;
}

.st-key-project_detail_sidebar .st-key-detail_visual_back_button {
    border-top: 1px solid var(--folio-border);
    margin-top: 8px;
    padding-top: 14px;
    width: 100%;
}

.st-key-project_detail_sidebar .st-key-detail_visual_back_button button,
.st-key-detail_content_back_button button {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    color: var(--folio-muted) !important;
    font-size: 0.84rem !important;
    font-weight: 700 !important;
}

.st-key-project_detail_sidebar .st-key-detail_visual_back_button button:hover,
.st-key-detail_content_back_button button:hover {
    color: var(--folio-blue) !important;
    transform: none !important;
}

/* Metric styling for detail view */
.stMetric {
    background: transparent;
    border: none;
    padding: 0;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
    .folio-detail-content-card { padding: 2px 22px; }

    .folio-detail-section-content {
        font-size: 0.94rem;
    }
}

@media (max-width: 768px) {
    .folio-detail-content-card { padding: 0 16px; }
    .folio-detail-section { padding: 16px 0 17px; }
    .folio-detail-content-heading { padding: 17px 0 13px; }

    .folio-detail-section-content {
        font-size: 0.93rem;
    }

    .folio-detail-meta-row {
        flex-wrap: wrap;
    }

    .folio-detail-summary { align-items: flex-start; flex-direction: column; gap: 8px; }

    .folio-detail-meta-item {
        padding: 4px 8px;
    }

    .folio-detail-meta-item::after {
        margin-left: 8px;
        right: -4px;
    }
}
"""
