import html
import hashlib
import re
from urllib.parse import urlparse


def is_http_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def plain_text(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    return " ".join(html.unescape(text).split())


def clean_html(html_str: str) -> str:
    return "".join(line.strip() for line in html_str.splitlines())


def render_tag_chips(tags: list[str]) -> str:
    if not tags:
        return ""
    chips = "".join(f"<span class='folio-tag'>#{html.escape(tag)}</span>" for tag in tags)
    return f"<div class='folio-tags'>{chips}</div>"


def _cover_variant(project: dict, variant_count: int = 6) -> int:
    seed = str(project.get("id") or project.get("title") or "folio")
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % variant_count


def _render_auto_cover(project: dict, *, compact: bool = False) -> str:
    title = html.escape(project.get("title") or "프로젝트명이 여기에 표시됩니다.")
    tag_html = "".join(
        f"<span>#{html.escape(str(tag))}</span>"
        for tag in (project.get("tags") or [])[:2]
    )
    compact_class = " folio-auto-cover-compact" if compact else ""
    return clean_html(f"""
    <div class="folio-auto-cover folio-auto-cover-{_cover_variant(project)}{compact_class}">
        <div class="folio-auto-cover-pattern" aria-hidden="true"></div>
        <div class="folio-auto-cover-content">
            <span class="folio-auto-cover-eyebrow">DATA PORTFOLIO</span>
            <h3>{title}</h3>
            <div class="folio-auto-cover-tags">{tag_html}</div>
        </div>
    </div>
    """)


def render_project_metrics(
    project: dict,
    container_class: str = "folio-home-metrics",
    extra_html: str = "",
    include_likes: bool = True,
) -> str:
    views = project.get("view_count", 0) or 0
    likes = project.get("like_count", 0) or 0
    likes_html = ""
    if include_likes:
        likes_html = f"""
        <span title=\"좋아요\" aria-label=\"좋아요 {likes}\">
            <svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M20.8 4.8a5.5 5.5 0 0 0-7.8 0L12 5.9l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.4a5.5 5.5 0 0 0 0-7.8Z\"></path></svg>
            {likes}
        </span>
        """
    return clean_html(f"""
    <div class="{container_class}">
        <span title="조회수" aria-label="조회수 {views}">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"></path><circle cx="12" cy="12" r="2.7"></circle></svg>
            {views}
        </span>
        {likes_html}
        {extra_html}
    </div>
    """)


def render_project_cover_html(project: dict, compact: bool = False) -> str:
    thumbnail_url = project.get("thumbnail_url")
    if thumbnail_url:
        return clean_html(f"""
        <img
            class="folio-page-hero-cover-image"
            src="{html.escape(thumbnail_url, quote=True)}"
            alt="프로젝트 커버 이미지"
        />
        """)
    return _render_auto_cover(project, compact=compact)


def render_project_card_html(
    project: dict,
    compact: bool = False,
    fallback_text: str = "",
    href: str | None = None,
) -> str:
    one_liner = html.escape(project.get("one_liner") or fallback_text or project.get("insights") or "")
    if not one_liner:
        one_liner = html.escape(project.get("problem") or "")

    author = project.get("author") or {}
    author_name = html.escape(author.get("name") or "작성자")
    cover_html = _render_auto_cover(project, compact=compact)
    metrics_html = render_project_metrics(project)

    card_class = "folio-home-card folio-home-card-compact" if compact else "folio-home-card"
    card_html = f"""
    <div class="{card_class}">
        {cover_html}
        <p class="folio-home-author">{author_name}</p>
        <p>{one_liner}</p>
        {metrics_html}
    </div>
    """
    if not href:
        return clean_html(card_html)

    return clean_html(f"""
    <a class="folio-card-link" href="{html.escape(href, quote=True)}" target="_self">
        {card_html}
    </a>
    """)


def render_portfolio_card_html(project: dict, href: str | None = None) -> str:
    title = html.escape(project.get("title") or "프로젝트명이 여기에 표시됩니다.")
    one_liner = html.escape(project.get("one_liner") or project.get("insights") or project.get("problem") or "")
    author = project.get("author") or {}
    author_name = html.escape(author.get("name") or "작성자")
    tags_html = render_tag_chips(project.get("tags") or [])
    metrics_html = render_project_metrics(project, container_class="folio-portfolio-card-meta")
    visibility_icon = (
        '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"></path></svg>'
        if project.get("is_public")
        else '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2"></rect><path d="M8 10V7a4 4 0 0 1 8 0v3"></path></svg>'
    )
    card_html = f"""
    <div class="folio-home-card folio-home-card-compact">
        <p class="folio-home-author">{author_name}</p>
        <p>{one_liner}</p>
        {tags_html}
        <div class="folio-portfolio-visibility">{visibility_icon}</div>
        {metrics_html}
    </div>
    """
    if not href:
        return clean_html(card_html)
    return clean_html(f"""
    <a class="folio-card-link" href="{html.escape(href, quote=True)}" target="_self">
        {card_html}
    </a>
    """)


def render_gallery_card_html(project: dict, href: str | None = None) -> str:
    author = project.get("author") or {}
    one_liner = html.escape(project.get("one_liner") or project.get("insights") or "")
    if not one_liner:
        one_liner = html.escape(project.get("problem") or "")
    author_name = html.escape(author.get("name") or "작성자")
    cover_html = _render_auto_cover(project)
    metrics_html = render_project_metrics(project, container_class="folio-gallery-footer")

    card_html = f"""
    <div class="folio-gallery-card">
        <div class="folio-thumbnail">
            {cover_html}
        </div>
        <div class="folio-gallery-content">
            <div>
                <p>{one_liner}</p>
                <p class="folio-muted">작성자: {author_name}</p>
            </div>
            <div class="folio-gallery-footer">
                {metrics_html}
            </div>
        </div>
    </div>
    """
    if not href:
        return clean_html(card_html)

    return clean_html(f"""
    <a class="folio-card-link" href="{html.escape(href, quote=True)}" target="_self">
        {card_html}
    </a>
    """)
