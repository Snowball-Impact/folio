"""Home page project card grid, including the auto-generated cover art."""

CSS = """
/* ── Project Cards (grid) ── */
.folio-home-card {
    background: var(--folio-surface);
    border: 1px solid var(--folio-border);
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    min-height: 350px;
    overflow: hidden;
    padding: 0 16px 14px;
    transition: border-color 0.16s, box-shadow 0.16s, transform 0.16s;
}

.folio-home-card-compact {
    min-height: 160px;
}

.folio-card-link,
.folio-card-link:visited,
.folio-card-link:active {
    color: inherit;
    display: block;
    text-decoration: none !important;
}

.folio-card-link:hover,
.folio-card-link:hover *,
.folio-card-link *,
.folio-card-link:visited * {
    color: inherit;
    text-decoration: none !important;
}

.folio-card-link:hover .folio-home-card {
    border-color: rgba(20, 89, 200, 0.4);
    box-shadow: 0 8px 28px rgba(11, 31, 63, 0.1);
    transform: translateY(-2px);
}

.folio-card-link .folio-home-card p,
.folio-card-link .folio-home-metrics,
.folio-card-link .folio-detail-meta {
    color: var(--folio-muted);
}

.folio-card-link .folio-tag {
    color: #0a7a72;
}

.folio-home-card p {
    color: var(--folio-muted);
    display: -webkit-box;
    font-size: 0.85rem;
    line-height: 1.55;
    margin: 0;
    min-height: 40px;
    overflow: hidden;
    word-break: keep-all;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
}

.folio-home-author {
    color: var(--folio-navy) !important;
    display: block !important;
    font-size: 0.78rem !important;
    font-weight: 700;
    margin: 12px 0 5px !important;
    min-height: auto !important;
}

.folio-auto-cover {
    aspect-ratio: 16 / 9;
    background: linear-gradient(135deg, #0d3b86, #1768ce);
    box-sizing: border-box;
    color: #ffffff;
    height: auto;
    margin: 0 -16px;
    overflow: hidden;
    padding: 18px 18px 9px;
    position: relative;
}

.folio-auto-cover-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    position: relative;
    z-index: 2;
}

.folio-auto-cover-eyebrow {
    color: rgba(255, 255, 255, 0.82) !important;
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.13em;
    opacity: 0.72;
}

.folio-auto-cover h3,
.folio-card-link .folio-auto-cover h3 {
    color: #ffffff;
    display: -webkit-box;
    font-size: 1.12rem;
    font-weight: 800;
    line-height: 1.4;
    margin: 12px 0 0;
    overflow: hidden;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.14);
    word-break: keep-all;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
}

.folio-auto-cover-tags {
    display: flex;
    gap: 7px;
    justify-content: flex-end;
    margin-top: auto;
    min-height: 22px;
}

.folio-auto-cover-tags span {
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.24);
    border-radius: 999px;
    color: #ffffff;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 3px 8px;
}

.folio-auto-cover-pattern {
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 50%;
    height: 112px;
    position: absolute;
    right: -28px;
    top: -30px;
    width: 112px;
}

.folio-auto-cover-pattern::after {
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 50%;
    content: "";
    height: 70px;
    left: 20px;
    position: absolute;
    top: 20px;
    width: 70px;
}

.folio-auto-cover-1 { background: linear-gradient(135deg, #086b72, #0ba3a0); }
.folio-auto-cover-2 { background: linear-gradient(135deg, #4932a8, #705ad7); }
.folio-auto-cover-3 { background: linear-gradient(135deg, #8a3c18, #d46a2b); }
.folio-auto-cover-4 { background: linear-gradient(135deg, #155e43, #2c9972); }
.folio-auto-cover-5 { background: linear-gradient(135deg, #7a2455, #bb4380); }

.folio-home-metrics {
    align-items: center;
    color: var(--folio-muted);
    display: flex;
    font-size: 0.8rem;
    gap: 18px;
    justify-content: flex-end;
    margin-top: auto;
    padding-top: 12px;
    min-width: 0;
}

.folio-home-metrics span {
    align-items: center;
    display: inline-flex;
    gap: 4px;
    flex-shrink: 0;
    min-width: 0;
}

.folio-home-metrics span + span {
    margin-left: 12px;
}

.folio-home-metrics svg {
    fill: none;
    height: 15px;
    stroke: currentColor;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-width: 1.8;
    width: 15px;
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .folio-home-card {
        min-height: 240px;
    }
}
"""
