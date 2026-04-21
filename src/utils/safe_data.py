from __future__ import annotations

from copy import deepcopy
from typing import Any


def clone_default(value: Any) -> Any:
    return deepcopy(value)


def safe_dict(value: Any, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return dict(default or {})


def safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
