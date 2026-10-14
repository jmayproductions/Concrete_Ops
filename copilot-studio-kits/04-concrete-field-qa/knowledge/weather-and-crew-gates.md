# Weather and crew gates (template)

From `pour_controller.py` PourConfig and SiteConditions.

Hold the pour if any of these are true and not waived in a cited project document:

- temperature_f < 40 or > 90
- wind_speed_mph > 25
- precipitation = true
- ground_conditions = frozen (or wet if the spec forbids it)
- access_clear = false
- crew_size < 4
- required certifications (template: ACI, OSHA) not confirmed

Record temperature, humidity, wind, precipitation, ground, access, crew size, and who confirmed them. If the user did not give a value, it is Unknown — the gate stays closed.
