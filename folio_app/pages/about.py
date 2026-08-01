"""Service introduction page."""

from __future__ import annotations

import streamlit as st

from folio_app.components.assets import static_image_src


_CONTACT_MAILTO = (
    "mailto:contact@snowballimpact.com"
    "?subject=FOLIO%20%EC%84%9C%EB%B9%84%EC%8A%A4%20%EB%AC%B8%EC%9D%98"
)
_SERVICE_STEPS = (
    (
        "01 RECORD",
        "맥락을 함께 기록합니다.",
        (
            "제목, 소개, 태그, 본문, 결과물 링크를 한 화면에 묶습니다.",
            "왜 만들었는지와 무엇을 만들었는지가 함께 남습니다.",
        ),
    ),
    (
        "02 SHARE",
        "공개하고 탐색합니다.",
        (
            "홈 갤러리에서 최근 등록순, 조회순, 좋아요순으로 프로젝트를 살펴봅니다.",
            "관심 있는 프로젝트는 상세 페이지에서 바로 확인합니다.",
        ),
    ),
    (
        "03 GROW",
        "반응을 보고 개선합니다.",
        (
            "조회, 좋아요, 공유로 프로젝트의 반응을 확인합니다.",
            "다음 단계에서는 댓글을 붙여 피드백까지 연결합니다.",
        ),
    ),
)
_CAPABILITIES = (
    ("프로젝트 등록", "프로젝트명, 한 줄 소개, 태그, 본문을 입력합니다."),
    ("결과물 연결", "대시보드, 보고서, GitHub 주소를 연결합니다."),
    ("갤러리 탐색", "최근 등록순, 조회순, 좋아요순으로 프로젝트를 둘러봅니다."),
    ("반응 확인", "조회수, 좋아요, 공유 링크로 반응을 확인합니다."),
    ("피드백 확장", "댓글을 통해 프로젝트별 의견을 남기는 흐름을 준비합니다."),
    ("포트폴리오 관리", "마이페이지에서 프로필과 등록 프로젝트를 관리합니다."),
)
_VISION_PHASES = (
    ("folio-about-phase-1", "PHASE 1", "Portfolio<br />Platform"),
    ("folio-about-phase-2", "PHASE 2", "Community"),
    ("folio-about-phase-3", "PHASE 3", "Best Practice<br />Archive"),
    ("folio-about-phase-4", "PHASE 4", "Career<br />Network"),
)


def render() -> None:
    st.html(
        f"""
        <main class="folio-about-page">
            {_hero_section()}
            {_team_section()}
            {_service_section()}
            {_vision_section()}
        </main>
        """
    )


def _hero_section() -> str:
    gapyear_banner = static_image_src("gapyear-hero-banner.jpg")
    return f"""
    <section class="folio-about-hero">
        <div class="folio-about-hero-banner">
            <img src="{gapyear_banner}" alt="경기청년 갭이어 프로그램 배너" />
        </div>
        <div class="folio-about-hero-caption">
            <strong>경기청년 갭이어 2026의 지원을 받아 시작했습니다.</strong>
            <p>
                <span class="folio-about-line">FOLIO는 경기도가 지원하는 경기청년 갭이어 2026 사업을 통해 시작한 프로젝트입니다.</span>
                <span class="folio-about-line">지원금을 바탕으로 아이디어를 실제 서비스로 구현하고 있습니다.</span>
            </p>
        </div>
    </section>
    """


def _team_section() -> str:
    team_image = static_image_src("snowball-impact.png")
    return f"""
    <section class="folio-about-section">
        <div class="folio-about-team">
            <div class="folio-about-team-image">
                <img src="{team_image}" alt="Snowball Impact 팀 캐릭터" />
            </div>
            <div class="folio-about-team-copy">
                <div class="folio-about-eyebrow">TEAM SNOWBALL IMPACT</div>
                <h1>
                    <span class="folio-about-line">작은 기록이 쌓여</span>
                    <span class="folio-about-line">다음 프로젝트의 근거가 되도록.</span>
                </h1>
                <p>
                    <span class="folio-about-line">Snowball Impact는 FOLIO를 만들고 있는 팀입니다.</span>
                    <span class="folio-about-line">프로젝트가 한 번의 제출로 끝나지 않고, 다음 시도와 연결되는 구조를 실험하고 있습니다.</span>
                </p>
                <div class="folio-about-team-status">
                    <span>지금은 서비스 MVP를 직접 구현하며 검증하는 단계입니다.</span>
                    <a class="folio-about-contact" href="{_CONTACT_MAILTO}">Contact Us</a>
                </div>
            </div>
        </div>
    </section>
    """


def _service_section() -> str:
    service_steps = "\n".join(_service_step_html(*step) for step in _SERVICE_STEPS)
    capabilities = "\n".join(_capability_html(*capability) for capability in _CAPABILITIES)
    return f"""
    <section class="folio-about-section">
        <div class="folio-about-section-heading">
            <h2>FOLIO는 프로젝트를 어떻게 남기나요?</h2>
            <p>
                <span class="folio-about-line">결과를 올리는 데서 끝나지 않습니다.</span>
                <span class="folio-about-line">기록, 공개, 피드백의 흐름으로 프로젝트를 관리합니다.</span>
            </p>
        </div>
        <div class="folio-about-service-flow">
            {service_steps}
        </div>
        <div class="folio-about-capabilities">
            {capabilities}
        </div>
    </section>
    """


def _vision_section() -> str:
    vision_image = static_image_src("vision-snowball.png")
    phases = "\n".join(_vision_phase_html(*phase) for phase in _VISION_PHASES)
    return f"""
    <section class="folio-about-section">
        <div class="folio-about-vision-heading">
            <h2>VISION</h2>
        </div>
        <div class="folio-about-vision-panel" style="background-image: url('{vision_image}');" aria-label="Snowball Impact 비전 이미지와 단계">
            {phases}
            <div class="folio-about-phase-note">
                <strong>Snowball Impact</strong>
                <span class="folio-about-line">프로젝트를 모으고, 피드백을 연결하고,</span>
                <span class="folio-about-line">좋은 사례를 축적해 커리어 기회로 확장합니다.</span>
            </div>
        </div>
    </section>
    """


def _service_step_html(label: str, title: str, lines: tuple[str, str]) -> str:
    body = "\n".join(f'<span class="folio-about-line">{line}</span>' for line in lines)
    return f"""
    <div class="folio-about-service-step">
        <small>{label}</small>
        <h3>{title}</h3>
        <p>{body}</p>
    </div>
    """


def _capability_html(title: str, body: str) -> str:
    return f"""
    <div class="folio-about-capability">
        <strong>{title}</strong>
        <span>{body}</span>
    </div>
    """


def _vision_phase_html(position_class: str, label: str, title_html: str) -> str:
    return (
        f'<div class="folio-about-phase-label {position_class}">'
        f"<small>{label}</small><strong>{title_html}</strong>"
        "</div>"
    )
