from __future__ import annotations

from typing import Any

from folio_app.services.supabase_client import get_supabase_client


def ensure_profile(
    user_id: str,
    email: str,
    name: str = "",
    organization: str = "",
) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        return None

    payload = {
        "id": user_id,
        "email": email,
        "name": name or email.split("@")[0],
        "organization": organization,
    }

    response = client.table("profiles").upsert(payload, on_conflict="id").execute()
    if response.data:
        return response.data[0]
    return None


def get_profile(user_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        return None

    response = client.table("profiles").select("*").eq("id", user_id).single().execute()
    return response.data


def profile_exists_for_email(email: str) -> bool:
    client = get_supabase_client()
    if client is None:
        return False

    response = (
        client.table("profiles")
        .select("id")
        .eq("email", email.strip().lower())
        .limit(1)
        .execute()
    )
    return bool(response.data)
