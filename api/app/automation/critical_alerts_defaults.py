"""System-default critical alert rules per grow type.

These are the safety-net thresholds that ship with Tendril for every
supported grow type. They are seeded into the ``automation_rules`` table
on tenant creation (and backfilled for existing tenants via Alembic
migration ``0047``) so every tenant gets visibility and edit access to
them in the same UI as their own custom rules.

Schema-of-record is now the ``automation_rules`` table; this module is
the canonical source for the **defaults only** — the engine no longer
reads it at evaluation time.

To add a new system-default rule:
  1. Add the entry below.
  2. Bump ``DEFAULTS_VERSION`` so the next deploy reseeds tenants whose
     ``Tenant.system_alert_rules_seeded_version`` is stale.

Each rule is a dict with these keys:
  - ``sensor``    (str)   sensor field on ``BucketSensorReading``
  - ``condition`` (str)   one of ``gt``, ``lt``, ``gte``, ``lte``, ``eq``
  - ``threshold`` (float) value to compare against
  - ``message``   (str)   human-readable alert message
  - ``severity``  (str)   ``info`` | ``warning`` | ``critical``
"""

from __future__ import annotations

# Bump when ``CRITICAL_ALERTS`` is edited in a way that should reseed
# tenants on next deploy. Tenants whose seeded version is below this
# value will receive missing defaults (but never have their overrides
# overwritten — see ``seed_system_alert_rules``).
DEFAULTS_VERSION = 1

CRITICAL_ALERTS = {
    "nft": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.1,
            "message": "NFT pump failure — flow rate critically low!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 4.5,
            "message": "NFT pH dangerously low — roots exposed to thin film, pH accuracy critical!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 7.5,
            "message": "NFT pH dangerously high — nutrient lockout imminent!",
            "severity": "critical",
        },
    ],
    "aeroponics": [
        {
            "sensor": "mist_pressure",
            "condition": "lt",
            "threshold": 10,
            "message": "Aeroponics nozzle clog — mist pressure critically low!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 4.5,
            "message": "Aeroponics pH dangerously low — root burn imminent!",
            "severity": "critical",
        },
    ],
    "dwc": [
        {
            "sensor": "dissolved_oxygen",
            "condition": "lt",
            "threshold": 4,
            "message": "DWC dissolved oxygen critically low — check air pump!",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 72,
            "message": (
                "DWC water temp above 72°F — risk of root rot. "
                "Ensure Hydroguard (2 ml/gal) is dosed and air stones are running."
            ),
            "severity": "warning",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 78,
            "message": (
                "DWC water temp critical (>78°F) — pythium risk extreme! Add ice or activate chiller immediately."
            ),
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 15,
            "message": "DWC water level critically low — roots may be exposed!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 4.5,
            "message": "DWC pH dangerously low — nutrient toxicity risk!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 7.5,
            "message": "DWC pH dangerously high — iron/calcium lockout!",
            "severity": "critical",
        },
    ],
    "rdwc": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.1,
            "message": "RDWC circulation pump failure!",
            "severity": "critical",
        },
        {
            "sensor": "dissolved_oxygen",
            "condition": "lt",
            "threshold": 4,
            "message": "RDWC dissolved oxygen critically low!",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 78,
            "message": "RDWC water temp critical (>78°F) — pythium risk extreme!",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 15,
            "message": "RDWC reservoir level critical — pump may run dry!",
            "severity": "critical",
        },
    ],
    "ebb_flow": [
        {
            "sensor": "water_level_pct",
            "condition": "gt",
            "threshold": 95,
            "message": "Ebb & Flow overflow risk — water level >95%! Check drain valve.",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 10,
            "message": "Ebb & Flow pump failure — tray not flooding!",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 7.5,
            "message": "Ebb & Flow pH too high — salt buildup likely!",
            "severity": "warning",
        },
    ],
    "drip": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.05,
            "message": "Drip emitter blockage detected — flow rate near zero!",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 4.0,
            "message": "Drip runoff EC dangerously high (>4.0) — salt buildup critical! Flush immediately.",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 3.0,
            "message": "Drip runoff EC elevated (>3.0) — salt accumulation building, schedule flush.",
            "severity": "warning",
        },
    ],
    "aquaponics": [
        {
            "sensor": "dissolved_oxygen",
            "condition": "lt",
            "threshold": 5,
            "message": "Aquaponics DO critically low — fish suffocating! Check aerator immediately.",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "gt",
            "threshold": 82,
            "message": "Aquaponics water temp >82°F — lethal for most fish species!",
            "severity": "critical",
        },
        {
            "sensor": "water_temp_f",
            "condition": "lt",
            "threshold": 55,
            "message": "Aquaponics water temp <55°F — fish metabolism dangerously low!",
            "severity": "warning",
        },
        {
            "sensor": "ph",
            "condition": "lt",
            "threshold": 6.0,
            "message": "Aquaponics pH too low — harmful to fish! Target 6.8-7.2.",
            "severity": "critical",
        },
        {
            "sensor": "ph",
            "condition": "gt",
            "threshold": 8.0,
            "message": "Aquaponics pH too high — ammonia toxicity increases with pH! Target 6.8-7.2.",
            "severity": "critical",
        },
    ],
    "dutch_bucket": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.05,
            "message": "Dutch bucket emitter blocked — one stuck emitter kills plant!",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 4.0,
            "message": "Dutch bucket runoff EC critical (>4.0) — flush bucket immediately!",
            "severity": "critical",
        },
    ],
    "vertical_tower": [
        {
            "sensor": "flow_rate",
            "condition": "lt",
            "threshold": 0.1,
            "message": "Vertical tower flow failure — top plants drying out!",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 15,
            "message": "Vertical tower reservoir low — pump may run dry!",
            "severity": "critical",
        },
    ],
    "kratky": [
        {
            "sensor": "water_level_pct",
            "condition": "gt",
            "threshold": 90,
            "message": "Kratky water level too high (>90%) — air gap eliminated, roots suffocating!",
            "severity": "critical",
        },
        {
            "sensor": "water_level_pct",
            "condition": "lt",
            "threshold": 10,
            "message": "Kratky water level critical — roots may lose contact!",
            "severity": "warning",
        },
    ],
    "coco": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 20,
            "message": "Coco critically dry (<20%) — immediate irrigation needed!",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 4.0,
            "message": "Coco runoff EC dangerously high (>4.0) — salt toxicity! Flush with pH'd water.",
            "severity": "critical",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 3.0,
            "message": "Coco runoff EC elevated (>3.0) — schedule a flush soon.",
            "severity": "warning",
        },
    ],
    "rockwool": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 15,
            "message": "Rockwool slab critically dry (<15%) — immediate irrigation needed!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 85,
            "message": "Rockwool over-saturated (>85%) — root suffocation risk, skip next irrigation.",
            "severity": "warning",
        },
        {
            "sensor": "runoff_ec",
            "condition": "gt",
            "threshold": 5.0,
            "message": "Rockwool runoff EC extreme (>5.0) — emergency flush required!",
            "severity": "critical",
        },
    ],
    "soil": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 15,
            "message": "Soil critically dry (<15%) — plant wilting imminent!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 85,
            "message": "Soil waterlogged (>85%) — root rot and fungus gnat risk!",
            "severity": "warning",
        },
    ],
    "living_soil": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 20,
            "message": "Living soil too dry (<20%) — microbial life dying! Water immediately (no runoff).",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 80,
            "message": "Living soil too wet (>80%) — anaerobic conditions forming, harming biology!",
            "severity": "warning",
        },
    ],
    "outdoor_soil": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 10,
            "message": "Outdoor soil critically dry (<10%) — deep water immediately!",
            "severity": "critical",
        },
    ],
    "outdoor_container": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 15,
            "message": "Outdoor container critically dry (<15%) — containers dry faster, water now!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 90,
            "message": "Outdoor container waterlogged (>90%) — check drainage holes!",
            "severity": "warning",
        },
    ],
    "wicking": [
        {
            "sensor": "soil_moisture",
            "condition": "lt",
            "threshold": 25,
            "message": "Wicking system dry (<25%) — reservoir empty or wick disconnected!",
            "severity": "critical",
        },
        {
            "sensor": "soil_moisture",
            "condition": "gt",
            "threshold": 90,
            "message": "Wicking system over-saturated (>90%) — algae risk on wick!",
            "severity": "warning",
        },
    ],
}
