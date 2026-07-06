"""Small cross-cutting helpers reused across cards, hero footers, and detail pages."""

CSS = """
/* ── Tags ── */
.folio-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin: 8px 0 10px;
}

.folio-tag {
    background: #eaf5f3;
    border: 1px solid #c0e5e0;
    border-radius: 999px;
    color: #0a7a72;
    display: inline-flex;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 3px 9px;
}

/* ── Detail Meta ── */
.folio-detail-meta {
    color: var(--folio-muted);
    display: flex;
    flex-wrap: wrap;
    font-size: 0.84rem;
    gap: 10px;
    margin: -4px 0 6px;
}

/* ── Muted helper ── */
.folio-muted {
    color: var(--folio-muted);
}
"""
