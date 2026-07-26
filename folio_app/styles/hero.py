"""Home hero banner and the shared sub-page hero (render_hero) used across pages."""

CSS = """
/* ── Home Hero (light) ── */
.folio-home-hero-shell {
    margin-top: -8px;
    position: relative;
}

.folio-home-hero-viewport {
    border-radius: 16px;
    overflow: hidden;
}

.folio-home-hero-track {
    animation: folio-home-hero-slide 10s ease-in-out infinite;
    display: flex;
    width: 200%;
}

.folio-home-hero-shell:hover .folio-home-hero-track {
    animation-play-state: paused;
}

@keyframes folio-home-hero-slide {
    0%,
    42% {
        transform: translateX(0);
    }

    50%,
    92% {
        transform: translateX(-50%);
    }

    100% {
        transform: translateX(0);
    }
}

.folio-home-hero {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 16px;
    color: var(--folio-navy);
    display: grid;
    flex: 0 0 50%;
    gap: 24px;
    grid-template-columns: minmax(0, 1fr) minmax(260px, 0.8fr);
    min-height: 210px;
    padding: 26px 28px 34px;
    width: 50%;
}

.folio-home-guide-hero {
    grid-template-columns: minmax(0, 1fr) minmax(260px, 0.8fr);
}

.folio-home-guide-flow {
    align-items: stretch;
    align-self: center;
    display: grid;
    gap: 0;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    position: relative;
}

.folio-home-guide-flow::before {
    background: linear-gradient(90deg, rgba(20, 89, 200, 0), rgba(20, 89, 200, 0.32), rgba(20, 89, 200, 0));
    content: "";
    height: 2px;
    left: 12%;
    position: absolute;
    right: 12%;
    top: 27px;
}

.folio-home-guide-step {
    display: grid;
    gap: 12px;
    grid-template-rows: 56px 1fr;
    justify-items: center;
    min-width: 0;
    position: relative;
    text-align: center;
}

.folio-home-guide-node {
    align-items: center;
    background: var(--folio-blue);
    border: 5px solid #eef5ff;
    border-radius: 999px;
    box-shadow: 0 10px 24px rgba(20, 89, 200, 0.18);
    color: #ffffff;
    display: flex;
    font-size: 0.78rem;
    font-weight: 800;
    height: 56px;
    justify-content: center;
    letter-spacing: 0.04em;
    position: relative;
    width: 56px;
    z-index: 1;
}

.folio-home-guide-card {
    align-content: start;
    background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
    border: 1px solid rgba(20, 89, 200, 0.12);
    border-radius: 12px;
    box-shadow: 0 12px 28px rgba(11, 31, 63, 0.06);
    box-sizing: border-box;
    display: grid;
    height: 122px;
    padding: 14px 12px;
    width: calc(100% - 10px);
}

.folio-home-guide-card strong {
    color: var(--folio-navy);
    display: block;
    font-size: 0.98rem;
    line-height: 1.25;
    margin-bottom: 6px;
}

.folio-home-guide-card p {
    color: var(--folio-muted);
    font-size: 0.8rem;
    line-height: 1.38;
    margin: 0;
    word-break: keep-all;
}

.folio-home-hero-dots {
    align-items: center;
    bottom: 14px;
    display: flex;
    gap: 8px;
    justify-content: center;
    left: 50%;
    pointer-events: none;
    position: absolute;
    transform: translateX(-50%);
    z-index: 2;
}

.folio-home-hero-dots span {
    animation: folio-home-hero-dot 10s ease-in-out infinite;
    background: #c9d7ea;
    border-radius: 999px;
    display: block;
    height: 6px;
    transform: scaleX(0.72);
    transition: background 0.2s ease, transform 0.2s ease;
    width: 30px;
}

.folio-home-hero-dots span:nth-child(2) {
    animation-delay: -5s;
}

@keyframes folio-home-hero-dot {
    0%,
    42% {
        background: var(--folio-blue);
        transform: scaleX(1);
    }

    50%,
    100% {
        background: #c9d7ea;
        transform: scaleX(0.72);
    }
}

.folio-home-eyebrow {
    color: var(--folio-blue);
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    line-height: 1;
    margin: 0;
    text-transform: uppercase;
}

.folio-home-copy {
    align-items: flex-start;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.folio-home-copy h1 {
    color: var(--folio-navy);
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.05;
    margin: 0;
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
    line-height: 1.48;
    margin: 0;
    max-width: 460px;
    word-break: keep-all;
}

.folio-home-actions {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 10px;
}

.folio-home-actions a {
    align-items: center;
    border-radius: 8px;
    display: inline-flex;
    font-size: 0.94rem;
    font-weight: 600;
    min-height: 42px;
    text-decoration: none !important;
    transition: background 0.14s ease, border-color 0.14s ease, color 0.14s ease, transform 0.14s ease;
    white-space: nowrap;
}

.folio-home-primary-cta {
    background: var(--folio-blue);
    border: 1px solid var(--folio-blue);
    box-shadow: 0 12px 28px rgba(20, 89, 200, 0.2);
    color: #ffffff !important;
    padding: 0 20px;
}

.folio-home-primary-cta:hover {
    background: #0f4aab;
    border-color: #0f4aab;
    color: #ffffff !important;
    transform: translateY(-1px);
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
    margin-top: -8px;
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
        min-height: 180px;
        padding: 24px 8px 34px;
    }

    .folio-home-copy h1 {
        font-size: 1.9rem;
    }

    .folio-home-actions {
        gap: 10px;
        margin-top: 20px;
    }

    .folio-home-actions a {
        font-size: 0.88rem;
        min-height: 40px;
    }

    .folio-hero-preview {
        display: none;
    }

    .folio-home-guide-hero {
        grid-template-columns: 1fr;
    }

    .folio-home-guide-flow {
        gap: 10px;
        grid-template-columns: 1fr;
    }

    .folio-home-guide-flow::before {
        bottom: 20px;
        height: auto;
        left: 28px;
        right: auto;
        top: 20px;
        width: 2px;
    }

    .folio-home-guide-step {
        align-items: center;
        grid-template-columns: 56px minmax(0, 1fr);
        grid-template-rows: 1fr;
        justify-items: stretch;
        text-align: left;
    }

    .folio-home-guide-card {
        min-height: 0;
        padding: 13px 14px;
        width: auto;
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
