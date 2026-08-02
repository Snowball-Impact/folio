"""Auto-generated project card cover art."""

CSS = """
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

.folio-home-card-overlay {
    bottom: 0;
    display: grid;
    grid-template-areas:
        "title-zone"
        "summary-zone"
        "spacer"
        "tags-zone"
        "footer";
    grid-template-rows: 88px 20px minmax(0, 1fr) 42px 22px;
    left: 0;
    min-height: 0;
    padding: 16px 30px;
    position: absolute;
    right: 0;
    top: 0;
    transition: opacity 0.14s ease;
    z-index: 4;
}

.folio-home-card-title-zone {
    grid-area: title-zone;
    min-height: 0;
    overflow: visible;
    padding-top: 0;
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
    padding-bottom: 12px;
    padding-top: 8px;
}

.folio-home-card-summary {
    align-self: start;
    color: rgba(255, 255, 255, 0.78);
    display: block;
    font-size: 14px;
    height: 20px;
    line-height: 20px;
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
    font-weight: 500;
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
    font-weight: 500;
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

@media (max-width: 860px) {
    .folio-home-card-overlay {
        padding-left: 24px;
        padding-right: 24px;
    }
}
"""
