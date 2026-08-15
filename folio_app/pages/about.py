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
        "01 DISCOVER",
        "좋은 시각화 사례를 발견합니다.",
        (
            "Tableau, Power BI, Data Studio, Streamlit 레퍼런스를 한곳에서 탐색합니다.",
            "플랫폼보다 주제와 문제의식 중심으로 프로젝트를 비교합니다.",
        ),
    ),
    (
        "02 EXPERIENCE",
        "직접 열어보고 체험합니다.",
        (
            "임베드 가능한 대시보드는 상세 페이지에서 바로 조작합니다.",
            "임베드가 어려운 프로젝트는 원본 링크와 맥락을 함께 확인합니다.",
        ),
    ),
    (
        "03 SHARE",
        "내 프로젝트도 연결합니다.",
        (
            "제작자는 자신의 결과물과 분석 과정을 등록해 공개할 수 있습니다.",
            "댓글과 반응은 다음 개선을 위한 작은 피드백 루프가 됩니다.",
        ),
    ),
)
_VISION_PHASES = (
    ("folio-about-phase-1", "STEP 1", "좋은 사례가<br />모입니다"),
    ("folio-about-phase-2", "STEP 2", "비교할 기준이<br />생깁니다"),
    ("folio-about-phase-3", "STEP 3", "만든 사람이<br />드러납니다"),
    ("folio-about-phase-4", "STEP 4", "다음 기회로<br />이어집니다"),
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
    team_image = static_image_src("snowball-impact.webp")
    return f"""
    <section class="folio-about-section">
        <div class="folio-about-team">
            <div class="folio-about-team-image">
                <img src="{team_image}" alt="Snowball Impact 팀 캐릭터" />
            </div>
            <div class="folio-about-team-copy">
                <div class="folio-about-eyebrow">TEAM SNOWBALL IMPACT</div>
                <h1>
                    <span class="folio-about-line">좋은 시각화 사례를 모아</span>
                    <span class="folio-about-line">다음 질문의 출발점이 되도록.</span>
                </h1>
                <p>
                    <span class="folio-about-line">Snowball Impact는 FOLIO를 만들고 있는 팀입니다.</span>
                    <span class="folio-about-line">흩어진 데이터 시각화 프로젝트를 발견하고, 직접 경험하고, 함께 이야기하는 구조를 실험하고 있습니다.</span>
                </p>
                <div class="folio-about-team-status">
                    <span>지금은 공개 레퍼런스 갤러리와 제작자 직접 등록 흐름을 함께 검증하는 단계입니다.</span>
                    <a class="folio-about-contact" href="{_CONTACT_MAILTO}">Contact Us</a>
                </div>
            </div>
        </div>
    </section>
    """


def _service_section() -> str:
    service_steps = "\n".join(_service_step_html(*step) for step in _SERVICE_STEPS)
    return f"""
    <section class="folio-about-section">
        <div class="folio-about-section-heading">
            <h2>FOLIO는 어떤 프로젝트를 보여주나요?</h2>
            <p>
                <span class="folio-about-line">파일이나 링크만 모으는 공간이 아닙니다.</span>
                <span class="folio-about-line">문제의식, 분석 과정, 인터랙티브 결과물, 사용자 의견을 함께 축적합니다.</span>
            </p>
        </div>
        <div class="folio-about-service-flow">
            {service_steps}
        </div>
    </section>
    """


def _vision_section() -> str:
    vision_image = static_image_src("vision-snowball.webp")
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
                <span class="folio-about-line">좋은 프로젝트가 모이면 기준이 되고,</span>
                <span class="folio-about-line">기준이 생기면 사람과 기회가 모입니다.</span>
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


def _vision_phase_html(position_class: str, label: str, title_html: str) -> str:
    return (
        f'<div class="folio-about-phase-label {position_class}">'
        f"<small>{label}</small><strong>{title_html}</strong>"
        "</div>"
    )
