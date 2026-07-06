from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any


DRAFT_FIELDS = (
    "title",
    "one_liner",
    "tags",
    "project_body",
    "power_bi_url",
    "report_url",
    "github_url",
    "thumbnail_url",
    "is_public",
)

WIDGET_SUFFIXES = (
    "title",
    "one_liner",
    "tags",
    "body",
    "power_bi_url",
    "github_url",
    "etc_url",
    "is_public",
)


def draft_state_key(user_id: str, draft_id: str) -> str:
    return f"project_draft:{user_id}:{draft_id}"


def draft_clear_request_key(user_id: str, draft_id: str) -> str:
    return f"project_draft_clear:{user_id}:{draft_id}"


def load_project_draft(
    state: MutableMapping[str, Any],
    user_id: str,
    draft_id: str,
    defaults: dict[str, Any],
) -> dict[str, Any]:
    draft = state.get(draft_state_key(user_id, draft_id))
    if not isinstance(draft, dict):
        return dict(defaults)

    restored = dict(defaults)
    restored.update({field: draft[field] for field in DRAFT_FIELDS if field in draft})
    return restored


def save_project_draft(
    state: MutableMapping[str, Any],
    user_id: str,
    draft_id: str,
    form_data: dict[str, Any],
) -> None:
    state[draft_state_key(user_id, draft_id)] = {
        field: form_data[field]
        for field in DRAFT_FIELDS
        if field in form_data
    }


def clear_project_draft(
    state: MutableMapping[str, Any],
    user_id: str,
    draft_id: str,
    widget_prefix: str,
) -> None:
    state.pop(draft_state_key(user_id, draft_id), None)
    state[draft_clear_request_key(user_id, draft_id)] = widget_prefix


def apply_pending_draft_clear(
    state: MutableMapping[str, Any],
    user_id: str,
    draft_id: str,
) -> bool:
    widget_prefix = state.pop(draft_clear_request_key(user_id, draft_id), None)
    if not isinstance(widget_prefix, str) or not widget_prefix:
        return False
    for suffix in WIDGET_SUFFIXES:
        state.pop(f"{widget_prefix}_{suffix}", None)
    return True
