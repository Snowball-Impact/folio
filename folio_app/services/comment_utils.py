from datetime import datetime, timezone


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_comment_tree(rows: list[dict]) -> list[dict]:
    by_id = {row["id"]: {**row, "children": []} for row in rows}
    roots: list[dict] = []

    for row in rows:
        node = by_id[row["id"]]
        parent_id = row.get("parent_id")
        parent = by_id.get(parent_id) if parent_id else None
        if parent and not parent.get("parent_id") and (parent.get("depth") or 0) == 0:
            parent["children"].append(node)
        elif parent and parent.get("parent_id") in by_id:
            by_id[parent["parent_id"]]["children"].append(node)
        else:
            roots.append(node)

    return roots

