"""Global button and text-input styling shared across every page."""

CSS = """
/* ── Global Buttons ── */
.stButton > button {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 10px;
    color: var(--folio-navy);
    font-weight: 600;
    min-height: 40px;
    padding: 0 18px;
    transition: background 0.13s, border-color 0.13s, transform 0.13s;
}

.stButton > button:hover {
    background: var(--folio-subtle);
    border-color: #b8d0f0;
    color: var(--folio-blue);
    transform: translateY(-1px);
}

.stButton > button[kind="primary"] {
    background: var(--folio-blue);
    border-color: var(--folio-blue);
    color: #ffffff;
}

.stButton > button[kind="primary"]:hover {
    background: #0f4aab;
    border-color: #0f4aab;
    color: #ffffff;
}

/* ── Form Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 10px !important;
    color: var(--folio-navy) !important;
    padding: 12px 16px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--folio-blue) !important;
    box-shadow: 0 0 0 3px rgba(20, 89, 200, 0.1) !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--folio-muted) !important;
}

.stTextInput > div > label,
.stTextArea > div > label,
.stSelectbox > div > label {
    color: var(--folio-navy);
    font-weight: 700;
}

.stTextInput > div > div > label,
.stTextArea > div > div > label,
.stSelectbox > div > div > label {
    display: none;
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .stButton > button {
        min-height: 44px;
    }
}
"""
