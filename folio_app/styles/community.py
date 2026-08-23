"""Community board list, detail, and editor styles."""

CSS = """
.folio-community-hero {
    background: #ffffff;
    border: 1px solid rgba(20, 89, 200, 0.14);
    border-radius: 8px;
    box-shadow: 0 16px 34px rgba(11, 31, 63, 0.06);
    margin: 10px 0 16px;
    padding: 24px 26px;
}

.folio-community-hero span,
.folio-community-editor-head span {
    color: var(--folio-blue);
    display: block;
    font-size: 0.78rem;
    font-weight: 850;
    letter-spacing: 0;
    margin-bottom: 7px;
}

.folio-community-hero h1,
.folio-community-editor-head h1 {
    color: var(--folio-navy);
    font-size: 2rem;
    font-weight: 900;
    line-height: 1.18;
    margin: 0;
}

.folio-community-hero p {
    color: var(--folio-muted);
    font-size: 0.98rem;
    font-weight: 650;
    line-height: 1.55;
    margin: 8px 0 0;
}

.st-key-community_filters [data-testid="stHorizontalBlock"] {
    align-items: center;
}

.folio-community-list {
    display: grid;
    gap: 6px;
    margin-top: 14px;
}

.folio-community-row {
    background: #ffffff;
    border: 1px solid rgba(220, 229, 247, 0.9);
    border-radius: 8px;
    display: grid;
    gap: 6px;
    padding: 14px 16px;
}

.folio-community-row-main {
    align-items: center;
    display: flex;
    gap: 8px;
    min-width: 0;
}

.folio-community-row-main strong {
    color: var(--folio-navy);
    font-size: 1rem;
    font-weight: 850;
    line-height: 1.35;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.folio-community-row-meta {
    color: var(--folio-muted);
    font-size: 0.82rem;
    font-weight: 700;
    line-height: 1.4;
}

.folio-community-badge,
.folio-community-pinned,
.folio-community-detail-category {
    align-items: center;
    border-radius: 999px;
    display: inline-flex;
    flex: 0 0 auto;
    font-size: 0.75rem;
    font-weight: 850;
    line-height: 1;
    min-height: 24px;
    padding: 0 9px;
}

.folio-community-badge-notice,
.folio-community-pinned {
    background: #fff3e8;
    border: 1px solid #ffd9b4;
    color: #9a4a0f;
}

.folio-community-badge-question {
    background: #eaf2ff;
    border: 1px solid #d4e5ff;
    color: var(--folio-blue);
}

.folio-community-badge-tip {
    background: #e7f6f2;
    border: 1px solid #ccece4;
    color: #087568;
}

.folio-community-badge-other {
    background: #f4f6fb;
    border: 1px solid #dde5f2;
    color: #52637a;
}

.folio-community-empty {
    align-items: center;
    background: #ffffff;
    border: 1px dashed rgba(20, 89, 200, 0.24);
    border-radius: 8px;
    color: var(--folio-muted);
    display: grid;
    gap: 6px;
    justify-items: center;
    margin: 18px 0 12px;
    min-height: 120px;
    padding: 28px 18px;
    text-align: center;
}

.folio-community-empty strong {
    color: var(--folio-navy);
    font-size: 1rem;
    font-weight: 850;
}

.folio-community-detail {
    background: #ffffff;
    border: 1px solid rgba(20, 89, 200, 0.14);
    border-radius: 8px;
    box-shadow: 0 16px 34px rgba(11, 31, 63, 0.06);
    margin: 12px 0 12px;
    padding: 26px;
}

.folio-community-detail h1 {
    color: var(--folio-navy);
    font-size: 1.8rem;
    font-weight: 900;
    line-height: 1.25;
    margin: 12px 0 8px;
    word-break: keep-all;
}

.folio-community-detail-meta {
    border-bottom: 1px solid var(--folio-border);
    color: var(--folio-muted);
    font-size: 0.88rem;
    font-weight: 750;
    line-height: 1.5;
    padding-bottom: 18px;
}

.folio-community-detail-body {
    color: var(--folio-navy);
    font-size: 1rem;
    line-height: 1.75;
    padding-top: 22px;
    word-break: keep-all;
}

.folio-community-detail-body a {
    color: var(--folio-blue);
    font-weight: 800;
}

.folio-community-editor-head {
    margin: 14px 0 18px;
}

@media (max-width: 820px) {
    .folio-community-hero,
    .folio-community-detail {
        padding: 20px;
    }

    .folio-community-row-main {
        align-items: flex-start;
        flex-wrap: wrap;
    }

    .folio-community-row-main strong {
        flex-basis: 100%;
        white-space: normal;
    }
}
"""
