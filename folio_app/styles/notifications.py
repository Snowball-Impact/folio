"""Notifications page list and states."""

CSS = """
.st-key-notifications_panel {
    background: var(--folio-surface) !important;
    border: 1px solid var(--folio-border) !important;
    border-radius: 14px !important;
    padding: 22px 24px !important;
}

.folio-notifications-heading {
    align-items: center;
    border-bottom: 1px solid var(--folio-border);
    display: flex;
    gap: 14px;
    justify-content: space-between;
    margin-bottom: 14px;
    padding-bottom: 14px;
}

.folio-notifications-heading h2 {
    color: var(--folio-navy);
    font-size: 20px;
    font-weight: 800;
    margin: 0;
}

.folio-notifications-heading p {
    color: var(--folio-muted);
    font-size: 13px;
    margin: 0;
    text-align: right;
}

.folio-notifications-empty {
    background: #f7faff;
    border: 1px dashed var(--folio-border);
    border-radius: 10px;
    color: var(--folio-muted);
    font-size: 14px;
    padding: 18px;
    text-align: center;
}

[class*="st-key-notification_item_"] {
    border-bottom: 1px solid rgba(201, 216, 238, 0.72);
    padding: 10px 0 !important;
}

[class*="st-key-notification_item_"]:last-child {
    border-bottom: 0;
}

.folio-notification-item {
    align-items: center;
    display: grid;
    gap: 12px;
    grid-template-columns: 68px minmax(0, 1fr) 132px;
    min-height: 34px;
}

.folio-notification-state {
    border-radius: 999px;
    display: inline-flex;
    font-size: 11px;
    font-weight: 600;
    justify-content: center;
    padding: 4px 8px;
    white-space: nowrap;
}

.folio-notification-item.is-unread .folio-notification-state {
    background: #fee2e2;
    color: #b91c1c;
}

.folio-notification-item.is-read .folio-notification-state {
    background: #eef3fb;
    color: var(--folio-muted);
}

.folio-notification-item strong {
    color: var(--folio-navy);
    font-size: 14px;
    font-weight: 700;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.folio-notification-item time {
    color: var(--folio-muted);
    font-size: 12px;
    text-align: right;
    white-space: nowrap;
}

[class*="st-key-notification_item_"] .stButton {
    display: flex !important;
    justify-content: flex-end !important;
    margin-top: 4px !important;
}

[class*="st-key-notification_item_"] .stButton > button {
    border-radius: 999px !important;
    font-size: 12px !important;
    min-height: 30px !important;
    padding: 0 12px !important;
    width: auto !important;
}

@media (max-width: 760px) {
    .folio-notifications-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 6px;
    }

    .folio-notifications-heading p {
        text-align: left;
    }

    .folio-notification-item {
        align-items: flex-start;
        grid-template-columns: 1fr;
        gap: 6px;
    }

    .folio-notification-item time {
        text-align: left;
    }
}
"""
