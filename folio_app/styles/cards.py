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
    transform-origin: center center;
    transition: box-shadow 0.18s ease, transform 0.18s ease;
    z-index: 1;
}

.folio-gallery-rail .folio-home-card:hover {
    box-shadow: 0 26px 58px rgba(11, 31, 63, 0.26);
    transform: translateY(-8px) scale(1.5);
    z-index: 30;
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
    z-index: 8;
}

.folio-home-card-activity-badge {
    align-items: center;
    background: #dc2626;
    border: 1px solid rgba(255, 255, 255, 0.48);
    border-radius: 999px;
    box-shadow: 0 8px 18px rgba(11, 31, 63, 0.2);
    color: #fff;
    display: inline-flex;
    font-size: 11px;
    font-weight: 600;
    height: 24px;
    letter-spacing: 0;
    line-height: 1;
    padding: 0 9px;
    pointer-events: none;
    position: absolute;
    right: 14px;
    top: 14px;
    z-index: 9;
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
    overflow-y: visible;
    overscroll-behavior-x: contain;
    padding: 30px 0 36px;
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

.folio-gallery-rail .folio-home-card:first-child {
    transform-origin: left center;
}

.folio-gallery-rail .folio-home-card:last-child {
    transform-origin: right center;
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
    --folio-cover-bg: linear-gradient(135deg, #19a7ce, #76d7c4);
    background:
        radial-gradient(circle at 86% 16%, rgba(255, 255, 255, 0.28), transparent 28%),
        var(--folio-cover-bg);
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

.folio-gallery-rail .folio-home-card:hover .folio-auto-cover {
    filter: saturate(1.08) contrast(1.03);
}

.folio-home-card .folio-auto-cover::after {
    background: linear-gradient(
        180deg,
        rgba(11, 31, 63, 0.08) 0%,
        rgba(11, 31, 63, 0.22) 42%,
        rgba(11, 31, 63, 0.78) 100%
    );
    content: "";
    inset: 0;
    position: absolute;
    z-index: 1;
}

.folio-home-card-preview {
    background: rgba(11, 31, 63, 0.92);
    inset: 0;
    opacity: 0;
    overflow: hidden;
    pointer-events: none;
    position: absolute;
    transform: scale(1.015);
    transition: opacity 0.18s ease, transform 0.18s ease;
    z-index: 2;
}

.folio-home-card-has-preview:hover .folio-home-card-preview,
.folio-home-card-has-preview:focus-within .folio-home-card-preview {
    opacity: 1;
    transform: scale(1);
}

.folio-home-card-preview-frame {
    border: 0;
    height: 100%;
    inset: 0;
    pointer-events: none;
    position: absolute;
    width: 100%;
}

.folio-home-card-preview-label {
    align-items: center;
    background: linear-gradient(180deg, rgba(11, 31, 63, 0.18), rgba(11, 31, 63, 0.72));
    color: rgba(255, 255, 255, 0.86);
    display: flex;
    font-size: 13px;
    font-weight: 800;
    inset: 0;
    justify-content: center;
    letter-spacing: 0.02em;
    position: absolute;
    z-index: 1;
}

.folio-home-card-preview.is-loaded .folio-home-card-preview-label {
    opacity: 0;
}

.folio-home-card-has-preview:hover .folio-home-card-overlay,
.folio-home-card-has-preview:focus-within .folio-home-card-overlay {
    background: linear-gradient(180deg, rgba(11, 31, 63, 0.08) 0%, rgba(11, 31, 63, 0.12) 42%, rgba(11, 31, 63, 0.88) 100%);
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
    z-index: 4;
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
    background:
        linear-gradient(90deg, rgba(255, 255, 255, 0.22) 1px, transparent 1px),
        linear-gradient(180deg, rgba(255, 255, 255, 0.18) 1px, transparent 1px);
    background-size: 18px 18px;
    border-radius: 26px;
    height: 126px;
    opacity: 0.5;
    position: absolute;
    right: -18px;
    top: -22px;
    transform: rotate(8deg);
    width: 156px;
}

.folio-auto-cover-pattern::after {
    background: rgba(255, 255, 255, 0.16);
    border-radius: 50%;
    content: "";
    height: 86px;
    left: 54px;
    position: absolute;
    top: 34px;
    width: 86px;
}

.folio-auto-cover-0 .folio-auto-cover-pattern,
.folio-auto-cover-2 .folio-auto-cover-pattern,
.folio-auto-cover-4 .folio-auto-cover-pattern,
.folio-auto-cover-6 .folio-auto-cover-pattern,
.folio-auto-cover-8 .folio-auto-cover-pattern,
.folio-auto-cover-10 .folio-auto-cover-pattern,
.folio-auto-cover-12 .folio-auto-cover-pattern,
.folio-auto-cover-14 .folio-auto-cover-pattern,
.folio-auto-cover-16 .folio-auto-cover-pattern,
.folio-auto-cover-18 .folio-auto-cover-pattern,
.folio-auto-cover-20 .folio-auto-cover-pattern,
.folio-auto-cover-22 .folio-auto-cover-pattern {
    background:
        linear-gradient(90deg, rgba(255, 255, 255, 0.2) 1px, transparent 1px),
        linear-gradient(180deg, rgba(255, 255, 255, 0.2) 1px, transparent 1px);
    background-size: 14px 14px;
}

.folio-auto-cover-1 .folio-auto-cover-pattern,
.folio-auto-cover-3 .folio-auto-cover-pattern,
.folio-auto-cover-5 .folio-auto-cover-pattern,
.folio-auto-cover-7 .folio-auto-cover-pattern,
.folio-auto-cover-9 .folio-auto-cover-pattern,
.folio-auto-cover-11 .folio-auto-cover-pattern,
.folio-auto-cover-13 .folio-auto-cover-pattern,
.folio-auto-cover-15 .folio-auto-cover-pattern,
.folio-auto-cover-17 .folio-auto-cover-pattern,
.folio-auto-cover-19 .folio-auto-cover-pattern,
.folio-auto-cover-21 .folio-auto-cover-pattern,
.folio-auto-cover-23 .folio-auto-cover-pattern {
    background: repeating-radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.24) 0 2px, transparent 2px 15px);
    border-radius: 50%;
}

.folio-auto-cover-0,
.folio-auto-cover-1 { --folio-cover-bg: linear-gradient(135deg, #256fd8, #62c9e8); }
.folio-auto-cover-2,
.folio-auto-cover-3 { --folio-cover-bg: linear-gradient(135deg, #1496a8, #76d7c4); }
.folio-auto-cover-4,
.folio-auto-cover-5 { --folio-cover-bg: linear-gradient(135deg, #12846f, #8fd6b3); }
.folio-auto-cover-6,
.folio-auto-cover-7 { --folio-cover-bg: linear-gradient(135deg, #3f9967, #a8d977); }
.folio-auto-cover-8,
.folio-auto-cover-9 { --folio-cover-bg: linear-gradient(135deg, #8aa83d, #d7d96f); }
.folio-auto-cover-10,
.folio-auto-cover-11 { --folio-cover-bg: linear-gradient(135deg, #d19a2a, #f1cf68); }
.folio-auto-cover-12,
.folio-auto-cover-13 { --folio-cover-bg: linear-gradient(135deg, #d4743f, #f2b36f); }
.folio-auto-cover-14,
.folio-auto-cover-15 { --folio-cover-bg: linear-gradient(135deg, #c95c5c, #ee9a8f); }
.folio-auto-cover-16,
.folio-auto-cover-17 { --folio-cover-bg: linear-gradient(135deg, #c65b85, #eda5bd); }
.folio-auto-cover-18,
.folio-auto-cover-19 { --folio-cover-bg: linear-gradient(135deg, #a35fb7, #d4a3df); }
.folio-auto-cover-20,
.folio-auto-cover-21 { --folio-cover-bg: linear-gradient(135deg, #6d63cc, #a9a6e8); }
.folio-auto-cover-22,
.folio-auto-cover-23 { --folio-cover-bg: linear-gradient(135deg, #486fc5, #96b2e8); }

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

    .folio-gallery-rail .folio-home-card:hover {
        box-shadow: 0 14px 30px rgba(11, 31, 63, 0.18);
        transform: translateY(-3px) scale(1.03);
    }
}
"""
