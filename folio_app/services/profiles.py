from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from folio_app.services.supabase_client import get_supabase_client


@dataclass(frozen=True)
class OnboardingStatus:
    required: bool
    profile: dict[str, Any] | None
    policies: dict[str, dict[str, Any]]
    consented_policy_ids: set[str]
    error_message: str | None = None

    @property
    def missing_policy_types(self) -> list[str]:
        return [
            policy_type
            for policy_type, policy in self.policies.items()
            if policy.get("id") not in self.consented_policy_ids
        ]

    @property
    def is_complete(self) -> bool:
        return self.error_message is None and not self.missing_policy_types


def ensure_profile(
    user_id: str,
    email: str,
    name: str = "",
    organization: str = "",
) -> dict[str, Any] | None:
    client = get_supabase_client()
    if client is None:
        return None

    existing = (
        client.table("profiles")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]

    payload = {
        "id": user_id,
        "email": email,
        "name": name or email.split("@")[0],
        "organization": organization,
    }

    try:
        response = client.table("profiles").insert(payload).execute()
    except Exception:
        # The auth trigger may create the profile between the read and insert.
        repaired = (
            client.table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )
        if repaired.data:
            return repaired.data[0]
        raise
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


def get_onboarding_status(user_id: str) -> OnboardingStatus:
    try:
        profile = get_profile(user_id)
        policies = get_required_policy_versions()
        consented_policy_ids = get_user_consented_policy_ids(user_id)
    except Exception:
        return OnboardingStatus(
            required=True,
            profile=None,
            policies={},
            consented_policy_ids=set(),
            error_message="온보딩 정보를 불러오지 못했습니다. 잠시 후 다시 시도하세요.",
        )

    if not policies:
        return OnboardingStatus(
            required=False,
            profile=profile,
            policies=policies,
            consented_policy_ids=consented_policy_ids,
        )

    status = OnboardingStatus(
        required=True,
        profile=profile,
        policies=policies,
        consented_policy_ids=consented_policy_ids,
    )
    return status


def get_required_policy_versions() -> dict[str, dict[str, Any]]:
    client = get_supabase_client()
    if client is None:
        return {}

    response = (
        client.table("policy_versions")
        .select("*")
        .eq("is_active", True)
        .order("effective_at", desc=True)
        .execute()
    )

    policies: dict[str, dict[str, Any]] = {}
    for policy in response.data or []:
        policy_type = policy.get("policy_type")
        if policy_type in {"terms", "privacy"} and policy_type not in policies:
            policies[policy_type] = policy
    return policies


def get_user_consented_policy_ids(user_id: str) -> set[str]:
    client = get_supabase_client()
    if client is None:
        return set()

    response = (
        client.table("user_policy_consents")
        .select("policy_version_id")
        .eq("user_id", user_id)
        .execute()
    )
    return {
        consent["policy_version_id"]
        for consent in response.data or []
        if consent.get("policy_version_id")
    }


def update_profile(
    user_id: str,
    name: str,
    organization: str = "",
    bio: str = "",
) -> None:
    client = get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase 환경 변수가 설정되지 않았습니다.")

    client.table("profiles").update(
        {"name": name, "organization": organization, "bio": bio}
    ).eq("id", user_id).execute()


def complete_onboarding(
    user_id: str,
    policy_version_ids: list[str],
) -> None:
    client = get_supabase_client()
    if client is None:
        raise RuntimeError("Supabase 환경 변수가 설정되지 않았습니다.")

    existing_policy_ids = get_user_consented_policy_ids(user_id)
    consent_rows = [
        {
            "user_id": user_id,
            "policy_version_id": policy_version_id,
        }
        for policy_version_id in policy_version_ids
        if policy_version_id not in existing_policy_ids
    ]
    if consent_rows:
        client.table("user_policy_consents").insert(consent_rows).execute()
