"""Power BI news page styles."""

CSS = """
.folio-powerbi-hero-shell {
    margin-top: -8px;
}

.folio-powerbi-hero {
    background: linear-gradient(135deg, #fff8dc 0%, #ffffff 48%, #eaf7f4 100%);
    border: 1px solid rgba(214, 176, 50, 0.32);
    border-radius: 8px;
    display: grid;
    gap: 20px;
    grid-template-columns: minmax(0, 1fr) auto;
    min-height: 230px;
    margin: 0 0 18px;
    padding: 30px 34px;
}

.folio-powerbi-eyebrow {
    color: #806100;
    font-size: 0.78rem;
    font-weight: 900;
    letter-spacing: 0.1em;
    margin: 0 0 10px;
    text-transform: uppercase;
}

.folio-powerbi-hero h1 {
    color: var(--folio-navy);
    font-size: 2.05rem;
    font-weight: 850;
    letter-spacing: 0;
    line-height: 1.22;
    margin: 0;
}

.folio-powerbi-hero p {
    color: var(--folio-muted);
    font-size: 1rem;
    line-height: 1.72;
    margin: 12px 0 0;
    max-width: 720px;
    word-break: keep-all;
}

.folio-powerbi-hero-cta {
    align-items: center;
    background: var(--folio-blue);
    border: 1px solid var(--folio-blue);
    border-radius: 8px;
    color: #ffffff !important;
    display: inline-flex;
    font-size: 0.92rem;
    font-weight: 400;
    justify-content: center;
    line-height: 1;
    margin-top: 20px;
    min-height: 42px;
    padding: 0 16px;
    text-decoration: none !important;
}

.folio-powerbi-hero-cta:hover {
    background: #0f49a8;
    border-color: #0f49a8;
    color: #ffffff !important;
    text-decoration: none !important;
}

.folio-powerbi-hero-visual {
    align-items: center;
    display: flex;
    justify-content: center;
    min-width: 240px;
}

.folio-powerbi-hero-visual img {
    display: block;
    height: auto;
    max-height: 170px;
    max-width: 390px;
    object-fit: contain;
    width: auto;
}

.folio-powerbi-cert-hero {
    background: linear-gradient(135deg, #eef6ff 0%, #ffffff 48%, #fff5cf 100%);
    border-color: rgba(20, 89, 200, 0.18);
    min-height: 230px;
}

.folio-powerbi-cert-hero-visual {
    align-items: center;
    display: grid;
    grid-template-columns: 112px 168px;
    justify-content: end;
    min-width: 340px;
    position: relative;
}

.folio-powerbi-cert-hero-visual img {
    display: block;
    object-fit: contain;
}

.folio-powerbi-cert-hero-badge {
    filter: drop-shadow(0 16px 24px rgba(15, 42, 76, 0.18));
    grid-column: 1 / 3;
    grid-row: 1;
    justify-self: start;
    max-height: 142px;
    max-width: 142px;
    position: relative;
    z-index: 2;
}

.folio-powerbi-cert-hero-poster {
    border: 1px solid rgba(20, 89, 200, 0.18);
    border-radius: 8px;
    box-shadow: 0 18px 28px rgba(15, 42, 76, 0.13);
    grid-column: 2;
    grid-row: 1;
    height: 154px;
    width: 154px;
}

.folio-powerbi-learning-hero {
    background: linear-gradient(135deg, #edf5ff 0%, #ffffff 48%, #eaf7f4 100%);
    border-color: rgba(20, 89, 200, 0.18);
}

.folio-powerbi-community-hero {
    background: linear-gradient(135deg, #edf5ff 0%, #ffffff 50%, #fff7de 100%);
    border-color: rgba(20, 89, 200, 0.18);
}

.folio-powerbi-expander-title {
    color: var(--folio-navy);
}

.folio-powerbi-release-row {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    margin: 3px 0;
}

.folio-powerbi-cert-grid {
    display: grid;
    gap: 16px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    margin: 4px 0 26px;
}

.folio-powerbi-cert-card {
    align-items: center;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    color: var(--folio-navy) !important;
    display: flex;
    flex-direction: column;
    gap: 12px;
    justify-content: center;
    min-height: 238px;
    padding: 22px;
    text-align: center;
    text-decoration: none !important;
    transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.folio-powerbi-cert-card:hover {
    border-color: rgba(20, 89, 200, 0.34);
    box-shadow: 0 14px 32px rgba(15, 42, 76, 0.1);
    color: var(--folio-navy) !important;
    text-decoration: none !important;
    transform: translateY(-1px);
}

.folio-powerbi-cert-logo {
    align-items: center;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    height: 122px;
    justify-content: center;
    max-width: 260px;
    padding: 16px;
    width: 100%;
}

.folio-powerbi-cert-logo span {
    font-size: 0.78rem;
    font-weight: 850;
    letter-spacing: 0.04em;
    line-height: 1.2;
    text-transform: uppercase;
}

.folio-powerbi-cert-logo strong {
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 0;
    line-height: 1.12;
    margin-top: 6px;
}

.folio-powerbi-cert-logo em {
    font-size: 0.84rem;
    font-style: normal;
    font-weight: 800;
    line-height: 1.25;
    margin-top: 6px;
}

.folio-powerbi-cert-card-pl300 .folio-powerbi-cert-logo {
    background: linear-gradient(135deg, #fff0a8 0%, #f7c948 100%);
    border: 1px solid rgba(151, 105, 0, 0.2);
    color: #322400;
}

.folio-powerbi-cert-card-kcci .folio-powerbi-cert-logo {
    background: linear-gradient(135deg, #eaf7f4 0%, #b9e0da 100%);
    border: 1px solid rgba(38, 116, 107, 0.2);
    color: #143f3d;
}

.folio-powerbi-cert-name {
    font-size: 1rem;
    font-weight: 850;
    line-height: 1.35;
}

.folio-powerbi-cert-link {
    align-items: center;
    background: #eaf2ff;
    border: 1px solid rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-blue);
    display: inline-flex;
    font-size: 0.82rem;
    font-weight: 850;
    justify-content: center;
    min-height: 30px;
    padding: 0 12px;
}

.folio-powerbi-video-card {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    color: inherit !important;
    display: grid;
    height: 100%;
    margin: 2px 0 16px;
    overflow: hidden;
    transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.folio-powerbi-program-card {
    align-items: stretch;
    background: linear-gradient(135deg, #f7faff 0%, #ffffff 100%);
    border: 1px solid rgba(20, 89, 200, 0.2);
    border-radius: 8px;
    display: grid;
    gap: 16px;
    grid-template-columns: 250px minmax(0, 1fr);
    margin: 2px 0 16px;
    padding: 14px;
}

.folio-powerbi-program-thumb {
    align-self: center;
    aspect-ratio: 16 / 9;
    background: #edf3fb;
    border-radius: 8px;
    display: block;
    overflow: hidden;
}

.folio-powerbi-program-thumb img {
    display: block;
    height: 100%;
    object-fit: cover;
    width: 100%;
}

.folio-powerbi-program-copy {
    display: grid;
    gap: 8px;
    grid-template-rows: auto auto 1fr auto;
    min-width: 0;
    min-height: 100%;
}

.folio-powerbi-program-meta {
    color: var(--folio-muted);
    font-size: 0.78rem;
    font-weight: 850;
    line-height: 1.25;
}

.folio-powerbi-program-copy strong {
    color: var(--folio-navy);
    display: block;
    font-size: 1.12rem;
    font-weight: 850;
    letter-spacing: 0;
    line-height: 1.35;
}

.folio-powerbi-program-copy em {
    color: #263f63;
    display: block;
    font-size: 0.9rem;
    font-style: normal;
    line-height: 1.5;
    word-break: keep-all;
}

.folio-powerbi-video-card:hover {
    border-color: rgba(20, 89, 200, 0.34);
    box-shadow: 0 14px 32px rgba(15, 42, 76, 0.1);
    transform: translateY(-1px);
}

.folio-powerbi-community-card {
    align-items: start;
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 8px;
    display: grid;
    gap: 6px;
    grid-template-columns: 1fr;
    margin: 3px 0;
    min-height: 82px;
    padding: 12px 12px 12px 16px;
}

.folio-powerbi-community-card:hover {
    border-color: rgba(20, 89, 200, 0.28);
    box-shadow: 0 10px 24px rgba(15, 42, 76, 0.07);
}

.folio-powerbi-community-title-row,
.folio-powerbi-community-summary-row {
    align-items: start;
    display: grid;
    gap: 14px;
    grid-template-columns: minmax(0, 1fr) auto;
    min-width: 0;
}

.folio-powerbi-community-meta {
    color: var(--folio-muted);
    font-size: 0.76rem;
    font-weight: 850;
    line-height: 1.25;
}

.folio-powerbi-community-title-row strong {
    color: var(--folio-navy);
    display: block;
    font-size: 1rem;
    font-weight: 850;
    letter-spacing: 0;
    line-height: 1.35;
    word-break: keep-all;
}

.folio-powerbi-community-summary-row p {
    color: #263f63;
    font-size: 0.88rem;
    line-height: 1.45;
    margin: 0;
    word-break: keep-all;
}

.folio-powerbi-community-summary-row .folio-powerbi-video-tags {
    justify-content: flex-end;
    max-width: 300px;
}

.folio-powerbi-community-link {
    align-items: center;
    background: #eaf2ff;
    border: 1px solid rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-blue) !important;
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 850;
    justify-content: center;
    justify-self: end;
    min-height: 30px;
    padding: 0 10px;
    text-decoration: none !important;
    white-space: nowrap;
}

.folio-powerbi-community-link:hover {
    background: #dceaff;
    text-decoration: none !important;
}

.folio-powerbi-video-thumb {
    aspect-ratio: 16 / 9;
    background: #edf3fb;
    overflow: hidden;
}

.folio-powerbi-video-thumb img {
    display: block;
    height: 100%;
    object-fit: cover;
    width: 100%;
}

.folio-powerbi-video-copy {
    display: grid;
    gap: 8px;
    grid-template-rows: auto auto 1fr auto;
    padding: 12px 13px 13px;
}

.folio-powerbi-video-meta {
    color: var(--folio-muted);
    font-size: 0.76rem;
    font-weight: 800;
    line-height: 1.25;
}

.folio-powerbi-video-copy strong {
    color: var(--folio-navy);
    display: block;
    font-size: 0.98rem;
    font-weight: 850;
    letter-spacing: 0;
    line-height: 1.35;
    margin: 0;
    min-height: 2.7em;
    word-break: keep-all;
}

.folio-powerbi-video-copy em {
    color: #263f63;
    display: block;
    font-size: 0.86rem;
    font-style: normal;
    line-height: 1.48;
    margin: 0;
    min-height: 3.8em;
    word-break: keep-all;
}

.folio-powerbi-video-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.folio-powerbi-video-action-row {
    align-items: end;
    display: grid;
    gap: 10px;
    grid-template-columns: minmax(0, 1fr) auto;
}

.folio-powerbi-video-action-row .folio-powerbi-video-tags {
    min-width: 0;
}

.folio-powerbi-video-tags span {
    align-items: center;
    background: #f7faff;
    border: 1px solid rgba(20, 89, 200, 0.16);
    border-radius: 999px;
    color: #315783;
    display: inline-flex;
    font-size: 0.72rem;
    font-weight: 850;
    line-height: 1;
    min-height: 24px;
    padding: 0 8px;
}

.folio-powerbi-video-open {
    align-items: center;
    background: #eaf2ff;
    border: 1px solid rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-blue) !important;
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 850;
    justify-content: center;
    justify-self: end;
    min-height: 28px;
    padding: 0 10px;
    text-decoration: none !important;
    white-space: nowrap;
}

.folio-powerbi-video-open:hover {
    background: #dceaff;
    text-decoration: none !important;
}

.folio-powerbi-news-video {
    align-items: center;
    background: #f7faff;
    border: 1px solid rgba(20, 89, 200, 0.18);
    border-radius: 8px;
    color: inherit !important;
    display: grid;
    gap: 10px;
    grid-template-columns: 112px minmax(0, 1fr) auto;
    margin: 0 0 8px;
    padding: 8px;
    text-decoration: none !important;
}

.folio-powerbi-news-video:hover {
    background: #eef5ff;
    border-color: rgba(20, 89, 200, 0.3);
    text-decoration: none !important;
}

.folio-powerbi-news-video-thumb {
    align-items: center;
    aspect-ratio: 16 / 9;
    background: #e7eef8;
    border-radius: 6px;
    display: flex;
    justify-content: center;
    overflow: hidden;
}

.folio-powerbi-news-video-thumb img {
    display: block;
    height: 100%;
    object-fit: cover;
    width: 100%;
}

.folio-powerbi-news-video-copy {
    display: grid;
    gap: 3px;
    min-width: 0;
}

.folio-powerbi-news-video-copy span {
    color: var(--folio-muted);
    font-size: 0.74rem;
    font-weight: 850;
    line-height: 1.2;
}

.folio-powerbi-news-video-copy strong {
    color: var(--folio-navy);
    font-size: 0.9rem;
    font-weight: 850;
    line-height: 1.35;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.folio-powerbi-news-video-link {
    align-items: center;
    background: #eaf2ff;
    border: 1px solid rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-blue);
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 850;
    justify-content: center;
    min-height: 28px;
    padding: 0 10px;
    white-space: nowrap;
}

.folio-powerbi-release-row summary {
    align-items: center;
    cursor: pointer;
    display: grid;
    gap: 10px;
    grid-template-columns: auto 38px 128px minmax(0, 1fr) auto;
    justify-content: space-between;
    min-height: 34px;
    padding: 4px 10px;
}

.folio-powerbi-release-row summary::-webkit-details-marker {
    display: none;
}

.folio-powerbi-release-row summary::before {
    color: var(--folio-muted);
    content: ">";
    flex: 0 0 auto;
    font-size: 18px;
    line-height: 1;
    transform: rotate(0deg);
    transition: transform 0.14s ease;
}

.folio-powerbi-release-row[open] summary::before {
    transform: rotate(90deg);
}

.folio-powerbi-release-row .folio-powerbi-expander-title {
    font-size: 0.92rem;
    font-weight: 850;
    min-width: 0;
    text-align: left;
}

.folio-powerbi-row-label {
    align-items: center;
    background: #f7faff;
    border: 1px solid rgba(20, 89, 200, 0.18);
    border-radius: 999px;
    color: #315783;
    display: inline-flex;
    font-size: 0.74rem;
    font-weight: 850;
    justify-content: center;
    line-height: 1;
    padding: 5px 8px;
    width: 128px;
    white-space: nowrap;
}

.folio-powerbi-row-index {
    color: var(--folio-muted);
    font-size: 0.78rem;
    font-weight: 850;
    text-align: right;
}

.folio-powerbi-release-body {
    border-top: 1px solid rgba(220, 229, 247, 0.82);
    padding: 6px 12px 7px 30px;
}

.folio-powerbi-summary-list {
    color: #263f63;
    display: grid;
    gap: 3px;
    font-size: 0.88rem;
    line-height: 1.42;
    list-style-position: outside;
    margin: 0 0 3px 18px;
    padding: 0;
    word-break: keep-all;
}

.folio-powerbi-summary-list li {
    padding-left: 2px;
}

.folio-powerbi-link {
    align-items: center;
    background: #eaf2ff;
    border: 1px solid rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-blue) !important;
    display: inline-flex;
    font-size: 0.78rem;
    font-weight: 850;
    flex: 0 0 auto;
    min-height: 24px;
    padding: 0 8px;
    text-decoration: none !important;
}

.folio-powerbi-link:hover {
    background: #dceaff;
    border-color: rgba(20, 89, 200, 0.42);
    text-decoration: none !important;
}

.folio-powerbi-page-indicator {
    align-items: center;
    color: var(--folio-muted);
    display: flex;
    font-size: 0.86rem;
    font-weight: 850;
    justify-content: center;
    min-height: 36px;
}

.st-key-powerbi_news_prev button,
.st-key-powerbi_news_next button {
    align-items: center !important;
    background: transparent !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 999px !important;
    box-shadow: none !important;
    color: var(--folio-navy) !important;
    display: inline-flex !important;
    font-family: Arial, sans-serif !important;
    font-size: 18px !important;
    font-weight: 850 !important;
    height: 32px !important;
    justify-content: center !important;
    line-height: 1 !important;
    margin: 2px auto 0 !important;
    min-height: 32px !important;
    padding: 0 !important;
    width: 32px !important;
}

.st-key-powerbi_news_prev button p,
.st-key-powerbi_news_next button p {
    color: var(--folio-navy) !important;
    font-family: Arial, sans-serif !important;
    font-size: 18px !important;
    font-weight: 850 !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.st-key-powerbi_news_prev button:hover,
.st-key-powerbi_news_next button:hover {
    background: #eaf2ff !important;
    border-color: rgba(20, 89, 200, 0.28) !important;
    transform: none !important;
}

.folio-powerbi-empty {
    background: rgba(255, 255, 255, 0.74);
    border: 1px dashed var(--folio-border);
    border-radius: 8px;
    color: var(--folio-muted);
    font-size: 0.95rem;
    padding: 18px;
}

@media (max-width: 820px) {
    .folio-powerbi-hero {
        grid-template-columns: 1fr;
        padding: 24px 20px;
    }

    .folio-powerbi-hero-visual {
        justify-content: flex-start;
        min-width: 0;
    }

    .folio-powerbi-hero-visual img {
        max-height: 120px;
        max-width: 320px;
    }

    .folio-powerbi-cert-hero-visual {
        grid-template-columns: 100px 142px;
        justify-content: flex-start;
        min-width: 0;
    }

    .folio-powerbi-cert-hero-badge {
        max-height: 120px;
        max-width: 120px;
    }

    .folio-powerbi-cert-hero-poster {
        height: 132px;
        width: 132px;
    }

    .folio-powerbi-cert-grid {
        grid-template-columns: 1fr;
    }

    .folio-powerbi-news-video {
        grid-template-columns: 96px minmax(0, 1fr);
    }

    .folio-powerbi-news-video-link {
        grid-column: 1 / -1;
        justify-self: flex-start;
    }

    .folio-powerbi-program-card {
        grid-template-columns: 1fr;
    }

    .folio-powerbi-community-title-row,
    .folio-powerbi-community-summary-row {
        grid-template-columns: 1fr;
    }

    .folio-powerbi-community-link {
        justify-self: flex-start;
    }

    .folio-powerbi-community-summary-row .folio-powerbi-video-tags {
        justify-content: flex-start;
        max-width: none;
    }
}
"""
