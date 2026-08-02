"""Header notification button and popover styling."""

CSS = """
.st-key-nav_Notifications .stButton > button {
    align-items: center !important;
    display: inline-flex !important;
    justify-content: center !important;
    min-width: 24px !important;
}

.st-key-nav_Notifications {
    margin-left: 18px !important;
    position: relative;
}

.st-key-nav_Notifications button {
    align-items: center !important;
    background: transparent !important;
    border: none !important;
    color: rgba(225, 234, 255, 0.82) !important;
    display: inline-flex !important;
    height: 36px !important;
    justify-content: center !important;
    min-height: 36px !important;
    min-width: 24px !important;
    padding: 6px 0 !important;
    position: relative;
}

.st-key-nav_Notifications button:hover {
    background: transparent !important;
    color: #ffffff !important;
}

.st-key-nav_Notifications button p {
    display: none !important;
}

.st-key-nav_Notifications .stPopover {
    width: auto !important;
}

.st-key-nav_Notifications .stButton > button p {
    display: none !important;
}

.folio-header-notifications-title {
    align-items: center;
    display: flex;
    gap: 16px;
    justify-content: space-between;
    min-width: 280px;
    padding-bottom: 8px;
}

.folio-header-notifications-title strong {
    color: var(--folio-navy);
    font-size: 15px;
    font-weight: 800;
}

.folio-header-notifications-title span {
    color: var(--folio-muted);
    font-size: 12px;
}

.folio-header-notification-preview {
    border-top: 1px solid var(--folio-border);
    padding: 9px 0 7px;
}

.folio-header-notification-preview span {
    color: #b91c1c;
    display: block;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 3px;
}

.folio-header-notification-preview strong {
    color: var(--folio-navy);
    display: block;
    font-size: 13px;
    font-weight: 700;
    max-width: 280px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

@media (max-width: 640px) {
    .st-key-nav_Notifications {
        margin-left: 12px !important;
    }
}

@media (max-width: 420px) {
    .st-key-nav_Notifications {
        margin-left: 9px !important;
    }
}
"""
