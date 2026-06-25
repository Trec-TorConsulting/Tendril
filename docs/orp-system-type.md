<!-- OPENSPEC:START -->
# ORP System Type Configuration Guide

This guide explains how to configure ORP (Oxidation-Reduction Potential) ranges for your RDWC system based on whether you're running a **Live system (Hydroguard)** or **Sterilized system (H2O2)**.

<!-- OPENSPEC:END -->

## Problem

Previously, Tendril displayed a fixed ORP optimal range of **300-450 mV** for all RDWC systems. However:
- **Live systems** with beneficial bacteria (Hydroguard) thrive at **150-250 mV**
- **Sterilized systems** with H2O2 require **300-450 mV**

This caused false "error" alerts when running Live systems at their correct 150-250 mV range.

## Solution

Tendril now supports configuring your system type when creating a grow cycle, which automatically adjusts ORP display ranges across all dashboards.

## Quick Setup

### 1. **Identify Your System Type**

Before creating a grow, determine which approach you're using:

| Aspect | Live/Beneficial | Sterilized |
|--------|-----------------|-----------|
| **Approach** | Beneficial bacteria | H2O2 or oxidizing agents |
| **ORP Range** | 150-250 mV | 300-450 mV |
| **Target ORP** | 200 mV | 375 mV |
| **Example Product** | Hydroguard (Bacillus amyloliquefaciens) | 3% H2O2 solution |
| **Dosage** | ~2 ml/gal | ~3 ml/gal (3% solution) |
| **Best For** | Organic-style, microbial ecosystem | Clinic-clean, sterile environment |

### 2. **Set System Type in Grow Settings**

When creating or updating a grow cycle, store the system type in the `settings` JSON field:

```json
{
  "name": "Summer Flower Run",
  "grow_type": "rdwc",
  "stage": "seedling",
  "settings": {
    "system_type": "live_beneficial"
  }
}
```

**Valid values:**
- `"live_beneficial"` — For Hydroguard/beneficial bacteria systems
- `"sterilized"` — For H2O2 or sterilization-based systems

### 3. **Verify on Dashboards**

After setting the system type:
- ✅ **Analytics Dashboard**: ORP gauge displays with correct zones
  - Live: Green zone = 150-250 mV
  - Sterilized: Green zone = 300-450 mV
- ✅ **Dashboards auto-adjust**: No false error warnings

## API Usage

### Create a Grow with System Type

```bash
POST /api/grows
{
  "name": "Spring Veg Cycle",
  "grow_type": "rdwc",
  "tent_id": "...",
  "stage": "seedling",
  "settings": {
    "system_type": "live_beneficial"
  }
}
```

### Update Existing Grow Settings

```bash
PATCH /api/grows/{grow_id}
{
  "settings": {
    "system_type": "sterilized"
  }
}
```

## What Changed in the Codebase

### Backend
1. **`api/app/grows/orp_utils.py`** — New utility module for ORP range lookups
   - `get_orp_range(stage_config, system_type)` — Returns ORP min/max/target
   - `get_orp_status(value, stage_config, system_type)` — Checks if ORP is ok/warning/critical

2. **`api/app/grows/grow_type_configs/rdwc.py`** — Updated all 9 active stages
   - Each stage now includes `"orp_mv_variants"` with both system types
   - Maintains backward compatibility with existing `"orp_mv"` field

### Frontend
1. **`web/src/components/sensor-gauge.tsx`**
   - New `getOrpZones(systemType)` function generates zones dynamically
   - `SensorGaugeProps` now accepts optional `systemType` prop

2. **`web/src/app/dashboard/analytics/page.tsx`**
   - Imports `getOrpZones` function
   - ORP gauge now passes system_type from grow settings
   - Zones update automatically based on grow configuration

## Troubleshooting

### Issue: ORP Gauge Still Shows Old Ranges

**Solution**: Ensure the grow cycle has `system_type` set in its `settings` field. If not set, it defaults to "sterilized" (300-450 mV).

```python
# Check current settings
grow = await session.get(GrowCycle, grow_id)
print(grow.settings)  # Should include "system_type" key

# Fix: Update the grow
if not grow.settings:
    grow.settings = {}
grow.settings["system_type"] = "live_beneficial"
await session.flush()
```

### Issue: ORP Values Out of Range But System is Running Fine

**Check**: Is your system_type correctly set?
- If using Hydroguard and settings show `"sterilized"`, change to `"live_beneficial"`
- If using H2O2 and settings show `"live_beneficial"`, change to `"sterilized"`

### Issue: New Grows Created Before This Update Don't Have system_type

**Solution**: Manually update their `settings.system_type` or recreate the grow with the correct type.

```python
# Migration: Set all existing grows to sterilized (safe default)
grows = await session.execute(select(GrowCycle))
for grow in grows:
    if not grow.settings:
        grow.settings = {}
    if "system_type" not in grow.settings:
        grow.settings["system_type"] = "sterilized"
await session.commit()
```

## Examples

### Example 1: Live System Setup
You've switched to Hydroguard and flushed your RDWC yesterday.

```json
{
  "name": "Summer Flower - Live Beneficial",
  "grow_type": "rdwc",
  "settings": {
    "system_type": "live_beneficial"
  }
}
```

**Expected ORP**: 150-250 mV (green zone)  
**If showing 200 mV**: ✅ Perfect! Beneficial bacteria thriving.  
**If showing 350 mV**: ⚠️ Check for H2O2 residue or aeration issues; beneficial microbes may be stressed.

### Example 2: Sterilized System Setup
You're running a strict H2O2 sterilization protocol.

```json
{
  "name": "Spring Veg - Sterile",
  "grow_type": "rdwc",
  "settings": {
    "system_type": "sterilized"
  }
}
```

**Expected ORP**: 300-450 mV (green zone)  
**If showing 375 mV**: ✅ Optimal sterilization level.  
**If showing 180 mV**: ⚠️ ORP too low; H2O2 not maintaining oxidation; bacteria may be growing.

## Advanced: Health Checks & AI Diagnostics

When this feature is fully integrated:
- **Health check system** will use system-type-aware ORP thresholds
- **AI diagnostics** will understand ORP in context (Live vs Sterilized)
- **Alerts** will only trigger when truly out of spec for the chosen system type

## Future Enhancements

- [ ] UI dropdown in grow creation to select system type
- [ ] Migrate all historical grows to have explicit system_type
- [ ] Update Grows dashboard sensors tab for system-type-aware ranges
- [ ] Integrate system_type into health check logic
- [ ] Support system_type selection for other hydro types (DWC, NFT, etc.)

---

**Questions?** Check the API documentation or contact support.
