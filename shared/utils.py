# shared/utils.py

"""Shared logging and alert helpers used across ConcreteOps modules."""

from __future__ import annotations

from datetime import datetime
from typing import Any


_EVENT_LOG: list[dict[str, Any]] = []
_ALERT_LOG: list[dict[str, Any]] = []


def log_event(message: str) -> None:
    entry = {"timestamp": datetime.now().isoformat(), "message": message}
    _EVENT_LOG.append(entry)
    print(f"[event] {message}")


def trigger_alert(message: str) -> None:
    entry = {"timestamp": datetime.now().isoformat(), "alert": message}
    _ALERT_LOG.append(entry)
    print(f"[alert] {message}")


def get_events() -> list[dict[str, Any]]:
    return list(_EVENT_LOG)


def get_alerts() -> list[dict[str, Any]]:
    return list(_ALERT_LOG)


def clear_logs() -> None:
    _EVENT_LOG.clear()
    _ALERT_LOG.clear()
