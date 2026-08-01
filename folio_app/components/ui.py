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


def _cover_variant(project: dict, variant_count: int = 24) -> int:
    seed = str(project.get("id") or project.get("title") or "folio")
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % variant_count


def _render_auto_cover(
    project: dict,
    *,
    compact: bool = False,
    show_title: bool = True,
    show_tags: bool = True,
) -> str:
    title = html.escape(project.get("title") or "프로젝트명이 여기에 표시됩니다.")
    tag_html = "".join(
        f"<span>#{html.escape(str(tag))}</span>"
        for tag in (project.get("tags") or [])[:2]
    )
    title_block = f"<h3>{title}</h3>" if show_title else ""
    tags_block = f'<div class="folio-auto-cover-tags">{tag_html}</div>' if show_tags else ""
    compact_class = " folio-auto-cover-compact" if compact else ""
    return clean_html(f"""
    <div class="folio-auto-cover folio-auto-cover-{_cover_variant(project)}{compact_class}">
        <div class="folio-auto-cover-pattern" aria-hidden="true"></div>
        <div class="folio-auto-cover-content">
            <span class="folio-auto-cover-eyebrow">PROJECT PORTFOLIO</span>
            {title_block}
            {tags_block}
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
    preview_url: str | None = None,
) -> str:
    one_liner = html.escape(project.get("one_liner") or fallback_text or project.get("insights") or "")
    if not one_liner:
        one_liner = html.escape(project.get("problem") or "")

    author = project.get("author") or {}
    author_name = html.escape(author.get("name") or "작성자")
    author_organization = html.escape(author.get("organization") or "")
    author_label = f"{author_name} · {author_organization}" if author_organization else author_name
    created_at = project.get("created_at") or ""
    date_label = html.escape(str(created_at)[:10]) if created_at else ""
    footer_meta_html = clean_html(f"""
    <div class="folio-home-footer-meta">
        <span class="folio-home-date">{date_label}</span>
        <span class="folio-home-author">{author_label}</span>
    </div>
    """)
    title_html = html.escape(project.get("title") or "프로젝트명이 여기에 표시됩니다.")
    cover_html = _render_auto_cover(project, compact=compact, show_title=False, show_tags=False)
    metrics_html = render_project_metrics(project)
    tags = [str(tag) for tag in (project.get("tags") or [])]
    visible_tags = tags[:4]
    tag_html = "".join(f"<span>#{html.escape(tag)}</span>" for tag in visible_tags)
    hidden_count = max(len(tags) - len(visible_tags), 0)
    if hidden_count:
        tag_list = ", ".join(tags)
        tag_html += (
            f'<span class="folio-home-card-tag-more" '
            f'title="{html.escape(tag_list, quote=True)}">+{hidden_count}</span>'
        )
    tags_block = f'<div class="folio-home-card-tags">{tag_html}</div>' if tag_html else ""

    # Streamlit's markdown renderer will not let <a> wrap block-level content
    # (e.g. <div>): it silently splits one <a> into several, one per inline
    # text run, leaving the cover/background unclickable. Instead, an empty
    # <a> stretched over the whole card (position: absolute; inset: 0;) makes
    # the entire card clickable while itself containing no block children.
    overlay_link_html = (
        f'<a class="folio-card-link" href="{html.escape(href, quote=True)}" target="_self" '
        f'aria-label="{html.escape(project.get("title") or "프로젝트")}"></a>'
        if href
        else ""
    )
    preview_html = (
        f"""
        <div class="folio-home-card-preview" data-folio-preview-src="{html.escape(preview_url, quote=True)}">
            <div class="folio-home-card-preview-label">대시보드 미리보기</div>
        </div>
        """
        if preview_url
        else ""
    )

    card_class = "folio-home-card folio-home-card-compact" if compact else "folio-home-card"
    if preview_url:
        card_class += " folio-home-card-has-preview"
    card_html = f"""
    <div class="{card_class}">
        {overlay_link_html}
        {cover_html}
        {preview_html}
        <div class="folio-home-card-overlay">
            <div class="folio-home-card-title-zone">
                <h3 class="folio-home-card-title">{title_html}</h3>
            </div>
            <div class="folio-home-card-summary-zone">
                <p class="folio-home-card-summary">{one_liner}</p>
            </div>
            <div class="folio-home-card-tags-zone">
                {tags_block}
            </div>
            <div class="folio-home-footer">
                {footer_meta_html}
                {metrics_html}
            </div>
        </div>
    </div>
    """
    return clean_html(card_html)
