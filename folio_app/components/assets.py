"""Helpers for serving packaged static assets inside Streamlit markup."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path


_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


@lru_cache(maxsize=32)
def static_image_src(image_name: str) -> str:
    image_path = _STATIC_DIR / image_name
    mime_type = _MIME_TYPES.get(image_path.suffix.lower(), "application/octet-stream")
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
