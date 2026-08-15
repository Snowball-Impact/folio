"""Power BI news and update hub."""

from __future__ import annotations

import html
import math
from pathlib import Path

import streamlit as st

from folio_app.components.assets import static_image_src
from folio_app.services import powerbi_content
from folio_app.services.powerbi_content import PowerBINewsItem
from folio_app.services.powerbi_i18n import localize_date

ROOT_DIR = Path(__file__).resolve().parents[2]
NEWS_PAGE_SIZE = 10


def render() -> None:
    content = powerbi_content.load_powerbi_content()

    topic = st.query_params.get("topic") or "news"
    _render_hero(powerbi_content.first_row(content.desktop_rows), topic=topic)
    if topic == "certifications":
        _render_certifications()
    elif topic == "learning":
        _render_learning_content(content.learning_rows, content.learning_program_rows)
    elif topic == "community":
        _render_community_content(content.community_rows)
    else:
        _render_news_board(content.update_rows, content.changelog_rows, content.update_video_rows)


def _render_hero(desktop_row: dict[str, str] | None, *, topic: str) -> None:
    if topic == "certifications":
        _render_certifications_hero()
        return
    if topic == "learning":
        _render_learning_hero()
        return
    if topic == "community":
        _render_community_hero()
        return

    logo_src = static_image_src("reference-powerbi-logo-cropped.webp")
    download_url = desktop_row.get("source_url") if desktop_row else ""
    cta_html = ""
    if download_url:
        cta_html = (
            '<a class="folio-powerbi-hero-cta" '
            f'href="{html.escape(download_url, quote=True)}" target="_blank" rel="noopener">'
            "최신 DESKTOP 다운로드"
            "</a>"
        )
    st.markdown(
        f"""
        <section class="folio-powerbi-hero-shell">
            <div class="folio-powerbi-hero">
                <div>
                    <div class="folio-powerbi-eyebrow">Power BI News</div>
                    <h1>Power BI 소식</h1>
                    <p>
                        Power BI 분석가에게 필요한 Desktop 다운로드, 월간 기능 업데이트,<br>
                        변경 로그를 원문 링크와 함께 모아 번역 및 요약합니다.
                    </p>
                    {cta_html}
                </div>
                <div class="folio-powerbi-hero-visual" aria-label="Power BI">
                    <img src="{logo_src}" alt="Power BI" />
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_community_hero() -> None:
    logo_src = static_image_src("reference-powerbi-logo-cropped.webp")
    st.markdown(
        f"""
        <section class="folio-powerbi-hero-shell">
            <div class="folio-powerbi-hero folio-powerbi-community-hero">
                <div>
                    <div class="folio-powerbi-eyebrow">Power BI Community Blog</div>
                    <h1>Power BI 커뮤니티 소식</h1>
                    <p>
                        Microsoft Fabric Community Blog의 최신 Power BI 글을 모아,<br>
                        실무에 필요한 핵심만 한국어로 번역하고 요약합니다.
                    </p>
                </div>
                <div class="folio-powerbi-hero-visual" aria-label="Power BI 커뮤니티 소식">
                    <img src="{logo_src}" alt="Power BI" />
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_learning_hero() -> None:
    logo_src = static_image_src("reference-powerbi-logo-cropped.webp")
    st.markdown(
        f"""
        <section class="folio-powerbi-hero-shell">
            <div class="folio-powerbi-hero folio-powerbi-learning-hero">
                <div>
                    <div class="folio-powerbi-eyebrow">Power BI Learning</div>
                    <h1>Power BI 학습 콘텐츠</h1>
                    <p>
                        공식 채널과 실무 크리에이터의 Power BI 영상을 모아,<br>
                        DAX, 모델링, 시각화, Fabric 업데이트 흐름을 빠르게 살펴볼 수 있습니다.
                    </p>
                </div>
                <div class="folio-powerbi-hero-visual" aria-label="Power BI 학습 콘텐츠">
                    <img src="{logo_src}" alt="Power BI" />
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_certifications_hero() -> None:
    pl300_src = static_image_src("cert-pl300.png")
    bi_specialist_src = static_image_src("cert-bi-specialist.jpg")
    st.markdown(
        f"""
        <section class="folio-powerbi-hero-shell">
            <div class="folio-powerbi-hero folio-powerbi-cert-hero">
                <div>
                    <div class="folio-powerbi-eyebrow">Power BI Certifications</div>
                    <h1>Power BI 자격증, 공식 경로로 바로 확인하세요.</h1>
                    <p>
                        PL-300과 경영정보시각화능력은 Power BI 분석가의 역량을 보여줄 수 있는 대표 자격증입니다.<br>
                        스터디 클럽에서 시험 준비와 포트폴리오 완성, 웹 배포 피드백까지 함께 이어갈 수 있습니다.
                    </p>
                    <a class="folio-powerbi-hero-cta"
                       href="https://discord.gg/vKb9SKA3k" target="_blank" rel="noopener">
                        스터디 클럽 참여하기
                    </a>
                </div>
                <div class="folio-powerbi-cert-hero-visual" aria-label="Power BI 자격증">
                    <img class="folio-powerbi-cert-hero-badge" src="{pl300_src}" alt="Microsoft Certified Power BI Data Analyst Associate" />
                    <img class="folio-powerbi-cert-hero-poster" src="{bi_specialist_src}" alt="경영정보시각화능력 BI Specialist" />
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_community_content(rows: list[dict[str, str]]) -> None:
    if not rows:
        _render_empty("아직 수집된 커뮤니티 소식이 없습니다.")
        return
    groups = powerbi_content.community_groups(rows)
    tabs = st.tabs([f"{name} ({len(group_rows)})" for name, group_rows in groups.items()])
    for tab, (name, group_rows) in zip(tabs, groups.items()):
        with tab:
            for row in group_rows:
                st.markdown(_community_card_html(row), unsafe_allow_html=True)


def _community_card_html(row: dict[str, str]) -> str:
    title = row.get("title_ko") or row.get("title_en") or "Power BI 커뮤니티 소식"
    summary = row.get("summary_ko") or "Power BI 커뮤니티에서 공유된 최신 글입니다."
    author = row.get("author") or "Community"
    published_at = localize_date(row.get("published_at"))
    topic = row.get("topic") or "실무 팁"
    labels = [label.strip() for label in (row.get("labels") or "").split(";") if label.strip()]
    meta_items = [published_at, author]
    meta = " · ".join(item for item in meta_items if item)
    tags = "".join(f"<span>{_escape(label)}</span>" for label in [topic, *labels[:2]] if label)
    href = html.escape(row.get("source_url") or "#", quote=True)
    return (
        '<article class="folio-powerbi-community-card">'
        f'<div class="folio-powerbi-community-meta">{_escape(meta)}</div>'
        '<div class="folio-powerbi-community-title-row">'
        f"<strong>{_escape(title)}</strong>"
        f'<a class="folio-powerbi-community-link" href="{href}" target="_blank" rel="noopener">원문 보기</a>'
        "</div>"
        '<div class="folio-powerbi-community-summary-row">'
        f"<p>{_escape(summary)}</p>"
        f'<div class="folio-powerbi-video-tags">{tags}</div>'
        "</div>"
        "</article>"
    )


def _render_learning_content(rows: list[dict[str, str]], program_rows: list[dict[str, str]]) -> None:
    if not rows:
        _render_empty("아직 수집된 학습 영상이 없습니다.")
        return
    categories = powerbi_content.learning_categories(rows)
    tabs = st.tabs([f"{category} ({len(category_rows)})" for category, category_rows in categories.items()])
    for tab, (category, category_rows) in zip(tabs, categories.items()):
        with tab:
            _render_learning_programs(powerbi_content.programs_for_category(program_rows, category))
            for start in range(0, len(category_rows), 3):
                cols = st.columns(3)
                for column, row in zip(cols, category_rows[start : start + 3]):
                    with column:
                        st.markdown(_learning_card_html(row), unsafe_allow_html=True)


def _render_learning_programs(rows: list[dict[str, str]]) -> None:
    for row in rows:
        st.markdown(_learning_program_html(row), unsafe_allow_html=True)


def _learning_program_html(row: dict[str, str]) -> str:
    thumbnail_src = _learning_thumbnail_src(row)
    image_html = ""
    if thumbnail_src:
        image_html = (
            '<span class="folio-powerbi-program-thumb">'
            f'<img src="{html.escape(thumbnail_src, quote=True)}" alt="" loading="lazy" />'
            "</span>"
        )
    title = row.get("title_ko") or row.get("title") or "Power BI 공식 학습 과정"
    summary = row.get("summary_ko") or "Power BI 공식 학습 프로그램입니다."
    video_count = row.get("video_count") or ""
    meta = row.get("program_type") or "공식 학습 과정"
    if video_count.isdigit() and int(video_count) > 1:
        meta = f"{meta} · {video_count}개 영상"
    href = html.escape(row.get("playlist_url") or "#", quote=True)
    cta_label = "공식 플레이리스트 보기" if row.get("topic") == "공식 학습" else "학습 프로그램 보기"
    return (
        '<div class="folio-powerbi-program-card">'
        f"{image_html}"
        '<span class="folio-powerbi-program-copy">'
        f'<span class="folio-powerbi-program-meta">{_escape(meta)}</span>'
        f"<strong>{_escape(title)}</strong>"
        f"<em>{_escape(summary)}</em>"
        f'<a class="folio-powerbi-video-open" href="{href}" target="_blank" rel="noopener">{_escape(cta_label)}</a>'
        "</span>"
        "</div>"
    )


def _learning_card_html(row: dict[str, str]) -> str:
    thumbnail_url = _learning_thumbnail_src(row)
    image_html = ""
    if thumbnail_url:
        image_html = (
            '<div class="folio-powerbi-video-thumb">'
            f'<img src="{html.escape(thumbnail_url, quote=True)}" alt="" loading="lazy" />'
            "</div>"
        )
    title = row.get("title_ko") or row.get("title_en") or "Power BI 학습 영상"
    summary = row.get("summary_ko") or "Power BI 학습에 참고할 수 있는 영상입니다."
    channel_name = row.get("channel_name") or "YouTube"
    published_at = localize_date(row.get("published_at"))
    meta_items = [channel_name]
    if published_at:
        meta_items.append(published_at)
    href = html.escape(row.get("video_url") or "#", quote=True)
    return (
        '<div class="folio-powerbi-video-card">'
        f"{image_html}"
        '<span class="folio-powerbi-video-copy">'
        f'<span class="folio-powerbi-video-meta">{_escape(" · ".join(meta_items))}</span>'
        f"<strong>{_escape(title)}</strong>"
        f"<em>{_escape(summary)}</em>"
        '<span class="folio-powerbi-video-action-row">'
        '<span class="folio-powerbi-video-tags">'
        f'<span>{_escape(row.get("channel_type") or "학습")}</span>'
        f'<span>{_escape(row.get("topic") or "Power BI")}</span>'
        "</span>"
        f'<a class="folio-powerbi-video-open" href="{href}" target="_blank" rel="noopener">영상 보기</a>'
        "</span>"
        "</span>"
        "</div>"
    )


def _learning_thumbnail_src(row: dict[str, str]) -> str:
    asset_name = row.get("thumbnail_asset") or ""
    if asset_name and (ROOT_DIR / "folio_app" / "static" / asset_name).exists():
        return static_image_src(asset_name)
    return row.get("thumbnail_url") or ""


def _render_news_board(
    update_rows: list[dict[str, str]],
    changelog_rows: list[dict[str, str]],
    update_video_rows: list[dict[str, str]],
) -> None:
    items = powerbi_content.build_news_items(update_rows, changelog_rows, update_video_rows)
    if not items:
        _render_empty("아직 수집된 Power BI 소식이 없습니다.")
        return

    page_index, total_pages = _current_board_page(len(items))
    start = page_index * NEWS_PAGE_SIZE
    end = start + NEWS_PAGE_SIZE
    for index, item in enumerate(items[start:end], start=start + 1):
        _render_news_item(len(items) - index + 1, item)
    _render_pagination(page_index, total_pages)


def _render_news_item(index: int, item: PowerBINewsItem) -> None:
    markup = (
        '<details class="folio-powerbi-release-row">'
        "<summary>"
        f'<span class="folio-powerbi-row-index">{index}</span>'
        f'<span class="folio-powerbi-row-label">{_escape(item.label)}</span>'
        f'<span class="folio-powerbi-expander-title">{_escape(item.title)}</span>'
        f'{_source_link(item.source_row, label="원문")}'
        "</summary>"
        '<div class="folio-powerbi-release-body">'
        f'{_news_video_html(item.video_row)}'
        f'{_summary_bullets_html(item.bullets)}'
        "</div>"
        "</details>"
    )
    st.markdown(markup, unsafe_allow_html=True)


def _news_video_html(row: dict[str, str] | None) -> str:
    if not row:
        return ""
    title = row.get("title_ko") or row.get("title_en") or "Power BI 업데이트 영상"
    href = html.escape(row.get("video_url") or "#", quote=True)
    thumbnail_url = html.escape(_learning_thumbnail_src(row) or powerbi_content.youtube_thumbnail_url(row), quote=True)
    image_html = f'<img src="{thumbnail_url}" alt="" loading="lazy" />' if thumbnail_url else ""
    return (
        f'<a class="folio-powerbi-news-video" href="{href}" target="_blank" rel="noopener">'
        f'<span class="folio-powerbi-news-video-thumb">{image_html}</span>'
        '<span class="folio-powerbi-news-video-copy">'
        "<span>공식 업데이트 영상</span>"
        f"<strong>{_escape(title)}</strong>"
        "</span>"
        '<span class="folio-powerbi-news-video-link">영상 보기</span>'
        "</a>"
    )


def _render_certifications() -> None:
    st.markdown(
        """
        <section class="folio-powerbi-cert-grid" aria-label="Power BI 자격증 바로가기">
            <a class="folio-powerbi-cert-card folio-powerbi-cert-card-pl300"
               href="https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/pl-300"
               target="_blank" rel="noopener">
                <div class="folio-powerbi-cert-logo" aria-hidden="true">
                    <span>Microsoft Certified</span>
                    <strong>PL-300</strong>
                    <em>Power BI Data Analyst</em>
                </div>
                <div class="folio-powerbi-cert-name">PL-300 Power BI Data Analyst</div>
                <div class="folio-powerbi-cert-link">공식 페이지 바로가기</div>
            </a>
            <a class="folio-powerbi-cert-card folio-powerbi-cert-card-kcci"
               href="https://license.korcham.net/co/examguide.do?mm=28&amp;cd=0108"
               target="_blank" rel="noopener">
                <div class="folio-powerbi-cert-logo" aria-hidden="true">
                    <span>KCCI</span>
                    <strong>BI Specialist</strong>
                    <em>경영정보시각화능력</em>
                </div>
                <div class="folio-powerbi-cert-name">경영정보시각화능력</div>
                <div class="folio-powerbi-cert-link">공식 페이지 바로가기</div>
            </a>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_empty(message: str) -> None:
    st.markdown(f'<div class="folio-powerbi-empty">{_escape(message)}</div>', unsafe_allow_html=True)


def _current_board_page(item_count: int) -> tuple[int, int]:
    total_pages = max(math.ceil(item_count / NEWS_PAGE_SIZE), 1)
    current = int(st.session_state.get("powerbi_news_page", 0))
    current = min(max(current, 0), total_pages - 1)
    st.session_state["powerbi_news_page"] = current
    return current, total_pages


def _render_pagination(page_index: int, total_pages: int) -> None:
    if total_pages <= 1:
        return
    _, previous_col, page_col, next_col, _ = st.columns([1, 0.08, 0.14, 0.08, 1])
    with previous_col:
        if st.button("←", key="powerbi_news_prev", disabled=page_index <= 0, use_container_width=True):
            st.session_state["powerbi_news_page"] = max(page_index - 1, 0)
            st.rerun()
    with page_col:
        st.markdown(
            f'<div class="folio-powerbi-page-indicator">{page_index + 1} / {total_pages}</div>',
            unsafe_allow_html=True,
        )
    with next_col:
        if st.button("→", key="powerbi_news_next", disabled=page_index >= total_pages - 1, use_container_width=True):
            st.session_state["powerbi_news_page"] = min(page_index + 1, total_pages - 1)
            st.rerun()


def _source_link(row: dict[str, str], *, label: str = "원문 보기") -> str:
    source_url = row.get("source_url")
    if not source_url:
        return ""
    return f'<a class="folio-powerbi-link" href="{html.escape(source_url, quote=True)}" target="_blank" rel="noopener">{_escape(label)}</a>'


def _summary_bullets_html(items: list[str]) -> str:
    if not items:
        return ""
    bullets = "".join(f"<li>{_escape(item)}</li>" for item in items)
    return f'<ul class="folio-powerbi-summary-list">{bullets}</ul>'


def _escape(value: object) -> str:
    return html.escape(str(value or "").strip())
