"""Specialist agent evaluators for the ConcreteOps crew swarm.

These are deterministic gate keepers that encode the same playbooks as the
Docker Agent specialists under agents/concrete-crew/. They consume pour
context dicts so workflows stay repeatable in CI and field sim mode.
"""

from __future__ import annotations

from typing import Any

from modules.agent_swarm.schemas import GateResult
from shared.config import (
    CIP_WALL_LIMITS,
    CURING_LIFECYCLE,
    ELEVATED_DECK_LIMITS,
    FAILSAFE_RULES,
    GEO_RISK_THRESHOLDS,
    MASS_POUR_LIMITS,
    MIX_REQUIREMENTS,
    SHOTCRETE_LIMITS,
    SLAB_TOLERANCES,
    SLUMP_RANGE,
    STRENGTH_THRESHOLD_PSI,
    TEMPERATURE_THRESHOLDS,
    THERMAL_LIMITS,
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

SOG_CREW_ROLES = (
    "pour_lead",
    "screed_operator",
    "finisher",
    "qc_tech",
    "safety_watch",
)

SHOTCRETE_CREW_ROLES = (
    "nozzleman",
    "blowpipe",
    "pump_operator",
    "qc_tech",
    "safety_watch",
)

CIP_WALL_CREW_ROLES = (
    "wall_lead",
    "pump_operator",
    "vibrator",
    "form_watch",
    "qc_tech",
    "safety_watch",
)

DECK_CREW_ROLES = (
    "pour_lead",
    "pump_operator",
    "deck_hand",
    "qc_tech",
    "safety_watch",
)

STRIP_CREW_ROLES = (
    "strip_lead",
    "carpenter",
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


class SOGAgent:
    name = "sog"

    def pre_pour_gate(self, ctx: dict[str, Any]) -> GateResult:
        sog = ctx.get("sog") or {}
        geo = sog.get("subgrade") or ctx.get("subgrade") or {}
        issues: list[str] = []

        bearing = _num(geo.get("bearing_capacity_ksf"))
        gw = _num(geo.get("groundwater_depth_ft"))
        slope = _num(geo.get("slope_percent"))
        if bearing is None or bearing < GEO_RISK_THRESHOLDS["min_bearing_capacity_ksf"]:
            issues.append(
                f"bearing {bearing} < {GEO_RISK_THRESHOLDS['min_bearing_capacity_ksf']} ksf"
            )
        if gw is None or gw < GEO_RISK_THRESHOLDS["min_groundwater_depth_ft"]:
            issues.append(
                f"groundwater {gw} < {GEO_RISK_THRESHOLDS['min_groundwater_depth_ft']} ft"
            )
        if slope is not None and slope > GEO_RISK_THRESHOLDS["max_slope_percent"]:
            issues.append(f"slope {slope}% > {GEO_RISK_THRESHOLDS['max_slope_percent']}%")
        if not sog.get("proof_roll_accepted", geo.get("proof_roll_accepted")):
            issues.append("proof-roll not accepted")

        for field, label in (
            ("vapor_barrier_continuous", "vapor barrier continuous"),
            ("joints_set", "isolation/control joints set"),
            ("dowels_set", "dowels set"),
            ("reinforcement_ready", "reinforcement/fiber ready"),
            ("edge_forms_ready", "edge forms ready"),
        ):
            if not sog.get(field):
                issues.append(f"{label} incomplete")

        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"sog": sog, "subgrade": geo})
        return GateResult(self.name, "PASS", "SOG pre-pour subgrade/barrier/forms clear", {"sog": sog})

    def finish_fffl(self, ctx: dict[str, Any]) -> GateResult:
        sog = ctx.get("sog") or {}
        finish = sog.get("finish") or {}
        if not finish and not sog.get("pour_completed", ctx.get("pour_completed")):
            return GateResult(self.name, "HOLD", "SOG pour not completed / no finish data", {})

        issues: list[str] = []
        max_var = _num(finish.get("max_variation_in"))
        ff = _num(finish.get("ff"))
        fl = _num(finish.get("fl"))
        min_ff = _num(finish.get("min_ff"), float(SLAB_TOLERANCES["min_ff"])) or float(
            SLAB_TOLERANCES["min_ff"]
        )
        min_fl = _num(finish.get("min_fl"), float(SLAB_TOLERANCES["min_fl"])) or float(
            SLAB_TOLERANCES["min_fl"]
        )
        max_allowed = _num(
            finish.get("max_variation_allowed"), float(SLAB_TOLERANCES["max_variation"])
        ) or float(SLAB_TOLERANCES["max_variation"])

        if max_var is not None and max_var > max_allowed:
            issues.append(f"elevation variation {max_var} in > {max_allowed} in")
        if ff is not None and ff < min_ff:
            issues.append(f"FF {ff} < {min_ff}")
        if fl is not None and fl < min_fl:
            issues.append(f"FL {fl} < {min_fl}")
        if ff is None and fl is None and max_var is None:
            issues.append("no FF/FL or elevation survey provided")
        if not finish.get("saw_cut_plan"):
            issues.append("saw-cut plan missing")

        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"finish": finish})
        return GateResult(
            self.name,
            "PASS",
            f"SOG finish accepted FF={ff} FL={fl} Δ={max_var}",
            {"finish": finish},
        )


class ShotcreteAgent:
    name = "shotcrete"

    def pre_shoot_gate(self, ctx: dict[str, Any]) -> GateResult:
        sc = ctx.get("shotcrete") or {}
        issues: list[str] = []
        for field, label in (
            ("substrate_clean", "substrate clean"),
            ("substrate_ssd", "substrate SSD/prep"),
            ("reinforcement_cover_ok", "mesh/rebar cover"),
            ("nozzleman_certified", "nozzleman certified"),
            ("test_panels_scheduled", "test panels scheduled"),
            ("exclusion_zone_set", "exclusion zone set"),
        ):
            if not sc.get(field):
                issues.append(f"{label} incomplete")

        wind = _num((ctx.get("weather") or {}).get("wind_kph"))
        max_wind = _num(sc.get("max_wind_kph"), SHOTCRETE_LIMITS["max_wind_kph"]) or SHOTCRETE_LIMITS[
            "max_wind_kph"
        ]
        if wind is not None and wind >= max_wind:
            issues.append(f"wind {wind}kph ≥ shotcrete hold {max_wind}kph")

        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"shotcrete": sc})
        return GateResult(self.name, "PASS", "Shotcrete pre-shoot clear", {"shotcrete": sc})

    def placement(self, ctx: dict[str, Any]) -> GateResult:
        sc = ctx.get("shotcrete") or {}
        placement = sc.get("placement") or {}
        if not placement:
            return GateResult(self.name, "HOLD", "No shotcrete placement telemetry", {})

        issues: list[str] = []
        abort: list[str] = []
        rebound = _num(placement.get("rebound_pct"))
        max_rebound = _num(sc.get("max_rebound_pct"), SHOTCRETE_LIMITS["max_rebound_pct"]) or SHOTCRETE_LIMITS[
            "max_rebound_pct"
        ]
        layer = _num(placement.get("layer_thickness_in"))
        max_layer = _num(
            sc.get("max_layer_thickness_in"), SHOTCRETE_LIMITS["max_layer_thickness_in"]
        ) or SHOTCRETE_LIMITS["max_layer_thickness_in"]

        if rebound is not None and rebound > max_rebound:
            issues.append(f"rebound {rebound}% > {max_rebound}%")
        if layer is not None and layer > max_layer:
            issues.append(f"layer {layer} in > {max_layer} in")
        if placement.get("cold_joint_unprepared"):
            issues.append("cold joint not prepared")
        if placement.get("uncontrolled_hazard"):
            abort.append("uncontrolled rebound/substrate hazard")

        if abort:
            return GateResult(self.name, "FAIL", "; ".join(abort), {"placement": placement})
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"placement": placement})
        return GateResult(
            self.name,
            "PASS",
            f"Placement clear rebound={rebound}% layer={layer}in",
            {"placement": placement},
        )


class CIPWallAgent:
    name = "cip-wall"

    def pre_pour_gate(self, ctx: dict[str, Any]) -> GateResult:
        wall = ctx.get("cip_wall") or ctx.get("wall") or {}
        issues: list[str] = []
        for field, label in (
            ("forms_plumb", "forms plumb/aligned"),
            ("ties_torqued", "form ties torqued"),
            ("rebar_inspected", "rebar inspected"),
            ("waterstops_ok", "waterstops OK"),
            ("embeds_ok", "embeds OK"),
            ("lift_plan_published", "lift/rate plan published"),
            ("cleanouts_staged", "cleanouts staged"),
        ):
            if not wall.get(field):
                issues.append(f"{label} incomplete")

        if issues:
            status = "FAIL" if wall.get("waterstops_ok") is False else "HOLD"
            return GateResult(self.name, status, "; ".join(issues), {"cip_wall": wall})
        return GateResult(self.name, "PASS", "CIP wall pre-pour forms/rebar/plan clear", {"cip_wall": wall})

    def pour_monitor(self, ctx: dict[str, Any]) -> GateResult:
        wall = ctx.get("cip_wall") or ctx.get("wall") or {}
        pour = wall.get("pour") or {}
        if not pour:
            return GateResult(self.name, "HOLD", "No CIP wall pour telemetry", {})

        issues: list[str] = []
        abort: list[str] = []
        lift = _num(pour.get("lift_height_ft"))
        rate = _num(pour.get("rate_ft_per_hr"))
        pressure = _num(pour.get("form_pressure_psf"))
        max_lift = _num(wall.get("max_lift_height_ft"), CIP_WALL_LIMITS["max_lift_height_ft"]) or CIP_WALL_LIMITS[
            "max_lift_height_ft"
        ]
        max_rate = _num(wall.get("max_rate_ft_per_hr"), CIP_WALL_LIMITS["max_rate_ft_per_hr"]) or CIP_WALL_LIMITS[
            "max_rate_ft_per_hr"
        ]
        max_pressure = _num(
            wall.get("max_form_pressure_psf"), CIP_WALL_LIMITS["max_form_pressure_psf"]
        ) or CIP_WALL_LIMITS["max_form_pressure_psf"]

        if lift is not None and lift > max_lift:
            issues.append(f"lift {lift} ft > {max_lift} ft")
        if rate is not None and rate > max_rate:
            issues.append(f"pour rate {rate} ft/hr > {max_rate}")
        if pressure is not None and pressure > max_pressure:
            abort.append(f"form pressure {pressure} psf > {max_pressure}")
        if pour.get("form_bulge") or pour.get("form_leak"):
            abort.append("form bulge/leak observed")
        if pour.get("vibration_continuous") is False:
            issues.append("vibration not continuous")

        if abort:
            return GateResult(self.name, "FAIL", "; ".join(abort), {"pour": pour})
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"pour": pour})
        return GateResult(
            self.name,
            "PASS",
            f"CIP pour clear lift={lift}ft rate={rate} pressure={pressure}",
            {"pour": pour},
        )


class ElevatedDeckAgent:
    name = "elevated-deck"

    def pre_pour_gate(self, ctx: dict[str, Any]) -> GateResult:
        deck = ctx.get("deck") or {}
        issues: list[str] = []
        if not deck.get("layout_type"):
            issues.append("deck layout_type missing (pan/metal/plywood)")
        if not deck.get("supports_verified"):
            issues.append("shoring/reshores not verified")
        if not deck.get("pour_strips_mapped"):
            issues.append("pour strips not mapped")
        if not deck.get("forms_ready"):
            issues.append("forms not ready")
        if not deck.get("load_path_ok", True):
            return GateResult(self.name, "FAIL", "load-path check failed — do not pour", {"deck": deck})
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"deck": deck})
        return GateResult(
            self.name,
            "PASS",
            f"Elevated deck clear layout={deck.get('layout_type')} shores verified",
            {"deck": deck},
        )

    def pour_monitor(self, ctx: dict[str, Any]) -> GateResult:
        deck = ctx.get("deck") or {}
        if not deck.get("supports_verified"):
            return GateResult(self.name, "FAIL", "shores lost verification under load", {"deck": deck})
        if not deck.get("pour_strip_sequence"):
            return GateResult(self.name, "HOLD", "pour strip sequence missing", {"deck": deck})
        return GateResult(self.name, "PASS", "Elevated pour path clear", {"deck": deck})

    def strip_reshore(self, ctx: dict[str, Any]) -> GateResult:
        deck = ctx.get("deck") or {}
        strip = deck.get("strip") or ctx.get("strip") or {}
        issues: list[str] = []
        abort: list[str] = []

        strength = _num(strip.get("strength_psi"))
        min_psi = _num(strip.get("min_strip_psi"), float(ELEVATED_DECK_LIMITS["min_strip_psi"])) or float(
            ELEVATED_DECK_LIMITS["min_strip_psi"]
        )
        reshore_levels = int(strip.get("reshore_levels") or 0)
        min_levels = int(strip.get("min_reshore_levels") or ELEVATED_DECK_LIMITS["min_reshore_levels"])

        if strength is None or strength < min_psi:
            issues.append(f"strip strength {strength} < {min_psi} psi")
        if reshore_levels < min_levels:
            issues.append(f"reshore levels {reshore_levels} < {min_levels}")
        if not strip.get("reshore_plan_published"):
            issues.append("reshore plan not published")
        if strip.get("backshores_required") and not strip.get("backshores_installed"):
            issues.append("backshores required but not installed")
        if deck.get("load_path_ok") is False or strip.get("load_path_ok") is False:
            abort.append("load-path failure — do not strip")

        if abort:
            return GateResult(self.name, "FAIL", "; ".join(abort), {"strip": strip})
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"strip": strip})
        return GateResult(
            self.name,
            "PASS",
            f"Strip/reshore clear strength={strength} psi levels={reshore_levels}",
            {"strip": strip},
        )


class MassThermalAgent:
    name = "mass-thermal"

    def pre_pour_gate(self, ctx: dict[str, Any]) -> GateResult:
        mass = ctx.get("mass") or {}
        volume = _num(mass.get("volume_cy") or ctx.get("volume_cy"))
        trigger = _num(mass.get("precool_required_above_cy"), MASS_POUR_LIMITS["precool_required_above_cy"]) or MASS_POUR_LIMITS[
            "precool_required_above_cy"
        ]
        issues: list[str] = []
        if volume is None:
            issues.append("volume_cy missing for mass-pour trigger")
        elif volume >= trigger and not mass.get("precool_method"):
            issues.append(f"volume {volume} CY ≥ {trigger} — pre-cool method required")
        if not mass.get("sensor_plan"):
            issues.append("core/surface sensor plan missing")
        if not mass.get("insulation_staged"):
            issues.append("insulation/blankets not staged")
        if not mass.get("limits_published"):
            issues.append("max core / ΔT limits not published")
        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"mass": mass})
        return GateResult(
            self.name,
            "PASS",
            f"Mass thermal plan clear volume={volume} CY precool={mass.get('precool_method', 'n/a')}",
            {"mass": mass},
        )

    def monitor(self, ctx: dict[str, Any]) -> GateResult:
        mass = ctx.get("mass") or {}
        core = _num(mass.get("core_temp_f"))
        surface = _num(mass.get("surface_temp_f"))
        delta = _num(mass.get("delta_t_f"))
        if delta is None and core is not None and surface is not None:
            delta = abs(core - surface)
        max_core = _num(mass.get("max_core_temp_f"), MASS_POUR_LIMITS["max_core_temp_f"]) or MASS_POUR_LIMITS[
            "max_core_temp_f"
        ]
        max_delta = _num(
            mass.get("max_delta_t_f"), THERMAL_LIMITS.get("max_diff", MASS_POUR_LIMITS["max_delta_t_f"])
        ) or float(THERMAL_LIMITS.get("max_diff", MASS_POUR_LIMITS["max_delta_t_f"]))

        if core is None or surface is None:
            return GateResult(self.name, "HOLD", "Missing core/surface temperatures", {"mass": mass})

        abort: list[str] = []
        holds: list[str] = []
        if core > max_core and not mass.get("mitigation_active"):
            abort.append(f"core {core}°F > {max_core}°F without mitigation")
        if delta is not None and delta > max_delta and not mass.get("mitigation_active"):
            abort.append(f"ΔT {delta}°F > {max_delta}°F without mitigation")
        elif delta is not None and delta > max_delta * 0.8:
            holds.append(f"ΔT {delta}°F approaching limit {max_delta}°F — reinforce insulation")

        if abort:
            return GateResult(self.name, "FAIL", "; ".join(abort), {"mass": mass, "delta_t_f": delta})
        if holds:
            return GateResult(self.name, "HOLD", "; ".join(holds), {"mass": mass, "delta_t_f": delta})
        return GateResult(
            self.name,
            "PASS",
            f"Thermal clear core={core}°F surface={surface}°F ΔT={delta}",
            {"mass": mass, "delta_t_f": delta},
        )


class CuringLifecycleAgent:
    name = "curing-lifecycle"

    def daily_check(self, ctx: dict[str, Any]) -> GateResult:
        curing = ctx.get("curing") or {}
        if not curing.get("started") and not curing.get("temperature_f"):
            return GateResult(self.name, "HOLD", "Curing not started / no telemetry", {})

        issues: list[str] = []
        temp = _num(curing.get("temperature_f"))
        moisture = _num(curing.get("moisture"))
        min_temp = _num(curing.get("min_temp_f"), 50.0) or 50.0
        max_temp = _num(curing.get("max_temp_f"), 95.0) or 95.0
        min_moisture = _num(curing.get("min_moisture"), CURING_LIFECYCLE["min_moisture"]) or CURING_LIFECYCLE[
            "min_moisture"
        ]

        if temp is not None and temp < min_temp:
            issues.append(f"curing temp {temp}°F < {min_temp}°F")
        if temp is not None and temp > max_temp:
            issues.append(f"curing temp {temp}°F > {max_temp}°F")
        if moisture is not None and moisture < min_moisture:
            issues.append(f"moisture {moisture} < {min_moisture}")
        if not curing.get("protection_ok", True):
            issues.append("protection/blankets/membrane compromised")

        if issues:
            return GateResult(self.name, "HOLD", "; ".join(issues), {"curing": curing})
        return GateResult(
            self.name,
            "PASS",
            f"Curing OK temp={temp}°F moisture={moisture}",
            {"curing": curing},
        )

    def strength_release(self, ctx: dict[str, Any]) -> GateResult:
        curing = ctx.get("curing") or {}
        release = curing.get("release") or ctx.get("release") or {}
        activity = release.get("activity") or curing.get("release_activity") or "unspecified"
        age_days = _num(release.get("age_days") or curing.get("age_days"))
        min_days = _num(release.get("min_days"), float(CURING_LIFECYCLE["min_days_before_release"])) or float(
            CURING_LIFECYCLE["min_days_before_release"]
        )
        strength = _num(release.get("strength_psi") or curing.get("strength_estimate_psi"))
        min_psi = _num(release.get("min_release_psi"), float(CURING_LIFECYCLE["min_release_psi"])) or float(
            CURING_LIFECYCLE["min_release_psi"]
        )

        issues: list[str] = []
        if age_days is None or age_days < min_days:
            issues.append(f"age {age_days} d < {min_days} d for {activity}")
        if strength is None or strength < min_psi:
            issues.append(f"strength {strength} < {min_psi} psi for {activity}")
        # Still enforce curing band
        band = self.daily_check(ctx)
        if band.status == "HOLD":
            issues.append(band.detail)

        if issues:
            return GateResult(
                self.name,
                "HOLD",
                f"Release HOLD for {activity}: " + "; ".join(issues),
                {"release": release, "activity": activity},
            )
        return GateResult(
            self.name,
            "PASS",
            f"Release GO for {activity} age={age_days}d strength={strength} psi",
            {"release": release, "activity": activity},
        )
