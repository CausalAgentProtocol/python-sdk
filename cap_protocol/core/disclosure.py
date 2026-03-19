from __future__ import annotations

from collections.abc import Collection
from typing import Any


def sanitize_fields(payload: Any, *, forbidden_fields: Collection[str]) -> Any:
    forbidden = set(forbidden_fields)

    if isinstance(payload, dict):
        return {
            key: sanitize_fields(value, forbidden_fields=forbidden)
            for key, value in payload.items()
            if key not in forbidden
        }
    if isinstance(payload, list):
        return [sanitize_fields(item, forbidden_fields=forbidden) for item in payload]
    return payload


__all__ = ["sanitize_fields"]
