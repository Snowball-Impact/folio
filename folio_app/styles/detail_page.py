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

.st-key-detail_back_action_row[data-testid="stHorizontalBlock"] {
    justify-content: flex-end;
    margin: 18px 0 4px;
    width: 100%;
}

.st-key-detail_back_action_row .stButton,
.st-key-detail_back_action_row [data-testid="stElementContainer"] {
    display: flex;
    justify-content: flex-end;
    margin: 0 !important;
}

.st-key-detail_content_back_button button {
    background: #ffffff !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 999px !important;
    box-shadow: 0 8px 18px rgba(11, 31, 63, 0.06) !important;
    color: var(--folio-muted) !important;
    font-size: 0.84rem !important;
    font-weight: 800 !important;
    min-height: 34px !important;
    padding: 0 16px !important;
    width: auto !important;
}

.st-key-detail_content_back_button button:hover {
    background: #f7faff !important;
    border-color: rgba(20, 89, 200, 0.32) !important;
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
        width: 100%;
    }

    .folio-detail-meta-item::after {
        display: none;
    }

}
"""
