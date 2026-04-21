from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from src.utils.safe_data import clone_default


class JSONStore:
    """通用 JSON 文件安全读写工具。"""

    def __init__(
        self,
        file_path: str | Path,
        default_data: dict[str, Any],
        validator: Callable[[Any], bool] | None = None,
    ) -> None:
        self.file_path = Path(file_path)
        self.default_data = clone_default(default_data)
        self.validator = validator
        self.ensure_exists()

    def ensure_exists(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.write(clone_default(self.default_data))

    def read(self) -> dict[str, Any]:
        self.ensure_exists()
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                content = file.read().strip()
        except (OSError, UnicodeDecodeError):
            return self._reset_to_default()

        if not content:
            return self._reset_to_default()

        try:
            data = json.loads(content)
        except (json.JSONDecodeError, TypeError, ValueError):
            return self._reset_to_default()

        if not self._is_valid(data):
            return self._reset_to_default()
        return data

    def write(self, data: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.file_path.with_suffix(f"{self.file_path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temp_path.replace(self.file_path)

    def _reset_to_default(self) -> dict[str, Any]:
        default_copy = clone_default(self.default_data)
        self.write(default_copy)
        return default_copy

    def _is_valid(self, data: Any) -> bool:
        if not isinstance(data, dict):
            return False
        if self.validator is None:
            return True
        try:
            return bool(self.validator(data))
        except Exception:
            return False
