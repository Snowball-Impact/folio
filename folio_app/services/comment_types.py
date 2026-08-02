from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CommentResult:
    ok: bool
    message: str
    comment: dict[str, Any] | None = None
    comment_id: str | None = None

