# System test name templates

Source: `STANDARD_TESTS` in `commissioning_service.py`. Tag every line `[TEMPLATE]` unless the project plan lists it.

HVAC central plant: chiller startup, boiler startup, cooling tower, pump staging, sequencing, energy sequences.

HVAC air handling: airflow, temperature control, humidity, filter monitoring, economizer, demand control ventilation, freeze protection.

Fire alarm: device verification, notification appliances, monitoring, HVAC/elevator interface, battery backup, FACP programming.

Building automation: point-to-point, graphics, trending and alarming, scheduling, integration, cybersecurity verification.

Other system types exist on the enum (plumbing, fire sprinkler, electrical, elevator, and others) with no standard test list in that file. Ask for the project commissioning plan. Do not invent the tests.
