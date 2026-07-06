"""Project detail page: meta row, content sections, and the dashboard/attachment sidebar."""

CSS = """
/* ── Project Detail Page Styles ── */

.folio-detail-meta-row {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    width: 100%;
}

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

/* Detail section cards */
.folio-detail-section {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 14px;
    margin-bottom: 20px;
    padding: 24px 26px;
    overflow: hidden;
}

.folio-detail-section-title {
    color: var(--folio-navy);
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    margin: 0 0 14px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--folio-subtle);
}

.folio-detail-section-content {
    color: var(--folio-navy);
    font-size: 0.96rem;
    line-height: 1.7;
    word-break: keep-all;
}

.folio-detail-section-content p {
    margin: 0 0 12px;
}

.folio-detail-section-content p:last-child {
    margin-bottom: 0;
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

.st-key-project_detail_sidebar {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 16px !important;
    box-sizing: border-box !important;
    box-shadow: 0 10px 28px rgba(11, 31, 63, 0.06) !important;
    max-width: 100% !important;
    overflow: hidden !important;
    padding: 18px !important;
    width: 100% !important;
}

.st-key-project_detail_sidebar [data-testid="stVerticalBlock"] {
    box-sizing: border-box;
    gap: 12px;
    max-width: 100%;
    min-width: 0;
    width: 100%;
}

.st-key-project_detail_sidebar [data-testid="stElementContainer"],
.st-key-project_detail_sidebar [data-testid="stCustomComponentV1"],
.st-key-project_detail_sidebar .stLinkButton {
    box-sizing: border-box !important;
    max-width: 100% !important;
    min-width: 0 !important;
    width: 100% !important;
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

.folio-sidebar-heading.folio-sidebar-resources {
    border-top: 1px solid var(--folio-border);
    margin-top: 10px;
    padding-top: 18px;
}

.st-key-project_detail_sidebar iframe {
    box-sizing: border-box;
    border-radius: 12px;
    display: block;
    max-width: 100%;
    overflow: hidden;
    width: 100%;
}

.st-key-project_detail_sidebar [data-testid="stCaptionContainer"] {
    color: var(--folio-muted);
    font-size: 0.78rem;
    line-height: 1.45;
}

.st-key-project_detail_sidebar .stLinkButton > a {
    background: #ffffff !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    color: var(--folio-navy) !important;
    font-size: 0.86rem !important;
    font-weight: 700 !important;
    min-height: 40px !important;
    transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease !important;
    width: 100% !important;
}

.st-key-project_detail_sidebar .stLinkButton > a:hover {
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
    .folio-detail-section {
        padding: 20px 22px;
    }

    .folio-detail-section-title {
        font-size: 1.05rem;
    }

    .folio-detail-section-content {
        font-size: 0.94rem;
    }
}

@media (max-width: 768px) {
    .folio-detail-section {
        margin-bottom: 16px;
        padding: 18px 16px;
    }

    .folio-detail-section-title {
        font-size: 1rem;
        margin-bottom: 12px;
    }

    .folio-detail-section-content {
        font-size: 0.93rem;
    }

    .folio-detail-meta-row {
        flex-wrap: wrap;
    }

    .folio-detail-meta-item {
        padding: 4px 8px;
    }

    .folio-detail-meta-item::after {
        margin-left: 8px;
        right: -4px;
    }
}
"""
