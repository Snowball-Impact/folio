"""About page vision panel styling."""

CSS = """
.folio-about-vision-heading {
    margin-bottom: 22px;
    text-align: center;
}

.folio-about-vision-panel {
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    border: 1px solid var(--folio-border);
    border-radius: 14px;
    min-height: 520px;
    overflow: hidden;
    position: relative;
}

.folio-about-phase-label {
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid rgba(220, 229, 247, 0.95);
    border-radius: 999px;
    box-shadow: 0 12px 28px rgba(11, 31, 63, 0.08);
    min-width: 132px;
    padding: 10px 13px;
    position: absolute;
    text-align: center;
}

.folio-about-phase-label small {
    color: var(--folio-blue);
    display: block;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.12em;
    line-height: 1;
    margin-bottom: 5px;
}

.folio-about-phase-label strong {
    color: var(--folio-navy);
    display: block;
    font-size: 12px;
    font-weight: 800;
    line-height: 1.2;
}

.folio-about-phase-1 {
    left: 10%;
    top: 18%;
}

.folio-about-phase-2 {
    left: 30%;
    top: 32%;
}

.folio-about-phase-3 {
    left: 53%;
    top: 48%;
}

.folio-about-phase-4 {
    right: 8%;
    top: 62%;
}

.folio-about-phase-note {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(220, 229, 247, 0.95);
    border-radius: 12px;
    bottom: 24px;
    color: var(--folio-muted);
    font-size: 13px;
    left: 24px;
    line-height: 1.7;
    max-width: 430px;
    padding: 16px 18px;
    position: absolute;
    word-break: keep-all;
}

.folio-about-phase-note strong {
    color: var(--folio-navy);
    display: block;
    font-size: 14px;
    margin-bottom: 5px;
}

@media (max-width: 860px) {
    .folio-about-vision-panel {
        background-position: center top;
        min-height: 360px;
    }

    .folio-about-phase-label {
        border-radius: 10px;
        box-shadow: none;
        display: block;
        left: 16px;
        min-width: 0;
        padding: 9px 11px;
        position: relative;
        right: auto;
        text-align: left;
        top: auto;
        width: calc(100% - 32px);
    }

    .folio-about-phase-label + .folio-about-phase-label {
        margin-top: 8px;
    }

    .folio-about-phase-note {
        bottom: auto;
        left: 16px;
        max-width: none;
        position: relative;
        right: 16px;
        top: auto;
        width: calc(100% - 32px);
    }
}
"""
