"""Home hero banner and the shared sub-page hero (render_hero) used across pages."""

CSS = """
/* ── Home Hero (light) ── */
.folio-home-hero {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 16px;
    color: var(--folio-navy);
    display: grid;
    gap: 24px;
    grid-template-columns: minmax(0, 1fr) minmax(260px, 0.8fr);
    margin-top: 16px;
    min-height: 248px;
    padding: 52px 28px 44px;
}

.folio-home-eyebrow {
    color: var(--folio-blue);
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
    text-transform: uppercase;
}

.folio-home-copy h1 {
    color: var(--folio-navy);
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.13;
    margin: 0 0 16px;
    text-wrap: balance;
    word-break: keep-all;
}

.folio-home-copy h1 em {
    color: var(--folio-blue);
    font-style: normal;
}

.folio-home-copy p {
    color: var(--folio-muted);
    font-size: 0.98rem;
    line-height: 1.65;
    margin: 0;
    max-width: 460px;
    word-break: keep-all;
}

.folio-hero-preview {
    align-items: center;
    display: flex;
    justify-content: flex-end;
}

.folio-hero-preview-image {
    border: 1px solid var(--folio-border);
    border-radius: 14px;
    box-shadow: 0 16px 48px rgba(11, 31, 63, 0.11);
    display: block;
    height: auto;
    max-height: 230px;
    max-width: 100%;
    object-fit: cover;
    width: min(100%, 400px);
}

/* ── Page Hero (sub-pages) ── */
.folio-page-hero {
    align-items: start;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 16px;
    display: grid;
    gap: 18px;
    grid-template-columns: minmax(0, 1fr) minmax(300px, 0.78fr);
    margin-top: 16px;
    margin-bottom: 20px;
    min-height: 220px;
    overflow: hidden;
    padding: 22px 20px;
}

.folio-page-hero-copy {
    padding-left: 2px;
}

.folio-page-hero-eyebrow {
    color: var(--folio-blue);
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
    text-transform: uppercase;
}

.folio-page-hero h1 {
    color: var(--folio-navy);
    font-size: 2.15rem;
    font-weight: 800;
    line-height: 1.16;
    margin: 0 0 12px;
    word-break: keep-all;
}

.folio-page-hero p {
    color: var(--folio-muted);
    font-size: 0.92rem;
    line-height: 1.55;
    margin: 0;
    max-width: 440px;
    word-break: keep-all;
}

.folio-page-hero-visual {
    align-items: flex-start;
    background: var(--folio-subtle);
    border-radius: 20px;
    display: flex;
    justify-content: flex-end;
    padding: 6px;
}

.folio-page-hero-visual img,
.folio-page-hero-cover-image {
    border: 1px solid rgba(20, 89, 200, 0.08);
    border-radius: 18px;
    box-shadow: 0 12px 32px rgba(11, 31, 63, 0.08);
    display: block;
    height: 236px;
    object-fit: cover;
    width: min(100%, 420px);
}

.folio-page-hero-visual .folio-auto-cover {
    margin: 0;
    height: 236px;
    width: 100%;
    border-radius: 16px;
}

.folio-page-hero.folio-page-hero-no-visual {
    grid-template-columns: minmax(0, 1fr);
}

/* Hero footer actions styling */
.st-key-folio_hero_footer_actions {
    margin-top: -20px;
    margin-bottom: 24px;
    position: relative;
    z-index: 2;
}

.st-key-folio_hero_footer_actions > div {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-top: none;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 10px 24px rgba(11, 31, 63, 0.05);
    padding: 12px 20px 14px 22px;
}

.st-key-folio_hero_footer_actions [data-testid="stColumn"] {
    align-items: center;
    padding: 0;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action {
    align-items: center;
    display: flex;
    height: 38px;
    justify-content: flex-end;
    margin: 0;
    transform: translateY(5px);
    width: 100%;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action .stButton {
    display: flex;
    justify-content: flex-end;
    width: 100% !important;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action button {
    height: 32px;
    margin: 0 !important;
    min-height: 32px !important;
    width: auto !important;
}

/* Like button appearance -- consolidated here since detail_like_action
   only ever renders nested inside folio_hero_footer_actions. */
.st-key-folio_hero_footer_actions .st-key-detail_like_action button {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 999px;
    color: var(--folio-blue);
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0 12px;
    transition: all 0.13s ease;
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action button:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
}

.st-key-folio_hero_footer_actions .st-key-detail_like_action [data-testid="stTooltipHoverTarget"] {
    display: flex;
    justify-content: flex-end;
    width: 100% !important;
}

.folio-project-detail-hero {
    border-radius: 16px 16px 0 0;
    margin-bottom: 0;
    min-height: 0;
}

.folio-project-detail-hero .folio-page-hero-copy {
    align-self: center;
}

/* ── Responsive ── */
@media (max-width: 768px) {
    .folio-page-hero {
        grid-template-columns: 1fr;
        gap: 16px;
        padding: 20px 16px;
        min-height: auto;
    }

    .folio-page-hero-visual {
        justify-content: center;
    }

    .folio-page-hero-visual img,
    .folio-page-hero-cover-image {
        height: 200px;
        width: 100%;
    }
}

@media (max-width: 860px) {
    .folio-home-hero {
        grid-template-columns: 1fr;
        min-height: 200px;
        padding: 32px 8px 28px;
    }

    .folio-home-copy h1 {
        font-size: 1.9rem;
    }

    .folio-hero-preview {
        display: none;
    }

    .folio-page-hero h1 {
        font-size: 1.5rem;
    }

    .folio-page-hero {
        grid-template-columns: 1fr;
        min-height: 190px;
        padding: 28px 20px;
    }

    .folio-page-hero-visual {
        display: none;
    }
}
"""
