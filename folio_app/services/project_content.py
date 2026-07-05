from __future__ import annotations

import html
from html.parser import HTMLParser
from urllib.parse import urlparse


ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "em",
    "h2",
    "h3",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "u",
    "ul",
}
VOID_TAGS = {"br"}
DROP_WITH_CONTENT_TAGS = {"iframe", "script", "style"}


def sanitize_project_html(value: str | None) -> str:
    """Keep the small HTML subset used by the project editor and escape everything else."""
    if not value:
        return ""

    parser = _ProjectHTMLSanitizer()
    parser.feed(value)
    parser.close()
    return "".join(parser.output).strip()


class _ProjectHTMLSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.output: list[str] = []
        self._dropped_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in DROP_WITH_CONTENT_TAGS:
            self._dropped_depth += 1
            return
        if self._dropped_depth or tag not in ALLOWED_TAGS:
            return

        if tag == "a":
            href = next((value for name, value in attrs if name.lower() == "href"), None)
            if _is_safe_link(href):
                safe_href = html.escape(href or "", quote=True)
                self.output.append(f'<a href="{safe_href}" target="_blank" rel="noopener noreferrer">')
                return
        self.output.append(f"<{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in DROP_WITH_CONTENT_TAGS:
            return
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in DROP_WITH_CONTENT_TAGS:
            self._dropped_depth = max(0, self._dropped_depth - 1)
            return
        if self._dropped_depth or tag not in ALLOWED_TAGS or tag in VOID_TAGS:
            return
        self.output.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._dropped_depth:
            self.output.append(html.escape(data))


def _is_safe_link(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
