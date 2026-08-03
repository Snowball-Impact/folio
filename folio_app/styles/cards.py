"""Home page project card shell and metadata."""

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

.folio-home-card-compact {
    min-height: 160px;
}

.folio-home-card-cover-image {
    aspect-ratio: 16 / 9;
    display: block;
    height: auto;
    object-fit: cover;
    position: relative;
    width: 100%;
    z-index: 0;
}

.folio-home-card-has-thumbnail::before {
    background: linear-gradient(
        180deg,
        rgba(4, 12, 28, 0.34) 0%,
        rgba(4, 12, 28, 0.58) 45%,
        rgba(4, 12, 28, 0.88) 100%
    );
    content: "";
    inset: 0;
    pointer-events: none;
    position: absolute;
    z-index: 1;
}

.folio-home-card-cover-image + .folio-home-card-preview {
    z-index: 2;
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
}
"""
