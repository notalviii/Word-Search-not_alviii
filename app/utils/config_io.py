"""Guardado seguro de configuraciones de la aplicación."""

from __future__ import annotations

import json
from pathlib import Path

from app.models import AppConfig


def save_config(config: AppConfig, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_config(path: str | Path) -> AppConfig:
    source = Path(path)
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("La configuración debe estar codificada en UTF-8.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido en la línea {exc.lineno}: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise ValueError("La configuración JSON debe contener un objeto.")
    try:
        return AppConfig.from_dict(raw)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"La configuración contiene valores no válidos: {exc}") from exc
