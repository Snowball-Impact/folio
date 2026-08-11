"""Submit/edit project form: section cards, field resets, and the visibility toggle."""

CSS = """
/* ── Forms ── */
div[data-testid="stForm"] {
    background: transparent;
    border: 0;
    padding: 0;
}

div[data-testid="stForm"] .stButton button,
div[data-testid="stForm"] button {
    margin-top: 6px;
}

/* ── Submit / Edit panels ── */
.folio-project-form-intro {
    align-items: center;
    display: flex;
    gap: 14px;
    justify-content: space-between;
    margin: 4px 0 18px;
}

.folio-project-form-intro strong {
    color: var(--folio-navy);
    font-size: 1.05rem;
}

.folio-project-form-intro span {
    color: var(--folio-muted);
    flex: 1 1 auto;
    font-size: 0.82rem;
    text-align: right;
}

.folio-project-form-intro small {
    background: var(--folio-subtle);
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-muted);
    flex: 0 0 auto;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 5px 10px;
    white-space: nowrap;
}

.folio-project-form-intro b {
    color: var(--folio-blue);
}

[class*="form_section_"] {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 14px !important;
    box-sizing: border-box !important;
    box-shadow: none !important;
    margin-bottom: 18px !important;
    max-width: 100% !important;
    min-width: 0 !important;
    padding: 24px 26px !important;
    width: 100% !important;
}

[class*="form_section_"] [data-testid="stVerticalBlock"],
[class*="form_section_"] [data-testid="stHorizontalBlock"],
[class*="form_section_"] [data-testid="stColumn"],
[class*="form_section_"] [data-testid="stElementContainer"] {
    box-sizing: border-box !important;
    max-width: 100% !important;
    min-width: 0 !important;
}

[class*="form_section_"] .stTextInput,
[class*="form_section_"] .stTextArea,
[class*="form_section_"] .stRadio,
[class*="form_section_"] .stSelectbox,
[class*="form_section_"] .stMultiSelect,
[class*="form_section_"] [data-testid="stFileUploader"],
[class*="form_section_"] [data-testid="stCustomComponentV1"],
[class*="form_section_"] iframe {
    box-sizing: border-box !important;
    max-width: 100% !important;
    min-width: 0 !important;
    width: 100% !important;
}

/* Quill editor's iframe reports its real height only after its JS
   mounts, popping from a small placeholder to its full toolbar+editor
   size a moment later. Reserving space up front avoids that jump. */
[class*="form_section_"] [data-testid="stCustomComponentV1"] {
    min-height: 300px !important;
}

[class*="_form_section_content"] [data-testid="stVerticalBlock"] {
    gap: 0.75rem !important;
}

[class*="form_section_"] .stTextInput > div,
[class*="form_section_"] .stTextInput div[data-baseweb="input"],
[class*="form_section_"] .stTextArea > div,
[class*="form_section_"] .stTextArea div[data-baseweb="textarea"] {
    box-sizing: border-box !important;
    max-width: 100% !important;
    min-width: 0 !important;
    width: 100% !important;
}

[class*="form_section_"] input,
[class*="form_section_"] textarea {
    box-sizing: border-box !important;
    max-width: 100% !important;
    min-width: 0 !important;
    width: 100% !important;
}

[class*="form_section_"] [data-testid="stWidgetLabel"] {
    display: flex !important;
}

[class*="form_section_"] [data-testid="stWidgetLabel"] p {
    color: var(--folio-navy) !important;
    font-size: 0.86rem !important;
    font-weight: 700 !important;
}

.folio-form-section-heading {
    display: block;
    margin-bottom: 16px;
}

.folio-form-section-heading > div {
    align-items: center;
    display: flex;
    gap: 18px;
    justify-content: space-between;
    min-width: 0;
}

.folio-form-preview-heading strong {
    color: var(--folio-navy);
    display: block;
    font-size: 0.9rem;
    font-weight: 800;
    margin: 0 0 14px;
}

.folio-form-preview-heading {
    margin-bottom: 14px;
}

[class*="_form_section_overview"] [data-testid="stHorizontalBlock"] {
    align-items: stretch;
}

[class*="_form_section_overview"] [data-testid="stColumn"]:nth-child(2) {
    border-left: 1px solid var(--folio-border);
    padding-left: 28px;
}

[class*="_form_section_overview"] .folio-home-card {
    margin: 0 auto;
    width: 100%;
}

[class*="_thumbnail_settings"] {
    margin-top: 18px !important;
}

[class*="_form_section_links"] [data-testid="stHorizontalBlock"] {
    align-items: flex-start;
}

.folio-form-section-heading strong {
    color: var(--folio-navy);
    flex: 0 0 auto;
    font-size: 1rem;
}

.folio-form-section-heading small {
    color: var(--folio-muted);
    flex: 1 1 auto;
    font-size: 0.82rem;
    margin-top: 0;
    text-align: right;
    word-break: keep-all;
}

[class*="form_section_"] .stTextInput input,
[class*="form_section_"] .stTextArea textarea,
[class*="form_section_"] [data-baseweb="select"] > div {
    background: var(--folio-bg) !important;
}

[class*="_form_section_overview"] [data-testid="stVerticalBlock"] {
    gap: 0.78rem !important;
}

[class*="_form_section_overview"] .stTextInput {
    margin-bottom: 2px !important;
}

[class*="_form_section_overview"] .stRadio > div {
    align-items: center;
    column-gap: 18px;
    flex-wrap: wrap;
    row-gap: 4px;
}

[class*="_form_section_overview"] .stRadio label {
    color: var(--folio-navy);
    font-size: 0.84rem;
    font-weight: 700;
    min-height: 24px;
}

[class*="_form_section_overview"] .stRadio p {
    font-size: inherit !important;
    font-weight: inherit !important;
    line-height: 1 !important;
    white-space: nowrap;
}

[class*="_form_section_overview"] .stTextInput div[data-baseweb="input"] {
    min-height: 42px !important;
}

[class*="_form_section_overview"] .stTextInput input {
    font-size: 0.88rem !important;
    min-height: 42px !important;
}

/* Visibility toggle card (rendered when show_visibility_setting=True) */
[class*="_visibility_setting"] {
    background: linear-gradient(135deg, #f8faff, #eef4ff) !important;
    border: 1px solid rgba(20, 89, 200, 0.2) !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    padding: 16px 18px !important;
}

[class*="_visibility_setting"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
}

.folio-visibility-setting-copy {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.folio-visibility-setting-copy strong {
    color: var(--folio-navy);
    font-size: 0.95rem;
    font-weight: 800;
}

.folio-visibility-setting-copy span {
    color: var(--folio-muted);
    font-size: 0.78rem;
    line-height: 1.45;
}

[class*="_visibility_setting"] .stToggle {
    display: flex !important;
    justify-content: flex-end !important;
}

[class*="_visibility_setting"] .stToggle [data-testid="stWidgetLabel"] {
    justify-content: flex-end !important;
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .folio-project-form-intro {
        align-items: flex-start;
        flex-direction: column;
        gap: 5px;
    }

    .folio-project-form-intro span {
        text-align: left;
    }

    .folio-form-section-heading > div {
        align-items: flex-start;
        flex-direction: column;
        gap: 3px;
    }

    .folio-form-section-heading small {
        text-align: left;
    }

    [class*="form_section_"] {
        padding: 20px 18px !important;
    }

    [class*="_form_section_overview"] [data-testid="stColumn"]:nth-child(2) {
        border-left: 0;
        border-top: 1px solid var(--folio-border);
        margin-top: 8px;
        padding-left: 0;
        padding-top: 20px;
    }

    [class*="_form_section_overview"] [data-testid="stHorizontalBlock"],
    [class*="_form_section_links"] [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }

    [class*="_form_section_overview"] [data-testid="stColumn"],
    [class*="_form_section_links"] [data-testid="stColumn"] {
        width: 100% !important;
    }
}
"""
