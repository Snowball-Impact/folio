"""User profile page (avatar header, bio, project/view-count metrics)."""

CSS = """
/* ── Profile ── */
.folio-profile-header {
    align-items: center;
    display: flex;
    gap: 18px;
    margin-bottom: 20px;
}

.folio-avatar {
    align-items: center;
    background: linear-gradient(135deg, var(--folio-blue), #2d6fd8);
    border-radius: 50%;
    color: #ffffff;
    display: flex;
    flex-shrink: 0;
    font-size: 1.4rem;
    font-weight: 800;
    height: 56px;
    justify-content: center;
    width: 56px;
}

.folio-profile-info-name {
    color: var(--folio-navy);
    font-size: 1.3rem;
    font-weight: 800;
    margin: 0 0 3px;
}

.folio-profile-info-org {
    color: var(--folio-muted);
    font-size: 0.9rem;
    margin: 0;
}

.folio-profile-bio {
    color: var(--folio-navy);
    font-size: 0.92rem;
    line-height: 1.6;
    margin: 12px 0 0;
    word-break: keep-all;
}

.st-key-profile_overview {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 14px !important;
    margin-bottom: 24px !important;
    padding: 24px 26px !important;
}

.st-key-profile_overview [data-testid="stMetric"] {
    background: var(--folio-bg);
    border: 1px solid var(--folio-border);
    border-radius: 12px;
    padding: 16px 18px;
}
"""
