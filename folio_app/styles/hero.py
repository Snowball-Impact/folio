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
    animation: folio-home-hero-slide 20s ease-in-out infinite;
    display: flex;
    width: 400%;
}

.folio-home-hero-shell:hover .folio-home-hero-track,
.folio-home-hero-shell:hover .folio-home-hero-dots span {
    animation-play-state: paused;
}

@keyframes folio-home-hero-slide {
    0%,
    20% {
        transform: translateX(0);
    }

    25%,
    45% {
        transform: translateX(-25%);
    }

    50%,
    70% {
        transform: translateX(-50%);
    }

    75%,
    95% {
        transform: translateX(-75%);
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
    flex: 0 0 25%;
    gap: 18px;
    grid-template-columns: minmax(0, 1.1fr) minmax(420px, 0.72fr);
    min-height: 220px;
    padding: 28px 41px 34px;
    width: 25%;
}

.folio-home-guide-hero {
    grid-template-columns: minmax(0, 0.82fr) minmax(520px, 1fr);
}

.folio-home-guide-flow {
    align-items: stretch;
    align-self: center;
    display: grid;
    gap: 8px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    justify-self: end;
    width: 85%;
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
    height: 98px;
    padding: 11px 10px;
    width: 100%;
}

.folio-home-guide-card strong {
    color: var(--folio-navy);
    display: block;
    font-size: 0.88rem;
    line-height: 1.25;
    margin-bottom: 4px;
}

.folio-home-guide-card p {
    color: var(--folio-muted);
    font-size: 14px;
    line-height: 1.32;
    margin: 0;
    word-break: keep-all;
}

.folio-home-powerbi-flow .folio-home-guide-node {
    background: #f2c811;
    color: #0b1f3f;
}

.folio-home-powerbi-flow .folio-home-guide-card {
    border-color: rgba(242, 200, 17, 0.32);
    box-shadow: 0 14px 30px rgba(11, 31, 63, 0.08);
}

.folio-home-powerbi-flow .folio-home-guide-card strong {
    color: #0b1f3f;
}

.folio-home-study-flow .folio-home-guide-node {
    background: var(--folio-blue);
}

.folio-home-study-flow .folio-home-guide-card {
    border-color: rgba(10, 148, 133, 0.28);
    box-shadow: 0 14px 30px rgba(10, 148, 133, 0.08);
}

.folio-home-study-flow .folio-home-guide-card strong {
    color: #0f4a7a;
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
    background: #c9d7ea;
    border-radius: 999px;
    display: block;
    height: 6px;
    transform: scaleX(0.72);
    transition: background 0.2s ease, transform 0.2s ease;
    width: 30px;
}

.folio-home-hero-dots span:nth-child(1) {
    animation: folio-home-hero-dot-one 20s ease-in-out infinite;
}

.folio-home-hero-dots span:nth-child(2) {
    animation: folio-home-hero-dot-two 20s ease-in-out infinite;
}

.folio-home-hero-dots span:nth-child(3) {
    animation: folio-home-hero-dot-three 20s ease-in-out infinite;
}

.folio-home-hero-dots span:nth-child(4) {
    animation: folio-home-hero-dot-four 20s ease-in-out infinite;
}

@keyframes folio-home-hero-dot-one {
    0%,
    20% {
        background: var(--folio-blue);
        transform: scaleX(1);
    }

    25%,
    100% {
        background: #c9d7ea;
        transform: scaleX(0.72);
    }
}

@keyframes folio-home-hero-dot-two {
    0%,
    20%,
    50%,
    100% {
        background: #c9d7ea;
        transform: scaleX(0.72);
    }

    25%,
    45% {
        background: var(--folio-blue);
        transform: scaleX(1);
    }
}

@keyframes folio-home-hero-dot-three {
    0%,
    45%,
    75%,
    100% {
        background: #c9d7ea;
        transform: scaleX(0.72);
    }

    50%,
    70% {
        background: var(--folio-blue);
        transform: scaleX(1);
    }
}

@keyframes folio-home-hero-dot-four {
    0%,
    70%,
    100% {
        background: #c9d7ea;
        transform: scaleX(0.72);
    }

    75%,
    95% {
        background: var(--folio-blue);
        transform: scaleX(1);
    }
}

.folio-home-eyebrow {
    color: var(--folio-blue);
    font-size: 1.2rem;
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
    gap: 12px;
}

.folio-home-copy h1 {
    color: var(--folio-navy);
    font-size: calc(2.45rem - 4px);
    font-weight: 800;
    line-height: 1.22;
    margin: 0;
    text-wrap: nowrap;
    white-space: nowrap;
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

.folio-home-actions {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 8px;
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
    max-height: 246px;
    max-width: 100%;
    object-fit: cover;
    width: min(100%, 440px);
}

/* ── Page Hero (sub-pages) ── */
.folio-page-hero {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 16px;
    display: grid;
    gap: 18px;
    grid-template-columns: minmax(0, 1.1fr) minmax(420px, 0.72fr);
    margin-top: -8px;
    margin-bottom: 20px;
    min-height: 220px;
    overflow: hidden;
    padding: 28px 41px 34px;
}

.folio-page-hero-copy {
    align-items: flex-start;
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding-left: 2px;
}

.folio-page-hero-copy::after {
    content: "";
    display: block;
    height: 50px;
    margin-top: 8px;
}

.folio-page-hero-eyebrow {
    color: var(--folio-blue);
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    line-height: 1;
    margin-bottom: 0;
    text-transform: uppercase;
}

.folio-page-hero h1 {
    color: var(--folio-navy);
    font-size: 2.45rem;
    font-weight: 800;
    line-height: 1.22;
    margin: 0;
    word-break: keep-all;
}

.folio-page-hero p {
    color: var(--folio-muted);
    font-size: 0.98rem;
    line-height: 1.65;
    margin: 0;
    max-width: 440px;
    word-break: keep-all;
}

.folio-page-hero-visual {
    align-items: flex-start;
    aspect-ratio: 16 / 9;
    background: var(--folio-subtle);
    border-radius: 20px;
    box-sizing: border-box;
    display: flex;
    justify-content: flex-end;
    justify-self: end;
    padding: 6px;
    width: min(100%, 440px);
}

.folio-submit-preview-hero .folio-page-hero-visual {
    background: transparent;
    padding: 0;
}

.folio-submit-preview-hero .folio-page-hero-visual .folio-home-card {
    border-radius: 18px;
}

.folio-page-hero-visual img,
.folio-page-hero-cover-image {
    aspect-ratio: 16 / 9;
    border: 1px solid rgba(20, 89, 200, 0.08);
    border-radius: 18px;
    box-shadow: 0 12px 32px rgba(11, 31, 63, 0.08);
    display: block;
    height: 100%;
    object-fit: cover;
    width: 100%;
}

.folio-page-hero-visual .folio-auto-cover {
    aspect-ratio: 16 / 9;
    height: 100%;
    margin: 0;
    width: 100%;
    border-radius: 16px;
}

.folio-page-hero.folio-page-hero-no-visual {
    grid-template-columns: minmax(0, 1fr);
}

.folio-project-detail-hero {
    border-radius: 16px 16px 0 0;
    margin-bottom: 0;
    min-height: 0;
    padding-bottom: 22px;
    padding-top: 22px;
}

.folio-project-detail-hero .folio-page-hero-copy {
    align-self: center;
}

.folio-project-detail-hero .folio-page-hero-copy::after {
    display: none;
}

.folio-project-detail-hero .folio-page-hero-eyebrow {
    font-size: 1.05rem;
    font-weight: 800;
    margin-bottom: 14px;
}

.folio-project-detail-hero h1 {
    font-size: 2.15rem;
    line-height: 1.16;
}

.folio-project-detail-hero p {
    font-size: 0.92rem;
    line-height: 1.55;
}

.folio-project-detail-hero .folio-page-hero-visual {
    align-items: stretch;
}

.folio-project-detail-hero .folio-page-hero-visual .folio-home-card {
    aspect-ratio: 16 / 9;
    box-shadow: 0 12px 32px rgba(11, 31, 63, 0.08);
    height: auto;
    width: 100%;
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
        aspect-ratio: 16 / 9;
        height: 100%;
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
        text-wrap: balance;
        text-align: center;
        white-space: normal;
    }

    .folio-home-copy {
        align-items: center;
        text-align: center;
    }

    .folio-home-copy p {
        text-align: center;
    }

    .folio-home-actions {
        justify-content: center;
        gap: 10px;
        margin-top: 20px;
        width: 100%;
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
        display: none;
    }

    .folio-home-guide-flow::before {
        display: none;
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
