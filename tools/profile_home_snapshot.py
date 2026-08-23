from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import time
from typing import Any, Callable, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from folio_app.services.project_queries import clear_project_caches, list_home_project_snapshot
import folio_app.services.project_queries as project_queries


PROFILE_TARGETS = (
    "get_supabase_client",
    "_fetch_home_project_snapshot_rpc",
    "_fetch_home_project_rows",
    "_fetch_home_platform_project_rows",
    "_fetch_home_liked_project_ids",
    "_fetch_public_projects_by_ids",
    "_attach_related_data",
    "_fetch_public_profiles",
    "_fetch_like_counts",
    "comment_stats_by_project",
    "home_tag_summary",
    "_fetch_home_tag_summary",
    "_fetch_home_platform_tag_summary",
    "_fetch_public_project_tags",
)


def _size(value: Any) -> int | None:
    if isinstance(value, tuple) and len(value) == 2 and all(isinstance(item, dict) for item in value):
        return sum(len(item) for item in value)
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, (list, tuple, set)):
        return len(value)
    if hasattr(value, "recent_projects"):
        return (
            len(value.recent_projects)
            + len(value.viewed_projects)
            + len(value.liked_projects)
            + len(value.popular_tags)
        )
    return None


@contextmanager
def timed_functions() -> Iterator[list[dict[str, Any]]]:
    timings: list[dict[str, Any]] = []
    originals: dict[str, Callable[..., Any]] = {}

    def wrap(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            started = time.perf_counter()
            ok = False
            try:
                result = func(*args, **kwargs)
                ok = True
                return result
            finally:
                elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
                timings.append(
                    {
                        "name": name,
                        "ms": elapsed_ms,
                        "ok": ok,
                        "args": [repr(arg)[:120] for arg in args],
                        "size": _size(locals().get("result")),
                    }
                )

        return wrapped

    for name in PROFILE_TARGETS:
        if hasattr(project_queries, name):
            originals[name] = getattr(project_queries, name)
            setattr(project_queries, name, wrap(name, originals[name]))

    try:
        yield timings
    finally:
        for name, original in originals.items():
            setattr(project_queries, name, original)


def run_once(label: str, limit: int, tag_limit: int, platform_key: str | None, clear: bool) -> dict[str, Any]:
    if clear:
        clear_project_caches()
    with timed_functions() as timings:
        started = time.perf_counter()
        snapshot = list_home_project_snapshot(limit=limit, tag_limit=tag_limit, platform_key=platform_key)
        total_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "label": label,
        "platform_key": platform_key or "",
        "total_ms": total_ms,
        "counts": {
            "recent": len(snapshot.recent_projects),
            "viewed": len(snapshot.viewed_projects),
            "liked": len(snapshot.liked_projects),
            "popular_tags": len(snapshot.popular_tags),
            "total_projects": snapshot.total_project_count,
        },
        "timings": timings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--tag-limit", type=int, default=40)
    parser.add_argument("--platform-key", default="powerbi")
    parser.add_argument("--warm-runs", type=int, default=1)
    parser.add_argument("--prime-client", action="store_true")
    args = parser.parse_args()

    if args.prime_client:
        started = time.perf_counter()
        project_queries.get_supabase_client()
        print(
            json.dumps(
                {"prime_client_ms": round((time.perf_counter() - started) * 1000, 1)},
                ensure_ascii=False,
            )
        )

    platform_key = args.platform_key.strip() or None
    runs = [run_once("cold", args.limit, args.tag_limit, platform_key, clear=True)]
    for index in range(args.warm_runs):
        runs.append(run_once(f"warm-{index + 1}", args.limit, args.tag_limit, platform_key, clear=False))

    print(json.dumps(runs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
