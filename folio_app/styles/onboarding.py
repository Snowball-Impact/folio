"""Onboarding (terms-of-service consent) card."""

CSS = """
/* ── Onboarding ── */
.folio-onboarding-hero {
    grid-template-columns: 1fr;
    margin: 12px auto 18px;
    max-width: 680px;
    text-align: center;
}

.folio-onboarding-hero p {
    margin: 0 auto;
}

.folio-onboarding-badge {
    background: rgba(20, 89, 200, 0.1);
    border-radius: 999px;
    color: var(--folio-blue);
    display: inline-block;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    margin-bottom: 14px;
    padding: 6px 16px;
    text-transform: uppercase;
}

.folio-onboarding-effective {
    color: var(--folio-muted);
    font-size: 0.82rem;
    margin: 10px auto 0;
}

.st-key-folio_onboarding_card {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 14px;
    box-shadow: 0 16px 40px rgba(11, 31, 63, 0.08);
    margin: 0 auto;
    max-width: 560px;
    padding: 24px;
    width: min(560px, calc(100vw - 48px));
}
"""
