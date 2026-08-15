"""Scrollable project rails on the home gallery."""

CSS = """
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

.folio-gallery-rail-highlight {
    color: var(--folio-blue);
}

.folio-gallery-rail-wrap {
    margin: -34px 0 -20px;
    padding: 42px 0 0;
}

.folio-gallery-rail-scrollbar {
    background: rgba(11, 31, 63, 0);
    border-radius: 999px;
    cursor: pointer;
    height: 6px;
    margin: 0;
    opacity: 0;
    overflow: hidden;
    position: relative;
    transition: background 0.14s ease, opacity 0.14s ease;
    width: 100%;
}

.folio-gallery-rail-spacer {
    height: 14px;
}

.folio-gallery-rail-scrollbar span {
    background: rgba(20, 89, 200, 0.88);
    border: 1px solid rgba(244, 247, 253, 0.95);
    border-radius: inherit;
    display: block;
    height: 100%;
    left: 0;
    min-width: 44px;
    position: absolute;
    top: 0;
    transition: background 0.14s ease;
    width: 44px;
}

.folio-gallery-rail-wrap:hover .folio-gallery-rail-scrollbar,
.folio-gallery-rail-wrap:focus-within .folio-gallery-rail-scrollbar {
    background: rgba(11, 31, 63, 0.08);
    opacity: 1;
}

.folio-gallery-rail {
    display: flex;
    gap: 18px;
    margin: -24px 0 0;
    overflow-x: auto;
    overflow-y: hidden;
    overscroll-behavior-x: contain;
    padding: 24px 0 56px;
    scroll-padding-left: 4px;
    scroll-snap-type: x proximity;
    scrollbar-width: none;
}

.folio-gallery-rail::-webkit-scrollbar {
    display: none;
    height: 0;
    width: 0;
}

.folio-gallery-rail .folio-home-card {
    flex: 0 0 clamp(330px, 27vw, 400px);
    scroll-snap-align: start;
}

.folio-gallery-rail .folio-home-card:hover {
    box-shadow: 0 14px 30px rgba(11, 31, 63, 0.18);
    transform: translateY(-3px);
    z-index: 2;
}

.folio-gallery-rail .folio-home-card:hover .folio-auto-cover {
    filter: saturate(1.08) contrast(1.03);
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

@media (max-width: 860px) {
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

    .folio-gallery-rail-wrap {
        margin: 0;
        padding: 0;
    }

    .folio-gallery-rail-scrollbar {
        display: none;
    }

    .folio-gallery-rail-spacer {
        display: none;
    }

    .folio-gallery-rail {
        gap: 14px;
        margin: 0;
        max-width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 6px 0 16px;
        scroll-padding-left: 0;
        scroll-snap-type: x mandatory;
        width: 100%;
    }

    .folio-gallery-rail .folio-home-card {
        flex-basis: 100%;
        max-width: 100%;
    }

    .folio-gallery-rail .folio-home-card:hover {
        box-shadow: none;
        transform: none;
    }
}

@media (hover: none) {
    .folio-gallery-rail .folio-home-card:hover {
        box-shadow: none;
        transform: none;
    }
}
"""
