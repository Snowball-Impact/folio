"""Profile summary markup for My Page."""

from __future__ import annotations

import html


def profile_overview_html(user: dict, profile: dict, projects: list[dict], stats: dict[str, int]) -> str:
    public_count = sum(1 for project in projects if project.get("is_public"))
    like_count = sum(project.get("like_count", 0) or 0 for project in projects)

    name = profile.get("name") or user.get("email") or ""
    email = profile.get("email") or user.get("email") or ""
    organization = profile.get("organization") or ""
    bio = profile.get("bio") or ""

    organization_label = organization or "소속을 추가해 나를 더 잘 소개해 보세요"
    bio_label = bio or "아직 자기소개가 없습니다. 어떤 관점으로 데이터를 바라보는지 들려주세요."

    return f"""
    <div class="folio-profile-identity">
        <div class="folio-profile-identity-copy">
            <dl class="folio-profile-fields">
                <div>
                    <dt>작성자</dt>
                    <dd class="folio-profile-name">{html.escape(name)}</dd>
                </div>
                <div>
                    <dt>소속</dt>
                    <dd class="folio-profile-info-org{' is-empty' if not organization else ''}">{html.escape(organization_label)}</dd>
                </div>
                <div>
                    <dt>이메일</dt>
                    <dd class="folio-profile-email">{html.escape(email)}</dd>
                </div>
            </dl>
        </div>
    </div>
    <div class="folio-profile-about">
        <p class="folio-profile-bio{' is-empty' if not bio else ''}">{html.escape(bio_label)}</p>
    </div>
    <div class="folio-profile-stats">
        <span><small>전체 프로젝트</small><strong>{stats["project_count"]}</strong></span>
        <span><small>공개 프로젝트</small><strong>{public_count}</strong></span>
        <span><small>누적 조회</small><strong>{stats["view_count"]:,}</strong></span>
        <span><small>총 좋아요</small><strong>{like_count:,}</strong></span>
    </div>
    """
