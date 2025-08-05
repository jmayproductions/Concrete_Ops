# modules/geo_check/soil_validation.py

"""
ConcreteOps: Soil Validation Module
Validates site conditions based on geotechnical input, bearing capacity, and groundwater risk thresholds.
"""

from shared.utils import log_event, trigger_alert
from shared.config import GEO_RISK_THRESHOLDS


def validate_site_conditions(site_profile: dict) -> bool:
    """
    Example site_profile:
    {
        "soil_type": "clay",
        "bearing_capacity_ksf": 2.1,
        "groundwater_depth_ft": 4.2,
        "slope_percent": 3.0
    }
    """
    issues = []

    if site_profile["bearing_capacity_ksf"] < GEO_RISK_THRESHOLDS["min_bearing_capacity_ksf"]:
        issues.append("Low bearing capacity")

    if site_profile["groundwater_depth_ft"] < GEO_RISK_THRESHOLDS["min_groundwater_depth_ft"]:
        issues.append("Shallow groundwater level")

    if site_profile["slope_percent"] > GEO_RISK_THRESHOLDS["max_slope_percent"]:
        issues.append("Excessive slope")

    if issues:
        for issue in issues:
            trigger_alert(f"Site condition issue: {issue}")
        log_event(f"Site validation FAILED: {issues}")
        return False

    log_event("Site validation PASSED")
    return True
