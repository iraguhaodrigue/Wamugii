"""
Shared handling for the columns that store a list of strings as JSON Text.

`ServiceQuestion.options` and `Service.features` are both Text rather than a
JSON column, so the same migration runs on SQLite and PostgreSQL. The API,
though, takes and returns a real list -- handing a JSON string to the frontend
and making it parse would be a worse contract for no gain.

`parse_json_list` is a `mode="before"` validator helper, so one function covers
both directions: inbound (a real list from the request body) passes straight
through, outbound (the stored string from the ORM row) gets decoded.
`dump_json_list` is the matching encoder the CRUD layer writes with.
"""

import json
from typing import Any


def parse_json_list(value: Any) -> Any:
    """
    Normalize to `list[str] | None`, whichever direction the value came from.

    Deliberately forgiving on the read side: a row that was hand-edited into
    something that isn't a JSON array should degrade to a single-item list
    rather than 500 a public page. Writes are strict -- the schemas below reject
    anything that isn't a list of strings before it reaches the database.
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        if isinstance(decoded, list):
            return [str(item) for item in decoded]
        return [str(decoded)]
    return value


def dump_json_list(value: list[str] | None) -> str | None:
    """The stored form. An empty list is stored as NULL, not as `[]` or `null`."""
    if not value:
        return None
    items = [str(item).strip() for item in value if str(item).strip()]
    if not items:
        return None
    return json.dumps(items)
