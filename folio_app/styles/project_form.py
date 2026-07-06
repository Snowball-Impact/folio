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
    justify-content: space-between;
    margin: 4px 0 18px;
}

.folio-project-form-intro strong {
    color: var(--folio-navy);
    font-size: 1.05rem;
}

.folio-project-form-intro span {
    color: var(--folio-muted);
    font-size: 0.82rem;
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
    min-height: 360px !important;
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
    align-items: center;
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
}

.folio-form-section-heading > span {
    align-items: center;
    background: var(--folio-subtle);
    border-radius: 50%;
    color: var(--folio-blue);
    display: inline-flex;
    flex: 0 0 32px;
    font-size: 0.86rem;
    font-weight: 800;
    height: 32px;
    justify-content: center;
}

.folio-form-section-heading strong,
.folio-form-section-heading small {
    display: block;
}

.folio-form-section-heading strong {
    color: var(--folio-navy);
    font-size: 1rem;
}

.folio-form-section-heading small {
    color: var(--folio-muted);
    font-size: 0.82rem;
    margin-top: 2px;
}

[class*="form_section_"] .stTextInput input,
[class*="form_section_"] .stTextArea textarea,
[class*="form_section_"] [data-baseweb="select"] > div {
    background: var(--folio-bg) !important;
}

/* Visibility toggle card (rendered when show_visibility_setting=True) */
[class*="_visibility_setting"] {
    background: linear-gradient(135deg, #f8faff, #eef4ff) !important;
    border: 1px solid rgba(20, 89, 200, 0.2) !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    padding: 16px 18px !important;
}

[class*="_visibility_setting"] [data-testid="stVerticalBlock"] {
    gap: 8px !important;
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

/* ── Responsive ── */
@media (max-width: 860px) {
    .folio-project-form-intro {
        align-items: flex-start;
        flex-direction: column;
        gap: 5px;
    }

    [class*="form_section_"] {
        padding: 20px 18px !important;
    }
}
"""
