"""ORP (Oxidation-Reduction Potential) utilities for system-type-aware configurations.

Supports dynamic ORP ranges based on hydroponic system approach:
  - Live/Beneficial (Hydroguard): Lower ORP range where beneficial bacteria thrive
  - Sterilized (H2O2): Higher ORP range for pathogen control via oxidation
"""

# Default ORP ranges by system type and grow stage
ORP_DEFAULTS = {
    "live_beneficial": {
        "min": 200,
        "max": 300,
        "target": 260,
        "description": "Live system (Hydroguard). Lower ORP favors beneficial microbes.",
    },
    "sterilized": {
        "min": 300,
        "max": 450,
        "target": 375,
        "description": "Sterilized system (H2O2). Higher ORP kills pathogens.",
    },
}


def get_orp_range(
    stage_config: dict | None,
    system_type: str = "sterilized",
) -> dict | None:
    """Get ORP range for a stage, accounting for system type.

    Args:
        stage_config: The stage reservoir config dict (contains "orp_mv" or "orp_mv_variants")
        system_type: "live_beneficial" or "sterilized"

    Returns:
        Dict with {"min", "max", "target"} or None if ORP not applicable for this stage
    """
    if not stage_config:
        return None

    # Check for new variant-based config
    orp_variants = stage_config.get("orp_mv_variants", {})
    if orp_variants and system_type in orp_variants:
        return orp_variants[system_type]

    # Fall back to legacy "orp_mv" field (treated as default/sterilized)
    orp_mv = stage_config.get("orp_mv")
    if orp_mv:
        return orp_mv

    return None


def get_orp_status(
    value: float | None,
    stage_config: dict | None,
    system_type: str = "sterilized",
) -> str:
    """Determine ORP status (ok, warning, critical) based on system type.

    Args:
        value: Current ORP reading in mV
        stage_config: Stage reservoir config
        system_type: "live_beneficial" or "sterilized"

    Returns:
        "ok", "warning", or "critical"
    """
    if value is None:
        return "warning"

    orp_range = get_orp_range(stage_config, system_type)
    if not orp_range:
        return "ok"  # ORP not applicable for this stage

    min_val = orp_range.get("min")
    max_val = orp_range.get("max")

    if min_val is None or max_val is None:
        return "ok"

    if min_val <= value <= max_val:
        return "ok"
    elif (value < min_val and value > min_val - 50) or (value > max_val and value < max_val + 50):
        return "warning"
    else:
        return "critical"
