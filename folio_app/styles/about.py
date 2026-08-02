"""Service introduction page styles."""

CSS = """
.folio-about-page {
    margin-top: -8px;
}

.folio-about-line {
    display: block;
}

.folio-about-hero,
.folio-about-section {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 16px;
}

.folio-about-hero {
    overflow: hidden;
}

.folio-about-hero-banner {
    background: #ffffff;
    display: block;
    width: 100%;
}

.folio-about-hero-banner img {
    display: block;
    height: auto;
    object-fit: cover;
    object-position: center;
    width: 100%;
}

.folio-about-hero-caption {
    align-items: center;
    border-top: 1px solid var(--folio-border);
    display: flex;
    gap: 18px;
    justify-content: space-between;
    padding: 18px 28px;
}

.folio-about-hero-caption strong {
    color: var(--folio-navy);
    flex: 0 0 auto;
    font-size: 20px;
    font-weight: 800;
    line-height: 1.35;
    word-break: keep-all;
}

.folio-about-hero-caption p {
    color: var(--folio-muted);
    font-size: 14px;
    line-height: 1.7;
    margin: 0;
    text-align: right;
    word-break: keep-all;
}

.folio-about-section {
    margin-top: 28px;
    padding: 34px 42px;
}

.folio-about-eyebrow {
    color: var(--folio-blue);
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.22em;
    line-height: 1;
    margin-bottom: 24px;
    text-transform: uppercase;
}

.folio-about-team {
    align-items: center;
    display: grid;
    gap: 34px;
    grid-template-columns: minmax(360px, 0.58fr) minmax(0, 1fr);
    text-align: left;
}

.folio-about-team-image {
    background: var(--folio-subtle);
    border-radius: 16px;
    padding: 6px;
}

.folio-about-team-image img {
    aspect-ratio: 16 / 9;
    border-radius: 12px;
    display: block;
    object-fit: cover;
    object-position: center;
    width: 100%;
}

.folio-about-team-copy h1 {
    color: var(--folio-navy);
    font-size: 28px;
    font-weight: 800;
    line-height: 1.35;
    margin: 0;
    word-break: keep-all;
}

.folio-about-team-copy p {
    color: var(--folio-muted);
    font-size: 14px;
    line-height: 1.8;
    margin: 16px 0 0;
    max-width: 560px;
    word-break: keep-all;
}

.folio-about-team-status {
    align-items: flex-end;
    border-top: 1px solid var(--folio-border);
    color: var(--folio-muted);
    display: flex;
    font-size: 13px;
    gap: 16px;
    justify-content: space-between;
    line-height: 1.65;
    margin-top: 24px;
    padding-top: 18px;
    text-align: left;
    word-break: keep-all;
}

.folio-about-contact {
    align-items: center;
    background: #ffffff;
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-blue) !important;
    display: inline-flex;
    flex: 0 0 auto;
    font-size: 13px;
    font-weight: 800;
    height: 38px;
    padding: 0 16px;
    text-decoration: none !important;
}

.folio-about-contact:hover {
    border-color: rgba(20, 89, 200, 0.35);
    box-shadow: 0 6px 14px rgba(11, 31, 63, 0.08);
}

.folio-about-section-heading {
    align-items: center;
    border-bottom: 1px solid var(--folio-border);
    display: flex;
    flex-direction: column;
    gap: 24px;
    justify-content: space-between;
    margin-bottom: 22px;
    padding-bottom: 18px;
    text-align: center;
}

.folio-about-section-heading h2,
.folio-about-vision-heading h2 {
    color: var(--folio-navy);
    font-size: 24px;
    font-weight: 800;
    line-height: 1.35;
    margin: 0;
    word-break: keep-all;
}

.folio-about-section-heading p {
    color: var(--folio-muted);
    font-size: 13px;
    line-height: 1.6;
    margin: 0;
    text-align: center;
    word-break: keep-all;
}

.folio-about-service-flow {
    display: grid;
    gap: 0;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-top: 22px;
}

.folio-about-service-step {
    border-right: 1px solid var(--folio-border);
    padding: 0 24px;
    text-align: center;
}

.folio-about-service-step:first-child {
    padding-left: 0;
}

.folio-about-service-step:last-child {
    border-right: 0;
    padding-right: 0;
}

.folio-about-service-step small {
    color: var(--folio-blue);
    display: block;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.16em;
    margin-bottom: 13px;
}

.folio-about-service-step h3 {
    color: var(--folio-navy);
    font-size: 20px;
    line-height: 1.35;
    margin: 0 0 12px;
    word-break: keep-all;
}

.folio-about-service-step p {
    color: var(--folio-muted);
    font-size: 14px;
    line-height: 1.75;
    margin: 0;
    word-break: keep-all;
}

.folio-about-capabilities {
    display: grid;
    gap: 10px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    margin-top: 20px;
    text-align: center;
}

.folio-about-capability {
    background: #fbfdff;
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    min-height: 88px;
    padding: 17px 18px;
}

.folio-about-capability strong {
    color: var(--folio-navy);
    display: block;
    font-size: 15px;
    margin-bottom: 8px;
}

.folio-about-capability span {
    color: var(--folio-muted);
    display: block;
    font-size: 13px;
    line-height: 1.55;
    word-break: keep-all;
}

@media (max-width: 860px) {
    .folio-about-hero-caption {
        align-items: flex-start;
        flex-direction: column;
        padding: 18px 20px;
    }

    .folio-about-hero-caption strong {
        font-size: 18px;
    }

    .folio-about-hero-caption p {
        text-align: left;
    }

    .folio-about-section {
        padding: 26px 22px;
    }

    .folio-about-eyebrow {
        font-size: 13px;
        margin-bottom: 20px;
    }

    .folio-about-team {
        display: block;
    }

    .folio-about-team-image {
        margin-bottom: 22px;
    }

    .folio-about-team-copy h1 {
        font-size: 22px;
    }

    .folio-about-team-status {
        align-items: flex-start;
        flex-direction: column;
    }

    .folio-about-service-flow,
    .folio-about-capabilities {
        grid-template-columns: 1fr;
    }

    .folio-about-service-step {
        border-bottom: 1px solid var(--folio-border);
        border-right: 0;
        padding: 20px 0;
    }

    .folio-about-service-step:first-child {
        padding-top: 0;
    }

    .folio-about-service-step:last-child {
        border-bottom: 0;
        padding-bottom: 0;
    }

}
"""
