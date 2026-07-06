"""Login/signup card (folio_auth_shell / folio_auth_form containers)."""

CSS = """
/* ── Auth Cards ── */
.st-key-folio_auth_shell {
    background: transparent;
    border: 0;
    border-radius: 0;
    box-sizing: border-box;
    box-shadow: none;
    margin: 0 auto;
    max-width: 440px;
    padding: 0;
    width: min(440px, calc(100vw - 48px));
}

.st-key-folio_auth_shell:has(.folio-auth-card-signup) {
    max-width: 520px;
    width: min(520px, calc(100vw - 48px));
}

.st-key-folio_auth_form {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 0 0 14px 14px;
    border-top: 0;
    box-sizing: border-box;
    box-shadow: 0 16px 40px rgba(11, 31, 63, 0.08);
    padding: 24px;
}

/* Auth card inputs */
.st-key-folio_auth_form .stTextInput div[data-baseweb="input"] {
    align-items: center;
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    display: flex;
    min-height: 48px;
    overflow: hidden;
    padding: 0;
}

.st-key-folio_auth_form .stTextInput div[data-baseweb="input"] input {
    background: var(--folio-surface) !important;
    border: 0 !important;
    box-shadow: none !important;
    flex: 1;
    min-height: 46px;
    padding: 12px 16px !important;
}

.st-key-folio_auth_form .stTextInput input:-webkit-autofill,
.st-key-folio_auth_form .stTextInput input:-webkit-autofill:hover,
.st-key-folio_auth_form .stTextInput input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
    -webkit-text-fill-color: var(--folio-navy) !important;
    caret-color: var(--folio-navy);
}

.st-key-folio_auth_form .stTextInput div[data-testid="InputInstructions"] {
    display: none !important;
}

.st-key-folio_auth_form .st-key-login_to_signup button {
    width: calc(100% - 48px) !important;
}

.st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"],
.st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"] > div {
    background: var(--folio-surface) !important;
    width: 100%;
}

.st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:focus-within,
.st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:has(input:not(:placeholder-shown)) {
    background: var(--folio-surface) !important;
}

.st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:focus-within *,
.st-key-folio_auth_form .stTextInput:has(input[type="password"]) div[data-baseweb="input"]:has(input:not(:placeholder-shown)) * {
    background-color: transparent !important;
}

.st-key-folio_auth_form .stTextInput:has(input[type="password"]) button {
    align-items: center;
    align-self: stretch;
    background: transparent !important;
    border: 0 !important;
    border-radius: 8px;
    box-shadow: none !important;
    color: var(--folio-muted) !important;
    display: inline-flex;
    flex: 0 0 38px;
    height: auto;
    justify-content: center;
    margin: 0 6px 0 0;
    min-height: 46px;
    padding: 0;
    position: static;
    transform: none;
    width: 38px;
}

.st-key-folio_auth_shell .stTextInput {
    margin-bottom: 4px;
}

.st-key-folio_auth_shell .stAlert {
    margin: 6px 0 12px;
}

.st-key-folio_auth_shell .stAlert [data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem;
    line-height: 1.5;
    word-break: keep-all;
}

.st-key-folio_auth_shell details {
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    margin-top: 16px;
    padding: 2px 10px;
}

.st-key-folio_auth_shell details summary {
    color: var(--folio-navy);
    font-weight: 700;
}

.st-key-folio_auth_shell hr {
    margin: 18px 0;
}

/* Auth submit buttons */
.st-key-folio_auth_shell .stButton > button,
.st-key-folio_auth_shell .stFormSubmitButton > button {
    background: var(--folio-blue);
    border: 1px solid var(--folio-blue);
    border-radius: 10px;
    box-shadow: 0 6px 18px rgba(20, 89, 200, 0.2);
    color: #ffffff;
    font-weight: 700;
    min-height: 44px;
    padding: 0 1.2rem;
}

.st-key-folio_auth_shell .stButton > button:hover,
.st-key-folio_auth_shell .stFormSubmitButton > button:hover {
    background: #0e42a8;
    border-color: #0e42a8;
    transform: none;
}

.st-key-folio_auth_shell .stButton > button:disabled,
.st-key-folio_auth_shell .stFormSubmitButton > button:disabled {
    background: #d4e0f8;
    border-color: #d4e0f8;
    box-shadow: none;
    color: #7a8fb0;
}

.folio-auth-card-header {
    background: linear-gradient(135deg, #08142b, #0b1f3f 72%, #0c2a48);
    border-radius: 14px 14px 0 0;
    box-sizing: border-box;
    margin-bottom: 0;
    max-width: calc(100vw - 48px);
    padding: 24px 24px 22px;
    width: 440px;
}

.folio-auth-card-signup {
    width: 520px;
}

.folio-auth-card-header h2 {
    color: #ffffff;
    font-size: 1.55rem;
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 8px;
    word-break: keep-all;
}

.folio-auth-card-header p {
    color: rgba(200, 215, 248, 0.9);
    font-size: 0.9rem;
    line-height: 1.55;
    margin: 0;
    word-break: keep-all;
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .st-key-folio_auth_shell {
        width: min(100%, calc(100vw - 28px));
    }

    .st-key-folio_auth_form {
        padding: 18px;
    }

    .folio-auth-card-header {
        padding: 18px;
    }

    .folio-auth-card-header h2 {
        font-size: 1.35rem;
    }

    .st-key-folio_auth_shell .stFormSubmitButton > button {
        min-height: 44px;
    }
}
"""
