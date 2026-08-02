from __future__ import annotations

from collections import Counter
from datetime import datetime
import logging

import streamlit as st

from folio_app.services.comment_utils import parse_timestamp
from folio_app.services.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


def count_comments_by_project(project_ids: list[str]) -> dict[str, int]:
    return _fetch_comment_counts(tuple(sorted(set(project_ids))))


def latest_comment_at_by_project(project_ids: list[str]) -> dict[str, str]:
    return _fetch_latest_comment_times(tuple(sorted(set(project_ids))))


@st.cache_data(ttl=15, show_spinner=False)
def _fetch_comment_counts(project_ids: tuple[str, ...]) -> dict[str, int]:
    client = get_supabase_client()
    if not project_ids:
        return {}
    if client is None:
        return {}

    try:
        response = (
            client.table("comments")
            .select("project_id")
            .in_("project_id", list(project_ids))
            .execute()
        )
    except Exception:
        logger.exception("Failed to count project comments")
        return {}

    counter: Counter[str] = Counter()
    for comment in response.data or []:
        project_id = comment.get("project_id")
        if project_id:
            counter[project_id] += 1
    return dict(counter)


@st.cache_data(ttl=15, show_spinner=False)
def _fetch_latest_comment_times(project_ids: tuple[str, ...]) -> dict[str, str]:
    client = get_supabase_client()
    if not project_ids:
        return {}
    if client is None:
        return {}

    try:
        response = (
            client.table("comments")
            .select("project_id, created_at")
            .in_("project_id", list(project_ids))
            .execute()
        )
    except Exception:
        logger.exception("Failed to load latest project comment times")
        return {}

    latest_by_project: dict[str, datetime] = {}
    latest_raw_by_project: dict[str, str] = {}
    for comment in response.data or []:
        project_id = comment.get("project_id")
        raw_created_at = comment.get("created_at")
        created_at = parse_timestamp(raw_created_at)
        if not project_id or created_at is None:
            continue
        current = latest_by_project.get(project_id)
        if current is None or created_at > current:
            latest_by_project[project_id] = created_at
            latest_raw_by_project[project_id] = raw_created_at
    return latest_raw_by_project


def clear_comment_caches() -> None:
    _fetch_comment_counts.clear()
    _fetch_latest_comment_times.clear()

