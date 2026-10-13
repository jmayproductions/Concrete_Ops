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
    STRENGTH_THRESHOLD_PSI,
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

PT_CREW_ROLES = (
    "pt_lead",
    "jack_operator",
    "qc_tech",
    "safety_watch",
)

TILT_CREW_ROLES = (
    "tilt_lead",
    "crane_operator",
    "rigger",
    "brace_crew",
    "qc_tech",
    "safety_watch",
)

DEFAULT_ELONGATION_TOLERANCE = 0.07  # ±7%
DEFAULT_TILT_WIND_HOLD_KPH = 40.0
DEFAULT_PT_SPACING_MAX_IN = 48.0


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

    def evaluate(
        self,
        ctx: dict[str, Any],
        require_briefing: bool = True,
        required_roles: tuple[str, ...] | None = None,
    ) -> GateResult:
        crew = ctx.get("crew") or {}
        roles = set(crew.get("roles") or [])
        expected = required_roles or tuple(crew.get("required_roles") or REQUIRED_CREW_ROLES)
        missing_roles = [r for r in expected if r not in roles]
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
        job = ctx.get("pour_id") or ctx.get("deck_id") or ctx.get("panel_id") or "unknown"
        if "FAIL" in statuses and any(g.agent == "safety-failsafe" and g.status == "FAIL" for g in gates):
            decision_hint = "ABORT"
            detail = f"Fail-safe blocked work — assemble abort package for {job}"
        elif "FAIL" in statuses or "HOLD" in statuses:
            decision_hint = "HOLD"
            blockers = [g.agent for g in gates if g.status in ("FAIL", "HOLD")]
            detail = f"Blocked by: {', '.join(blockers)}"
        else:
            decision_hint = "GO"
            detail = f"Plan ready for {job}"

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


class PTStressAgent:
    name = "pt-stress"

    def pre_stress_gate(self, ctx: dict[str, Any]) -> GateResult:
        pt = ctx.get("pt") or {}
        strength = _num(pt.get("concrete_strength_psi"))
        min_strength = _num(pt.get("min_stress_psi"), float(STRENGTH_THRESHOLD_PSI)) or float(
            STRENGTH_THRESHOLD_PSI
        )
        cables = list(pt.get("cables") or [])
        sequence = list(pt.get("sequence") or [])
        issues: list[str] = []

        if strength is None:
            return GateResult(self.name, "HOLD", "Missing concrete strength for stress gate", {})
        if strength < min_strength:
            issues.append(f"strength {strength} psi < {min_strength} psi")

        if not cables:
            return GateResult(self.name, "HOLD", "No PT cables registered for deck", {})

        over_spaced: list[str] = []
        for c in cables:
            spacing = _num(c.get("spacing_in"))
            if (
                spacing is not None
                and spacing > DEFAULT_PT_SPACING_MAX_IN
                and not c.get("engineered_spacing")
            ):
                over_spaced.append(str(c.get("id") or c.get("tag") or "?"))
        if over_spaced:
            issues.append(f"over-spaced tendons: {', '.join(over_spaced)}")

        if not sequence:
            issues.append("stressing sequence not published")
        else:
            cable_ids = {c.get("id") or c.get("tag") for c in cables}
            missing_in_seq = [cid for cid in cable_ids if cid not in sequence]
            if missing_in_seq:
                issues.append(
                    f"sequence missing cables: {', '.join(str(x) for x in missing_in_seq)}"
                )

        if not pt.get("gauge_calibrated"):
            issues.append("gauge calibration not current")
        if not pt.get("exclusion_zone_set"):
            issues.append("exclusion zone not set")

        if issues:
            status = "FAIL" if over_spaced else "HOLD"
            return GateResult(self.name, status, "; ".join(issues), {"pt": pt})

        return GateResult(
            self.name,
            "PASS",
            f"Pre-stress clear strength={strength} psi cables={len(cables)}",
            {"strength_psi": strength, "cable_count": len(cables)},
        )

    def stress_sequence(self, ctx: dict[str, Any]) -> GateResult:
        pt = ctx.get("pt") or {}
        cables = list(pt.get("cables") or [])
        sequence = list(pt.get("sequence") or [])
        tolerance = _num(pt.get("elongation_tolerance"), DEFAULT_ELONGATION_TOLERANCE) or DEFAULT_ELONGATION_TOLERANCE
        if not cables:
            return GateResult(self.name, "HOLD", "No cables to stress", {})

        abort_reasons: list[str] = []
        hold_reasons: list[str] = []
        stressed = 0

        by_id = {(c.get("id") or c.get("tag")): c for c in cables}
        if sequence:
            ordered = [by_id[i] for i in sequence if i in by_id]
            # Out-of-order: stressed cables that appear before an unstressed earlier sequence item
            for idx, cable_id in enumerate(sequence):
                cable = by_id.get(cable_id)
                if not cable:
                    hold_reasons.append(f"sequence id missing from inventory: {cable_id}")
                    continue
                if cable.get("broken_strand") or cable.get("anchorage_failure"):
                    abort_reasons.append(f"{cable_id}: strand/anchorage failure")
                log = cable.get("stress") or {}
                if not log:
                    # later cables already stressed while this one empty => out of order
                    later_stressed = any(
                        (by_id.get(sequence[j]) or {}).get("stress") for j in range(idx + 1, len(sequence))
                    )
                    if later_stressed:
                        hold_reasons.append(f"out-of-order: {cable_id} not stressed before later tendons")
                    continue
                stressed += 1
                planned = _num(log.get("planned_psi") or cable.get("planned_stress_psi"))
                actual = _num(log.get("actual_psi"))
                planned_elong = _num(log.get("planned_elongation"))
                actual_elong = _num(log.get("actual_elongation"))
                if planned is not None and actual is not None and planned > 0:
                    if abs(actual - planned) / planned > tolerance:
                        hold_reasons.append(
                            f"{cable_id}: psi {actual} outside ±{tolerance:.0%} of {planned}"
                        )
                if planned_elong is not None and actual_elong is not None and planned_elong > 0:
                    if abs(actual_elong - planned_elong) / planned_elong > tolerance:
                        hold_reasons.append(
                            f"{cable_id}: elongation {actual_elong} outside ±{tolerance:.0%} of {planned_elong}"
                        )
                if log and not cable.get("inspected"):
                    hold_reasons.append(f"{cable_id}: stressed but not inspected")
                if cable.get("inspected") and not cable.get("certified"):
                    hold_reasons.append(f"{cable_id}: inspected but not certified")
        else:
            hold_reasons.append("stressing sequence not published")
            for cable in cables:
                if cable.get("broken_strand") or cable.get("anchorage_failure"):
                    abort_reasons.append(f"{cable.get('id')}: strand/anchorage failure")

        if abort_reasons:
            return GateResult(
                self.name,
                "FAIL",
                f"ABORT stressing — {'; '.join(abort_reasons)}",
                {"abort": abort_reasons},
            )
        if hold_reasons:
            return GateResult(self.name, "HOLD", "; ".join(hold_reasons), {"holds": hold_reasons})
        return GateResult(
            self.name,
            "PASS",
            f"Stress sequence clear — {stressed}/{len(cables)} tendons logged",
            {"stressed": stressed, "total": len(cables)},
        )


class TiltUpAgent:
    name = "tilt-up"

    def cast_gate(self, ctx: dict[str, Any]) -> GateResult:
        tilt = ctx.get("tilt") or {}
        panels = list(tilt.get("panels") or [])
        if not panels:
            return GateResult(self.name, "HOLD", "No tilt panels listed for cast gate", {})

        failures: list[str] = []
        holds: list[str] = []
        for panel in panels:
            pid = panel.get("id") or "?"
            for field in ("embeds_complete", "weld_plates_complete"):
                if panel.get(field) is False:
                    failures.append(f"{pid}: {field} missing")
                elif field not in panel:
                    holds.append(f"{pid}: {field} not verified")
            for field in ("forms_ready", "bond_breaker_applied", "reveals_set", "panel_id_marked"):
                if panel.get(field) is False:
                    holds.append(f"{pid}: {field} incomplete")
                elif field not in panel:
                    holds.append(f"{pid}: {field} not verified")

        if failures:
            return GateResult(self.name, "FAIL", "; ".join(failures), {"panels": panels})
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"panels": panels})
        return GateResult(
            self.name,
            "PASS",
            f"Cast gate clear for {len(panels)} panel(s)",
            {"panel_ids": [p.get("id") for p in panels]},
        )

    def lift_day(self, ctx: dict[str, Any]) -> GateResult:
        tilt = ctx.get("tilt") or {}
        panels = list(tilt.get("panels") or [])
        wind_limit = _num(tilt.get("wind_hold_kph"), DEFAULT_TILT_WIND_HOLD_KPH) or DEFAULT_TILT_WIND_HOLD_KPH
        wind = _num((ctx.get("weather") or {}).get("wind_kph"))
        issues: list[str] = []

        if not panels:
            return GateResult(self.name, "HOLD", "No panels scheduled for lift", {})
        if not tilt.get("crane_chart_ok"):
            issues.append("crane chart not accepted")
        if not tilt.get("exclusion_zone_set"):
            issues.append("exclusion zone not set")
        if wind is not None and wind >= wind_limit:
            issues.append(f"wind {wind}kph ≥ tilt hold {wind_limit}kph")

        for panel in panels:
            pid = panel.get("id") or "?"
            strength = _num(panel.get("strength_psi"))
            min_lift = _num(panel.get("min_lift_psi"), float(STRENGTH_THRESHOLD_PSI)) or float(
                STRENGTH_THRESHOLD_PSI
            )
            if strength is None or strength < min_lift:
                issues.append(f"{pid}: strength {strength} < {min_lift} psi")
            if not panel.get("pick_points_verified"):
                issues.append(f"{pid}: pick points not verified")
            if not panel.get("braces_staged"):
                issues.append(f"{pid}: braces not staged")
            if panel.get("lifted") and not panel.get("braces_secured"):
                issues.append(f"{pid}: lifted without braces secured — do not release crane")

        lift_order = list(tilt.get("lift_order") or [])
        if lift_order:
            ids = [p.get("id") for p in panels]
            if sorted(lift_order) != sorted(x for x in ids if x):
                issues.append("lift order does not match panel list")

        if issues:
            status = "HOLD"
            if any("braces secured" in i for i in issues):
                status = "FAIL"
            return GateResult(self.name, status, "; ".join(issues), {"tilt": tilt, "wind_kph": wind})

        return GateResult(
            self.name,
            "PASS",
            f"Lift day clear — {len(panels)} panel(s), wind={wind}kph",
            {"panels": [p.get("id") for p in panels], "lift_order": lift_order},
        )

    def brace_release(self, ctx: dict[str, Any]) -> GateResult:
        tilt = ctx.get("tilt") or {}
        panels = list(tilt.get("panels") or [])
        if not panels:
            return GateResult(self.name, "HOLD", "No panels for brace release", {})

        holds: list[str] = []
        aborts: list[str] = []
        for panel in panels:
            pid = panel.get("id") or "?"
            if panel.get("instability"):
                aborts.append(f"{pid}: instability flagged")
            if not panel.get("permanent_connections_complete"):
                holds.append(f"{pid}: permanent connections incomplete")
            if not panel.get("connection_inspection_accepted"):
                holds.append(f"{pid}: connection inspection not accepted")

        if aborts:
            return GateResult(self.name, "FAIL", "; ".join(aborts), {"panels": panels})
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"panels": panels})
        return GateResult(
            self.name,
            "PASS",
            f"Brace release clear for {len(panels)} panel(s)",
            {"panel_ids": [p.get("id") for p in panels]},
        )
