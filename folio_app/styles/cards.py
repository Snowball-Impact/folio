"""Home page project card grid, including the auto-generated cover art."""

CSS = """
/* ── Project Cards (grid) ── */
.folio-home-card {
    background: var(--folio-navy);
    border: 0;
    border-radius: 10px;
    display: block;
    min-height: 0;
    overflow: hidden;
    padding: 0;
    position: relative;
    transition: transform 0.16s ease;
}

.folio-home-card:hover {
    transform: translateY(-4px);
}

.folio-home-card-compact {
    min-height: 160px;
}

/* Streamlit's markdown renderer splits an anchor that wraps block-level
   content into several smaller anchors, one per inline text run, which
   leaves the cover art and padding unclickable. This empty anchor is
   stretched over the whole card instead. */
.folio-card-link {
    inset: 0;
    position: absolute;
    z-index: 5;
}

.folio-home-card p {
    color: rgba(255, 255, 255, 0.76);
    display: -webkit-box;
    font-size: 0.85rem;
    line-height: 1.55;
    margin: 0;
    min-height: 0;
    overflow: hidden;
    word-break: keep-all;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
}

.folio-gallery-heading {
    align-items: flex-end;
    display: flex;
    gap: 18px;
    justify-content: space-between;
    margin: 28px 0 22px;
}

.folio-gallery-heading {
    display: none;
}

.folio-gallery-heading h2 {
    color: var(--folio-navy);
    font-size: 1.57rem;
    font-weight: 800;
    letter-spacing: 0;
    margin: 0;
}

.folio-gallery-heading p {
    color: var(--folio-muted);
    font-size: 1.12rem;
    line-height: 1.45;
    margin: 3px 0 0;
    word-break: keep-all;
}

.folio-gallery-heading span {
    color: var(--folio-muted);
    flex-shrink: 0;
    font-size: 1.09rem;
    font-weight: 800;
}

.folio-gallery-rail-section {
    margin-bottom: 2px;
    overflow: hidden;
    padding: 0;
    width: 100%;
}

.folio-gallery-rail-head {
    align-items: center;
    display: grid;
    grid-template-columns: 36px minmax(0, 1fr) 36px;
    min-height: 36px;
    padding: 0 0 4px;
    text-align: center;
}

.folio-gallery-rail-head h3 {
    color: var(--folio-navy);
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 0;
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.folio-gallery-rail-head p {
    display: none;
    color: var(--folio-muted);
    font-size: 1.07rem;
    line-height: 1.45;
    margin: 3px 0 0;
    word-break: keep-all;
}

.folio-gallery-rail {
    display: flex;
    gap: 18px;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    padding: 6px 0 16px;
    scroll-padding-left: 4px;
    scroll-snap-type: x proximity;
}

.folio-rail-scroll-button {
    align-items: center;
    appearance: none;
    background: transparent;
    border: 0;
    border-radius: 999px;
    color: rgba(11, 31, 63, 0.55);
    cursor: pointer;
    display: inline-flex;
    font-size: 26px;
    font-weight: 700;
    height: 32px;
    justify-content: center;
    line-height: 1;
    margin: 0;
    padding: 0;
    transition: background 0.14s ease, color 0.14s ease, transform 0.14s ease;
    width: 32px;
}

.folio-rail-scroll-button:hover,
.folio-rail-scroll-button:focus-visible {
    background: rgba(255, 255, 255, 0.72);
    color: var(--folio-blue);
    outline: none;
    transform: translateY(-1px);
}

.folio-gallery-rail::-webkit-scrollbar {
    height: 6px;
}

.folio-gallery-rail::-webkit-scrollbar-button {
    display: none;
    height: 0;
    width: 0;
}

.folio-gallery-rail::-webkit-scrollbar-track {
    background: rgba(11, 31, 63, 0);
    border-radius: 999px;
}

.folio-gallery-rail::-webkit-scrollbar-thumb {
    background: rgba(20, 89, 200, 0);
    border: 1px solid rgba(244, 247, 253, 0);
    border-radius: 999px;
}

.folio-gallery-rail {
    scrollbar-color: transparent transparent;
    scrollbar-width: thin;
}

.folio-gallery-rail:hover,
.folio-gallery-rail:focus-within {
    scrollbar-color: rgba(20, 89, 200, 0.88) rgba(11, 31, 63, 0.08);
}

.folio-gallery-rail:hover::-webkit-scrollbar-track,
.folio-gallery-rail:focus-within::-webkit-scrollbar-track {
    background: rgba(11, 31, 63, 0.08);
}

.folio-gallery-rail:hover::-webkit-scrollbar-thumb,
.folio-gallery-rail:focus-within::-webkit-scrollbar-thumb {
    background: rgba(20, 89, 200, 0.88);
    border-color: rgba(244, 247, 253, 0.95);
}

.folio-gallery-rail .folio-home-card {
    flex: 0 0 clamp(330px, 27vw, 400px);
    scroll-snap-align: start;
}

.folio-home-card .folio-home-card-title {
    color: #ffffff !important;
    display: -webkit-box;
    font-size: 20px !important;
    font-weight: 700 !important;
    height: 64px;
    line-height: 30px !important;
    margin: 0 !important;
    min-height: 64px;
    overflow: hidden;
    word-break: keep-all;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
}

.folio-home-footer {
    align-items: center;
    align-self: end;
    display: grid;
    gap: 10px;
    grid-template-columns: minmax(0, 1fr) auto;
    margin-top: 0;
    min-height: 22px;
    padding: 0;
    width: 100%;
}

.folio-home-footer-meta {
    align-items: center;
    display: flex;
    flex: 1 1 auto;
    gap: 8px;
    min-width: 0;
    overflow: hidden;
}

.folio-home-date {
    color: rgba(255, 255, 255, 0.68);
    flex-shrink: 0;
    font-size: 13px;
    font-weight: 700;
}

.folio-home-author {
    color: rgba(255, 255, 255, 0.78) !important;
    display: block !important;
    flex: 1 1 auto;
    font-size: 13px !important;
    font-weight: 700;
    margin: 0 !important;
    min-height: 0 !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.folio-auto-cover {
    aspect-ratio: 16 / 9;
    background: linear-gradient(135deg, #0d3b86, #1768ce);
    box-sizing: border-box;
    color: #ffffff;
    height: auto;
    border-radius: 10px;
    box-shadow: none;
    margin: 0;
    overflow: hidden;
    padding: 18px 27px 9px;
    position: relative;
    transition: box-shadow 0.16s ease, filter 0.16s ease;
}

.folio-home-card:hover .folio-auto-cover {
    filter: saturate(1.08) contrast(1.03);
}

.folio-home-card .folio-auto-cover::after {
    background: linear-gradient(
        180deg,
        rgba(11, 31, 63, 0.02) 0%,
        rgba(11, 31, 63, 0.28) 34%,
        rgba(11, 31, 63, 0.92) 100%
    );
    content: "";
    inset: 0;
    position: absolute;
    z-index: 1;
}

.folio-home-card-overlay {
    bottom: 0;
    display: grid;
    grid-template-areas:
        "title-zone"
        "summary-zone"
        "spacer"
        "tags-zone"
        "footer";
    grid-template-rows: 112px 18px minmax(0, 1fr) 47px 22px;
    left: 0;
    min-height: 0;
    padding: 0 27px 16px;
    position: absolute;
    right: 0;
    top: 0;
    z-index: 3;
}

.folio-home-card-title-zone {
    grid-area: title-zone;
    min-height: 0;
    overflow: visible;
    padding-top: 38px;
}

.folio-home-card-summary-zone {
    grid-area: summary-zone;
    min-height: 0;
    overflow: hidden;
}

.folio-home-card-tags-zone {
    grid-area: tags-zone;
    min-height: 0;
    overflow: hidden;
    padding-bottom: 15px;
    padding-top: 10px;
}

.folio-home-card-summary {
    align-self: start;
    color: rgba(255, 255, 255, 0.78);
    display: block;
    font-size: 14px;
    height: 18px;
    line-height: 18px;
    margin-top: 0;
    min-height: 0 !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 100%;
    -webkit-line-clamp: unset;
}

.folio-home-card-tags {
    align-self: start;
    display: flex;
    flex-wrap: nowrap;
    gap: 5px;
    height: 22px;
    margin-top: 0;
    min-height: 22px;
    overflow: hidden;
    width: 100%;
}

.folio-home-card-tags span {
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 999px;
    color: #ffffff;
    font-size: 11px;
    font-weight: 800;
    line-height: 14px;
    max-width: 120px;
    overflow: hidden;
    padding: 3px 7px;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.folio-home-card-tags .folio-home-card-tag-more {
    background: rgba(255, 255, 255, 0.24);
    cursor: help;
    flex-shrink: 0;
    max-width: none;
}

.folio-home-footer {
    grid-area: footer;
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
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 0.13em;
    opacity: 0.62;
}

.folio-auto-cover h3 {
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
    color: rgba(255, 255, 255, 0.72);
    display: flex;
    flex: 0 0 auto;
    flex-shrink: 0;
    font-size: 13px;
    gap: 12px;
    min-width: max-content;
    margin-left: auto;
}

.folio-home-metrics span {
    align-items: center;
    display: inline-flex;
    gap: 4px;
    flex-shrink: 0;
    min-width: 0;
}

.folio-home-metrics svg {
    fill: none;
    height: 17px;
    stroke: currentColor;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-width: 1.8;
    width: 17px;
}

/* ── Responsive ── */
@media (max-width: 860px) {
    .folio-home-card {
        min-height: 0;
    }

    .folio-gallery-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 6px;
    }

    .folio-gallery-rail-section {
        width: 100%;
    }

    .folio-gallery-rail-head {
        align-items: flex-start;
        flex-direction: column;
        gap: 4px;
    }

    .folio-gallery-rail-head h3 {
        font-size: 14px;
    }

    .folio-gallery-rail {
        gap: 14px;
        padding: 4px 0 14px;
    }

    .folio-gallery-rail .folio-home-card {
        flex-basis: min(82vw, 320px);
    }
}
"""
