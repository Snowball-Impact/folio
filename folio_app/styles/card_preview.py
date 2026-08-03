"""Hover-mounted dashboard preview for project cards in the home gallery."""

CSS = """
.folio-gallery-rail .folio-home-card-has-preview {
    --folio-preview-frame-height: 150%;
    --folio-preview-frame-scale: 0.6666667;
    --folio-preview-frame-width: 150%;
}

.folio-gallery-rail .folio-home-card-preview-streamlit {
    --folio-preview-frame-height: 225%;
    --folio-preview-frame-scale: 0.4444444;
    --folio-preview-frame-width: 225%;
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
    height: var(--folio-preview-frame-height, 100%);
    inset: 0;
    pointer-events: none;
    position: absolute;
    transform: scale(var(--folio-preview-frame-scale, 1));
    transform-origin: top left;
    width: var(--folio-preview-frame-width, 100%);
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
    opacity: 0;
}

@media (max-width: 860px) {
    .folio-gallery-rail .folio-home-card-has-preview {
        --folio-preview-frame-height: 100%;
        --folio-preview-frame-scale: 1;
        --folio-preview-frame-width: 100%;
    }

    .folio-home-card-preview {
        display: none;
    }

    .folio-home-card-has-preview:hover .folio-home-card-overlay,
    .folio-home-card-has-preview:focus-within .folio-home-card-overlay {
        opacity: 1;
    }
}

@media (hover: none) {
    .folio-home-card-preview {
        display: none;
    }

    .folio-home-card-has-preview:hover .folio-home-card-overlay,
    .folio-home-card-has-preview:focus-within .folio-home-card-overlay {
        opacity: 1;
    }
}
"""
