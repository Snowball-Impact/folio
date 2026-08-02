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

.folio-comments-shell {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;
}

.folio-comments-heading {
    align-items: center;
    background: #ffffff;
    border: 1px solid rgba(20, 89, 200, 0.12);
    border-radius: 8px;
    display: flex;
    gap: 18px;
    justify-content: space-between;
    padding: 16px 18px 15px;
}

.folio-comments-heading h2 {
    color: var(--folio-navy);
    flex: 0 0 auto;
    font-size: 20px;
    font-weight: 800;
    line-height: 1.2;
    margin: 0;
    white-space: nowrap;
}

.folio-comments-heading p {
    color: var(--folio-muted);
    font-size: 13px;
    font-weight: 600;
    line-height: 1.45;
    margin: 0;
    min-width: 0;
    text-align: right;
}

.folio-comments-divider {
    border-top: 1px solid var(--folio-border);
    margin: 12px 0 14px;
}

.folio-comments-login-note {
    background: #e7f1ff;
    border: 1px solid #d5e6ff;
    border-radius: 8px;
    color: var(--folio-blue);
    font-size: 13px;
    font-weight: 700;
    line-height: 1.5;
    margin: 0 0 10px;
    padding: 13px 16px;
}

.folio-comments-empty {
    align-items: center;
    background: #ffffff;
    border: 1px dashed rgba(20, 89, 200, 0.22);
    border-radius: 8px;
    color: var(--folio-muted);
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 4px 0 0;
    min-height: 74px;
    padding: 18px;
    text-align: center;
}

.folio-comments-empty strong {
    color: var(--folio-navy);
    font-size: 14px;
    font-weight: 800;
}

.folio-comments-empty span {
    font-size: 13px;
    line-height: 1.5;
}

.folio-comment-card {
    background: #ffffff;
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    box-sizing: border-box;
    box-shadow: 0 1px 0 rgba(11, 31, 63, 0.02);
    margin-bottom: 0;
    min-height: 38px;
    padding: 8px 272px 8px 10px;
    position: relative;
    width: 100%;
}

.folio-comment-has-actions {
    margin-bottom: 0;
}

.folio-comment-reply {
    background: #eef6ff;
    border-color: #cfe0fb;
    border-left: 3px solid rgba(20, 89, 200, 0.36);
}

.folio-comment-line {
    align-items: center;
    display: flex;
    gap: 18px;
    width: 100%;
}

.folio-comment-author-line {
    align-items: center;
    display: inline-flex;
    flex: 0 0 128px;
    flex-wrap: wrap;
    gap: 6px;
    min-width: 0;
}

.folio-comment-author-line strong {
    color: var(--folio-navy);
    font-size: 0.92rem;
    line-height: 1.5;
}

.folio-comment-author-badge {
    align-items: center;
    background: #e7f6f2;
    border: 1px solid #d2eee8;
    border-radius: 999px;
    color: #087568;
    display: inline-flex;
    font-size: 11px;
    font-weight: 800;
    height: 22px;
    line-height: 1;
    padding: 0 8px;
}

.folio-comment-index {
    color: var(--folio-blue);
    flex: 0 0 64px;
    font-size: 0.82rem;
    font-weight: 800;
    line-height: 1.7;
    white-space: nowrap;
}

.folio-comment-date {
    color: var(--folio-muted);
    font-size: 0.8rem;
    line-height: 1.7;
    position: absolute;
    right: 12px;
    text-align: right;
    top: 8px;
    white-space: nowrap;
    width: 126px;
}

.folio-comment-body {
    color: var(--folio-navy);
    flex: 1 1 auto;
    font-size: 0.95rem;
    line-height: 1.55;
    min-width: 0;
    white-space: pre-wrap;
    word-break: keep-all;
}

.st-key-project_comments_section {
    background: #f7faff;
    border: 1px solid rgba(20, 89, 200, 0.14);
    border-radius: 10px;
    box-shadow: 0 14px 30px rgba(11, 31, 63, 0.06);
    margin-top: 18px;
    overflow: visible;
    padding: 14px 16px 18px;
}

.st-key-project_comments_section [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent;
    border: 0;
}

.st-key-project_comments_section [class*="st-key-comment_row_"] {
    box-sizing: border-box;
    margin-bottom: 4px;
    max-width: 100%;
    min-width: 0;
    position: relative;
    width: 100%;
}

.st-key-project_comments_section [class*="st-key-comment_row_root_"]:first-of-type {
    margin-top: 4px;
}

.st-key-project_comments_section [class*="st-key-comment_row_reply_"] {
    margin-top: 4px;
    margin-bottom: 4px;
}

.st-key-project_comments_section [class*="st-key-comment_row_"] .folio-comment-card {
    margin-bottom: 0;
}

.st-key-project_comments_section [class*="st-key-comment_row_"] .folio-comment-has-actions {
    margin-bottom: 0;
}

.st-key-project_comments_section [class*="st-key-comment_actions_"][data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 8px !important;
    justify-content: flex-end;
    margin: -36px 148px 2px auto;
    min-height: 30px;
    padding: 0;
    position: relative;
    width: max-content;
    z-index: 1;
}

.st-key-project_comments_section [class*="st-key-comment_actions_reply_"][data-testid="stHorizontalBlock"] {
    margin-left: auto;
    width: max-content;
}

.st-key-project_comments_section [class*="st-key-reply_form_"] {
    background: #f7faff;
    border: 1px solid rgba(20, 89, 200, 0.16);
    border-left: 3px solid rgba(20, 89, 200, 0.38);
    border-radius: 8px;
    margin: 2px 0 4px 36px;
    padding: 10px 12px 12px;
    width: calc(100% - 36px);
}

.st-key-project_comments_section .folio-reply-composer-head {
    align-items: center;
    color: var(--folio-muted);
    display: flex;
    flex-wrap: wrap;
    font-size: 12px;
    gap: 6px;
    line-height: 1.4;
    margin: 0 0 8px;
}

.st-key-project_comments_section .folio-reply-composer-head span {
    color: var(--folio-blue);
    font-weight: 800;
}

.st-key-project_comments_section .folio-reply-composer-head strong {
    color: var(--folio-navy);
    font-size: 12px;
    font-weight: 800;
}

.st-key-project_comments_section .folio-reply-composer-head em {
    font-style: normal;
}

.st-key-project_comments_section [class*="st-key-reply_form_"] [data-testid="stHorizontalBlock"] {
    gap: 12px !important;
}

.st-key-project_comments_section [class*="st-key-reply_form_"] textarea {
    background: #ffffff;
    min-height: 76px !important;
}

.st-key-project_comments_section [class*="st-key-reply_form_"] .stButton {
    margin: 0 0 6px !important;
}

.st-key-project_comments_section [class*="st-key-reply_form_"] button {
    height: 34px;
    min-height: 34px !important;
}

.st-key-project_comments_section [class*="st-key-comment_actions_"] [data-testid="stElementContainer"],
.st-key-project_comments_section [class*="st-key-comment_actions_"] .stButton {
    margin: 0 !important;
    width: auto !important;
}

.st-key-project_comments_section [class*="st-key-comment_actions_"] button {
    height: 26px;
    min-height: 26px !important;
    min-width: 72px;
    padding: 0 10px !important;
    width: auto !important;
}

.st-key-project_comments_section .st-key-comments_pagination[data-testid="stHorizontalBlock"] {
    align-items: center;
    border-top: 1px solid rgba(20, 89, 200, 0.12);
    gap: 8px !important;
    justify-content: center;
    margin: 10px 0 0;
    padding-top: 10px;
    width: 100%;
}

.st-key-project_comments_section .st-key-comments_pagination [data-testid="stElementContainer"],
.st-key-project_comments_section .st-key-comments_pagination .stButton {
    margin: 0 !important;
    width: auto !important;
}

.st-key-project_comments_section .st-key-comments_pagination button {
    height: 30px;
    min-height: 30px !important;
    min-width: 64px;
    padding: 0 12px !important;
    width: auto !important;
}

.folio-comments-page-status {
    align-items: center;
    color: var(--folio-muted);
    display: inline-flex;
    font-size: 12px;
    font-weight: 800;
    height: 30px;
    padding: 0 4px;
    white-space: nowrap;
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

    .folio-comments-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 6px;
    }

    .folio-comments-heading h2 {
        font-size: 20px;
    }

    .folio-comment-line {
        align-items: flex-start;
        flex-direction: column;
        gap: 4px;
    }

    .folio-comment-card {
        padding-right: 10px;
    }

    .folio-comment-author-line {
        flex-basis: auto;
    }

    .folio-comment-index,
    .folio-comment-date {
        flex-basis: auto;
    }

    .folio-comment-date {
        position: static;
        text-align: left;
        width: auto;
    }

    .folio-comment-reply {
        margin-left: 0;
    }

    .st-key-project_comments_section [class*="st-key-comment_actions_"][data-testid="stHorizontalBlock"] {
        align-items: center;
        flex-direction: row;
        margin: 2px 0 4px auto;
        width: max-content;
    }

    .st-key-project_comments_section [class*="st-key-comment_actions_reply_"][data-testid="stHorizontalBlock"] {
        margin-left: auto;
        width: max-content;
    }

    .st-key-project_comments_section [class*="st-key-reply_form_"] {
        margin-left: 18px;
        width: calc(100% - 18px);
    }

    .st-key-project_comments_section [class*="st-key-comment_actions_"] [data-testid="stElementContainer"],
    .st-key-project_comments_section [class*="st-key-comment_actions_"] .stButton {
        width: auto !important;
    }
}
"""
