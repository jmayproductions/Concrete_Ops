"""Live evidence adapters — hydrate swarm context from ConcreteOps modules.

Used when Copilot Studio / API callers pass live=true or when context includes
adapter hints. Failures are soft: missing modules leave context unchanged.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from shared.config import CURING_THRESHOLDS, THERMAL_LIMITS


def from_curing_telemetry(telemetry: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    """Map curing sensor samples into curing-lifecycle context."""
    samples = telemetry if isinstance(telemetry, list) else [telemetry]
    if not samples:
        return {}
    latest = samples[-1]
    return {
        "curing": {
            "started": True,
            "temperature_f": latest.get("temperature"),
            "moisture": latest.get("moisture_level"),
            "strength_estimate_psi": latest.get("strength_estimate"),
            "humidity": latest.get("humidity"),
            "owner": latest.get("owner", "curing-agent"),
        }
    }


def from_thermal_pair(core_temp_f: float, surface_temp_f: float) -> dict[str, Any]:
    delta = abs(float(core_temp_f) - float(surface_temp_f))
    return {
        "mass": {
            "core_temp_f": core_temp_f,
            "surface_temp_f": surface_temp_f,
            "delta_t_f": delta,
            "max_delta_t_f": THERMAL_LIMITS.get("max_diff", 35.0),
        }
    }


def from_deck_zone(zone: dict[str, Any]) -> dict[str, Any]:
    return {
        "deck": {
            "layout_type": zone.get("layout_type"),
            "supports_verified": bool(zone.get("supports_verified")),
            "pour_status": zone.get("pour_status"),
            "zone_id": zone.get("zone_id") or zone.get("id"),
        }
    }


def from_weather_snapshot(wx: dict[str, Any]) -> dict[str, Any]:
    """Normalize OpenWeather-ish or swarm weather dicts."""
    if not wx:
        return {}
    if "temp_f" in wx or "wind_kph" in wx:
        return {"weather": wx}
    temp_c = wx.get("temp")
    temp_f = (temp_c * 9 / 5 + 32) if isinstance(temp_c, (int, float)) else wx.get("temp_f")
    wind = wx.get("wind_speed")
    # assume m/s if small, else treat as mph
    wind_kph = None
    if isinstance(wind, (int, float)):
        wind_kph = wind * 3.6 if wind < 40 else wind * 1.60934
    return {
        "weather": {
            "temp_f": temp_f,
            "wind_kph": wind_kph or wx.get("wind_kph", 0),
            "rain_mm": wx.get("rain_mm", 0),
            "conditions": wx.get("conditions"),
        }
    }


def enrich_context(context: dict[str, Any]) -> dict[str, Any]:
    """Merge adapter payloads declared under context['live_evidence']."""
    ctx = deepcopy(context)
    evidence = ctx.pop("live_evidence", {}) or {}

    if "curing_telemetry" in evidence:
        _deep_merge(ctx, from_curing_telemetry(evidence["curing_telemetry"]))
    if "thermal" in evidence:
        t = evidence["thermal"]
        if "core_temp_f" in t and "surface_temp_f" in t:
            _deep_merge(ctx, from_thermal_pair(t["core_temp_f"], t["surface_temp_f"]))
    if "deck_zone" in evidence:
        _deep_merge(ctx, from_deck_zone(evidence["deck_zone"]))
    if "weather" in evidence:
        _deep_merge(ctx, from_weather_snapshot(evidence["weather"]))

    # Soft defaults from shared thresholds for curing band checks
    curing = ctx.setdefault("curing", {})
    curing.setdefault("min_temp_f", CURING_THRESHOLDS.get("min_temp"))
    curing.setdefault("max_temp_f", CURING_THRESHOLDS.get("max_temp"))
    curing.setdefault("min_moisture", CURING_THRESHOLDS.get("min_moisture"))
    return ctx


def _deep_merge(dst: dict[str, Any], src: dict[str, Any]) -> None:
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _deep_merge(dst[key], value)
        else:
            dst[key] = value
