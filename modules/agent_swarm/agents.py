"""Specialist agent evaluators for the ConcreteOps crew swarm.

These are deterministic gate keepers that encode the same playbooks as the
Docker Agent specialists under agents/concrete-crew/. They consume pour
context dicts so workflows stay repeatable in CI and field sim mode.
"""

from __future__ import annotations

from typing import Any

from modules.agent_swarm.schemas import GateResult
from shared.config import (
    FAILSAFE_RULES,
    MIX_REQUIREMENTS,
    SLUMP_RANGE,
    TEMPERATURE_THRESHOLDS,
)


REQUIRED_CREW_ROLES = (
    "pour_lead",
    "pump_operator",
    "vibrator",
    "finisher",
    "qc_tech",
    "safety_watch",
)


def _num(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class MaterialsMixAgent:
    name = "materials-mix"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        mix = ctx.get("mix") or {}
        missing = [k for k in ("psi", "w_c_ratio", "slump", "air_content") if k not in mix]
        if missing:
            return GateResult(
                self.name,
                "HOLD",
                f"Missing mix fields: {', '.join(missing)}",
                {"missing": missing},
            )

        failures: list[str] = []
        psi = _num(mix["psi"])
        w_c = _num(mix["w_c_ratio"])
        slump = _num(mix["slump"])
        air = _num(mix["air_content"])

        if psi is None or psi < MIX_REQUIREMENTS["min_psi"]:
            failures.append(f"psi {psi} < {MIX_REQUIREMENTS['min_psi']}")
        if w_c is None or w_c > MIX_REQUIREMENTS["max_w_c_ratio"]:
            failures.append(f"w/c {w_c} > {MIX_REQUIREMENTS['max_w_c_ratio']}")
        lo, hi = MIX_REQUIREMENTS["slump_range"]
        if slump is None or not (lo <= slump <= hi):
            failures.append(f"slump {slump} outside {lo}-{hi}")
        alo, ahi = MIX_REQUIREMENTS["air_content_range"]
        if air is None or not (alo <= air <= ahi):
            failures.append(f"air {air}% outside {alo}-{ahi}")

        if failures:
            return GateResult(self.name, "FAIL", "; ".join(failures), {"mix": mix})

        ticket = mix.get("ticket_id", "unspecified")
        return GateResult(
            self.name,
            "PASS",
            f"Mix ACCEPT ticket={ticket} psi={psi}",
            {"mix": mix},
        )


class WeatherGateAgent:
    name = "weather-gate"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        wx = ctx.get("weather") or {}
        if not wx:
            return GateResult(self.name, "HOLD", "No weather data for pour window", {})

        rain = _num(wx.get("rain_mm"), 0.0) or 0.0
        wind = _num(wx.get("wind_kph"), 0.0) or 0.0
        temp_f = _num(wx.get("temp_f"))
        thresholds = ctx.get("weather_thresholds") or {
            "rain_mm": 2.5,
            "wind_kph": 40.0,
            "freeze_f": 35.0,
            "heat_f": 90.0,
        }

        holds: list[str] = []
        advisories: list[str] = []

        if rain >= thresholds["rain_mm"]:
            holds.append(f"rain {rain}mm ≥ {thresholds['rain_mm']}mm")
        if wind >= thresholds["wind_kph"]:
            holds.append(f"wind {wind}kph ≥ {thresholds['wind_kph']}kph")
        if temp_f is not None and temp_f <= thresholds["freeze_f"]:
            holds.append(f"cold {temp_f}°F — cold-weather protocol / HOLD")
        elif temp_f is not None and temp_f >= thresholds["heat_f"]:
            advisories.append(f"heat {temp_f}°F — hot-weather protocol")

        evidence = {"weather": wx, "thresholds": thresholds}
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), evidence)
        if advisories:
            return GateResult(self.name, "ADVISORY", "; ".join(advisories), evidence)
        return GateResult(
            self.name,
            "PASS",
            f"CLEAR temp={temp_f}°F wind={wind}kph rain={rain}mm",
            evidence,
        )


class QCInspectorAgent:
    name = "qc-inspector"

    def evaluate(self, ctx: dict[str, Any], phase: str = "pre") -> GateResult:
        checks = list(ctx.get("qc_checks") or [])
        phase_checks = [c for c in checks if c.get("phase", "pre") == phase]

        if not phase_checks:
            # Synthesize from telemetry / readiness when explicit checklist absent
            telemetry = ctx.get("telemetry") or {}
            if phase == "pre":
                required = ["forms_ready", "rebar_ready", "cylinders_ready"]
                missing = [k for k in required if not ctx.get("readiness", {}).get(k)]
                if missing:
                    return GateResult(
                        self.name,
                        "HOLD",
                        f"Pre-pour readiness missing: {', '.join(missing)}",
                        {"missing": missing},
                    )
                return GateResult(self.name, "PASS", "Pre-pour QC readiness clear", {})

            if phase == "post":
                curing = ctx.get("curing") or {}
                finish_ok = bool(ctx.get("finish_accepted", curing.get("finish_accepted")))
                curing_started = bool(curing.get("started"))
                if not finish_ok or not curing_started:
                    missing = []
                    if not finish_ok:
                        missing.append("finish_accepted")
                    if not curing_started:
                        missing.append("curing.started")
                    return GateResult(
                        self.name,
                        "HOLD",
                        f"Post-pour QC incomplete: {', '.join(missing)}",
                        {"missing": missing},
                    )
                return GateResult(
                    self.name,
                    "PASS",
                    f"Post-pour QC accepted; curing owner={curing.get('owner', 'unassigned')}",
                    {"curing": curing},
                )

            slump = _num(telemetry.get("slump"))
            temp = _num(telemetry.get("temperature"))
            issues: list[str] = []
            if slump is None or not (SLUMP_RANGE["min"] <= slump <= SLUMP_RANGE["max"]):
                issues.append(f"slump {slump} outside {SLUMP_RANGE['min']}-{SLUMP_RANGE['max']}")
            if temp is None or temp > TEMPERATURE_THRESHOLDS["max_concrete_temp"]:
                issues.append(
                    f"concrete temp {temp} > {TEMPERATURE_THRESHOLDS['max_concrete_temp']}"
                )
            if issues:
                return GateResult(self.name, "FAIL", "; ".join(issues), {"telemetry": telemetry})
            return GateResult(
                self.name,
                "PASS",
                f"{phase} QC clear slump={slump} temp={temp}",
                {"telemetry": telemetry},
            )

        failed = [c for c in phase_checks if not c.get("passed")]
        passed = len(phase_checks) - len(failed)
        if failed:
            detail = "; ".join(c.get("description", "check") for c in failed)
            return GateResult(
                self.name,
                "FAIL",
                f"{phase} QC {passed}/{len(phase_checks)} — failed: {detail}",
                {"failed": failed},
            )
        return GateResult(
            self.name,
            "PASS",
            f"{phase} QC {passed}/{len(phase_checks)} passed",
            {"passed": passed, "total": len(phase_checks)},
        )


class CrewOpsAgent:
    name = "crew-ops"

    def evaluate(self, ctx: dict[str, Any], require_briefing: bool = True) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        missing_roles = [r for r in REQUIRED_CREW_ROLES if r not in roles]
        headcount = int(crew.get("headcount") or len(roles))
        fatigued = list(crew.get("fatigued_workers") or [])
        briefing_complete = bool(crew.get("briefing_complete", False))

        if missing_roles:
            return GateResult(
                self.name,
                "HOLD",
                f"Missing roles: {', '.join(missing_roles)}",
                {"missing_roles": missing_roles},
            )
        if fatigued:
            return GateResult(
                self.name,
                "HOLD",
                f"Fatigue risk: {', '.join(fatigued)}",
                {"fatigued": fatigued},
            )
        if require_briefing and not briefing_complete:
            return GateResult(
                self.name,
                "HOLD",
                "Crew briefing incomplete",
                {"briefing_complete": False},
            )
        return GateResult(
            self.name,
            "PASS",
            f"Crew ready headcount={headcount} briefing={'yes' if briefing_complete else 'n/a'}",
            {"headcount": headcount, "roles": sorted(roles)},
        )

    def run_briefing(self, ctx: dict[str, Any]) -> GateResult:
        script = [
            "pour_identity",
            "mix_method",
            "qc_hold_points",
            "weather_protocol",
            "stop_work_radio",
            "breaks_hydration",
        ]
        covered = set((ctx.get("crew") or {}).get("briefing_items") or [])
        missing = [item for item in script if item not in covered]
        if missing:
            return GateResult(
                self.name,
                "HOLD",
                f"BRIEFING INCOMPLETE — missing {', '.join(missing)}",
                {"missing": missing},
            )
        return GateResult(
            self.name,
            "PASS",
            "BRIEFING COMPLETE — all six script items covered",
            {"covered": script},
        )


class SafetyFailsafeAgent:
    name = "safety-failsafe"

    def evaluate(self, ctx: dict[str, Any]) -> GateResult:
        telemetry = dict(ctx.get("telemetry") or {})
        site = dict(ctx.get("site_conditions") or {})
        # Allow weather wind to feed fail-safe when site wind omitted
        if "wind_speed" not in site and "wind_mph" in (ctx.get("weather") or {}):
            site["wind_speed"] = ctx["weather"]["wind_mph"]
        if "wind_speed" not in site and "wind_kph" in (ctx.get("weather") or {}):
            site["wind_speed"] = (ctx["weather"]["wind_kph"] or 0) * 0.621371

        violations: list[dict[str, Any]] = []
        for rule in FAILSAFE_RULES:
            metric = rule["metric"]
            source = telemetry if metric in telemetry else site
            if metric not in source:
                continue
            value = _num(source[metric])
            if value is None:
                continue
            threshold = rule["threshold"]
            comparator = rule["comparator"]
            ok = {
                ">": value > threshold,
                ">=": value >= threshold,
                "<": value < threshold,
                "<=": value <= threshold,
                "==": value == threshold,
            }.get(comparator, False)
            # Rule fires when comparison against safe envelope fails.
            # FAILSAFE_RULES encode "unsafe when metric comparator threshold"
            # e.g. slump > 6.0 is a violation.
            if ok:
                violations.append(
                    {
                        "metric": metric,
                        "value": value,
                        "comparator": comparator,
                        "threshold": threshold,
                    }
                )

        critical_missing = []
        for metric in ("slump", "temperature"):
            if metric not in telemetry and ctx.get("require_telemetry"):
                critical_missing.append(metric)
        if critical_missing:
            return GateResult(
                self.name,
                "HOLD",
                f"Missing critical telemetry: {', '.join(critical_missing)}",
                {"missing": critical_missing},
            )

        if violations:
            detail = "; ".join(
                f"{v['metric']}={v['value']} ({v['comparator']} {v['threshold']})"
                for v in violations
            )
            return GateResult(self.name, "FAIL", f"STOP-WORK: {detail}", {"violations": violations})

        return GateResult(self.name, "PASS", "No fail-safe violations", {"violations": []})


class PourLeadAgent:
    name = "pour-lead"

    def assemble(
        self,
        ctx: dict[str, Any],
        gates: list[GateResult],
        workflow: str,
    ) -> GateResult:
        statuses = {g.status for g in gates}
        if "FAIL" in statuses and any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in gates):
            decision_hint = "ABORT"
            detail = "Fail-safe blocked pour — assemble abort package"
        elif "FAIL" in statuses or "HOLD" in statuses:
            decision_hint = "HOLD"
            blockers = [g.agent for g in gates if g.status in ("FAIL", "HOLD")]
            detail = f"Blocked by: {', '.join(blockers)}"
        else:
            decision_hint = "GO"
            detail = f"Placement plan ready for {ctx.get('pour_id', 'unknown')}"

        return GateResult(
            self.name,
            "PASS" if decision_hint == "GO" else ("FAIL" if decision_hint == "ABORT" else "HOLD"),
            f"{detail} [{decision_hint}]",
            {
                "decision_hint": decision_hint,
                "volume_cy": ctx.get("volume_cy"),
                "area": ctx.get("area"),
                "workflow": workflow,
            },
        )
