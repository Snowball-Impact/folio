import html
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


def render_project_card_html(
    project: dict,
    compact: bool = False,
    fallback_text: str = "",
    href: str | None = None,
) -> str:
    title = html.escape(project.get("title") or "Untitled")
    one_liner = html.escape(project.get("one_liner") or fallback_text or project.get("insights") or "")
    if not one_liner:
        one_liner = html.escape(project.get("problem") or "")

    tags = render_tag_chips((project.get("tags") or [])[:2] if compact else (project.get("tags") or []))
    thumbnail_html = ""
    if not compact:
        thumbnail_url = project.get("thumbnail_url")
        if is_http_url(thumbnail_url):
            thumbnail_html = f"<img class='folio-home-thumb' src='{html.escape(thumbnail_url, quote=True)}' alt=''>"
        else:
            thumbnail_html = "<div class='folio-home-thumb folio-home-thumb-fallback'>FOLIO</div>"

    card_class = "folio-home-card folio-home-card-compact" if compact else "folio-home-card"
    card_html = f"""
    <div class="{card_class}">
        {thumbnail_html}
        <h3>{title}</h3>
        <p>{one_liner}</p>
        {tags}
        <div class="folio-home-metrics">조회 {project.get('view_count', 0)} · 좋아요 {project.get('like_count', 0)}</div>
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
    thumbnail_url = project.get("thumbnail_url")
    title = html.escape(project.get("title") or "Untitled")
    one_liner = html.escape(project.get("one_liner") or project.get("insights") or "")
    if not one_liner:
        one_liner = html.escape(project.get("problem") or "")
    author_name = html.escape(author.get("name") or "작성자")
    tags_html = render_tag_chips(project.get("tags") or [])

    image_html = (
        f'<img src="{html.escape(thumbnail_url, quote=True)}" class="folio-home-thumb" />'
        if is_http_url(thumbnail_url)
        else "FOLIO"
    )

    card_html = f"""
    <div class="folio-gallery-card">
        <div class="folio-thumbnail">
            {image_html}
        </div>
        <div class="folio-gallery-content">
            <div>
                <h3>{title}</h3>
                <p>{one_liner}</p>
                <p class="folio-muted">작성자: {author_name}</p>
            </div>
            <div class="folio-gallery-footer">
                {tags_html}
                <div class="folio-detail-meta">조회 {project.get('view_count', 0)} · 좋아요 {project.get('like_count', 0)}</div>
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
