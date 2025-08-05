# modules/mix_design_validator/mix_checker.py

"""
ConcreteOps: Mix Design Validator
Validates concrete mix designs against project requirements, rule thresholds, and field tolerances.
"""

from shared.utils import log_event, trigger_alert
from shared.config import MIX_REQUIREMENTS


def validate_mix_design(mix: dict) -> bool:
    """
    Example mix input:
    {
        "psi": 4000,
        "w_c_ratio": 0.42,
        "slump_target": 5.0,
        "air_content": 5.5
    }
    """

    issues = []

    if mix["psi"] < MIX_REQUIREMENTS["min_psi"]:
        issues.append(f"Compressive strength too low: {mix['psi']} psi")

    if mix["w_c_ratio"] > MIX_REQUIREMENTS["max_w_c_ratio"]:
        issues.append(f"Water-cement ratio too high: {mix['w_c_ratio']}")

    if not (MIX_REQUIREMENTS["slump_range"][0] <= mix["slump_target"] <= MIX_REQUIREMENTS["slump_range"][1]):
        issues.append(f"Slump target out of range: {mix['slump_target']} in")

    if not (MIX_REQUIREMENTS["air_content_range"][0] <= mix["air_content"] <= MIX_REQUIREMENTS["air_content_range"][1]):
        issues.append(f"Air content out of range: {mix['air_content']}%")

    if issues:
        for issue in issues:
            trigger_alert(f"Mix issue: {issue}")
        log_event(f"Mix validation FAILED: {issues}")
        return False

    log_event("Mix validation PASSED")
    return True
