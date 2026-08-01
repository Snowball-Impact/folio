"""User profile page (avatar header, bio, project/view-count metrics)."""

CSS = """
/* ── Profile dashboard ── */
.folio-profile-identity { display: block; text-align: center; }

.folio-profile-identity-copy { min-width: 0; }

.folio-profile-edit-heading > span {
    color: var(--folio-blue);
    display: block;
    font-size: 0.86rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    margin-bottom: 5px;
}

.folio-profile-fields {
    display: grid;
    gap: 18px;
    grid-template-columns: 1fr 1fr 1.25fr;
    margin: 0;
    text-align: center;
}

.folio-profile-fields > div { min-width: 0; }

.folio-profile-fields dt {
    color: var(--folio-muted);
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 5px;
}

.folio-profile-fields dd {
    color: var(--folio-navy);
    font-size: 20px;
    font-weight: 700;
    line-height: 1.4;
    margin: 0;
}

.folio-profile-info-org {
    color: var(--folio-navy);
}

.folio-profile-info-org.is-empty { color: var(--folio-muted); font-weight: 500; }

.folio-profile-email {
    overflow-wrap: anywhere;
}

.folio-profile-about {
    border-top: 1px solid var(--folio-border);
    margin-top: 18px;
    padding-top: 16px;
    text-align: center;
}

.folio-profile-bio {
    color: var(--folio-navy);
    font-size: 14px;
    line-height: 1.6;
    margin: 0;
    word-break: keep-all;
}

.folio-profile-bio.is-empty { color: var(--folio-muted); }

.folio-profile-stats {
    align-items: center;
    border-top: 1px solid var(--folio-border);
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 16px;
    padding-top: 16px;
}

.folio-profile-stats span {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-muted);
    display: inline-flex;
    font-size: 12px;
    gap: 7px;
    min-height: 32px;
    padding: 0 12px;
}

.folio-profile-stats small {
    font-size: 12px;
    font-weight: 700;
}

.folio-profile-stats strong {
    color: var(--folio-navy);
    font-size: 13px;
    font-weight: 800;
}

.st-key-profile_overview {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 14px !important;
    margin-bottom: 0 !important;
    padding: 22px 26px !important;
}

.st-key-profile_overview [data-testid="stElementContainer"]:has(.st-key-start_edit_profile),
.st-key-start_edit_profile {
    align-items: flex-end;
    display: flex !important;
    justify-content: flex-end !important;
    margin-left: auto !important;
    margin-top: 12px;
    width: 100% !important;
}
.st-key-start_edit_profile .stButton {
    display: flex !important;
    justify-content: flex-end !important;
    width: 100% !important;
}
.st-key-start_edit_profile button { width: auto; }

.folio-profile-section-heading {
    align-items: center;
    display: flex;
    gap: 18px;
    justify-content: space-between;
    margin: 18px 2px 12px;
}

.folio-profile-section-heading h2,
.folio-profile-edit-heading h2 { color: var(--folio-navy); font-size: 20px; font-weight: 800; margin: 0; }
.folio-profile-section-heading p,
.folio-profile-edit-heading p { color: var(--folio-muted); font-size: 13px; margin: 0; text-align: right; }

.st-key-profile_empty_projects {
    background: var(--folio-surface);
    border: 1px dashed #b8c9e6;
    border-radius: 14px;
    padding: 30px 24px;
    text-align: center;
}
.st-key-profile_empty_projects h3 { color: var(--folio-navy); font-size: 18px; margin: 0 0 7px; }
.st-key-profile_empty_projects p { color: var(--folio-muted); font-size: 13px; margin: 0 0 18px; }

.st-key-profile_edit_card {
    background: var(--folio-surface) !important;
    border-color: var(--folio-border) !important;
    border-radius: 14px !important;
    padding: 28px 30px !important;
}
.folio-profile-edit-heading { border-bottom: 1px solid var(--folio-border); margin-bottom: 22px; padding-bottom: 20px; }
.folio-profile-edit-heading p { margin-top: 7px; }

@media (max-width: 860px) {
    .st-key-profile_overview,
    .st-key-profile_edit_card { padding: 22px 20px !important; }
    .folio-profile-fields { gap: 18px; grid-template-columns: 1fr 1fr; }
    .folio-profile-fields > div:last-child { grid-column: 1 / -1; }
    .folio-profile-section-heading { align-items: flex-start; flex-direction: column; gap: 8px; }
    .folio-profile-section-heading p { text-align: left; }
}
"""
