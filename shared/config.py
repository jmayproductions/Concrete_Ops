# shared/config.py

# ---- Pour Thresholds ----
POUR_TIME_WINDOW = {
    "start": "06:00",
    "end": "14:00"
}

# ---- QA/Testing Thresholds ----
STRENGTH_THRESHOLD_PSI = 4000  # compressive strength baseline

# ---- Fail-Safe Rules ----
FAILSAFE_RULES = [
    {"metric": "slump", "comparator": ">", "threshold": 6.0},
    {"metric": "temperature", "comparator": ">", "threshold": 95},
    {"metric": "evaporation_rate", "comparator": ">", "threshold": 0.25},
    {"metric": "wind_speed", "comparator": ">", "threshold": 20},
]

# ---- Report Metadata ----
REPORT_METADATA = {
    "author": "ConcreteOps AI",
    "version": "1.0",
    "company": "StructureWave",
    "disclaimer": "Auto-generated QA report — verified via sensor & logic engine."
}
GEO_RISK_THRESHOLDS = {
    "min_bearing_capacity_ksf": 1.5,
    "min_groundwater_depth_ft": 3.0,
    "max_slope_percent": 5.0
}
CURING_THRESHOLDS = {
    "min_temp": 50.0,         # °F
    "max_temp": 95.0,         # °F
    "min_moisture": 0.85      # decimal (1.0 = fully saturated)
}
SLUMP_RANGE = {
    "min": 3.5,
    "max": 6.0
}
TEMPERATURE_THRESHOLDS = {
    "max_concrete_temp": 90.0,
    "max_ambient_temp": 95.0,
    "min_humidity": 30.0
}
MIX_REQUIREMENTS = {
    "min_psi": 3500,
    "max_w_c_ratio": 0.45,
    "slump_range": (3.5, 6.0),
    "air_content_range": (4.0, 7.0)
}
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
WEATHER_API_KEY = "your_api_key_here"

SITE_COORDS = {
    "lat": 45.512794,
    "lon": -122.679565
}
THERMAL_LIMITS = {
    "max_diff": 35.0  # degrees Fahrenheit
}
FORMWORK_TOLERANCES = {
    "plumb": 0.125,  # inches per foot
    "level": 0.25    # inches across 10'
}
ANCHOR_TOLERANCES = {
    "x": 0.25,  # inches horizontal tolerance
    "y": 0.25,
    "z": 0.125  # vertical embed depth tolerance
}
WEATHER_API_KEY = "your-api-key-here"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

# ---- Specialty workflow thresholds ----
SLAB_TOLERANCES = {
    "max_variation": 0.25,  # inches across survey set
    "min_ff": 25,
    "min_fl": 20,
}
SHOTCRETE_LIMITS = {
    "max_rebound_pct": 20.0,
    "min_core_psi": 4000,
    "max_layer_thickness_in": 4.0,
    "max_wind_kph": 35.0,
}
CIP_WALL_LIMITS = {
    "max_lift_height_ft": 5.0,
    "max_rate_ft_per_hr": 8.0,
    "max_form_pressure_psf": 1200.0,
    "min_vibrate_interval_ft": 2.0,
}
ELEVATED_DECK_LIMITS = {
    "min_reshore_levels": 2,
    "min_strip_strength_psi": 0.75,  # fraction of design f'c when absolute not given
    "min_strip_psi": 3000,
}
MASS_POUR_LIMITS = {
    "max_core_temp_f": 160.0,
    "max_delta_t_f": 35.0,  # mirrors THERMAL_LIMITS
    "precool_required_above_cy": 500,
}
CURING_LIFECYCLE = {
    "min_days_before_release": 3,
    "min_release_psi": 3000,
    "min_moisture": 0.85,
}
