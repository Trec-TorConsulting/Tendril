# Change: Add TrolMaster Integration

## Why
TrolMaster makes professional-grade environment (Hydro-X) and irrigation (Aqua-X) controllers used in commercial grows. API access would open the commercial grower market for Tendril.

## What Changes
- New TrolMaster connector (pending API access via TrolMaster Pro platform)
- Reads environment data: temp, humidity, CO2, VPD, light
- Reads irrigation data: zone schedules, flow rates, pH/EC
- Maps to Tendril tent ambient + bucket sensor tables

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- **BLOCKED**: No public API — requires partnership with TrolMaster
- Alternative: Route through Home Assistant bridge (community HA integration may exist)
- No breaking changes

## Integration Details
- **API Status**: TrolMaster Pro cloud platform — no public developer API
- **Action Required**: Contact TrolMaster (support@trolmaster.com) for API partnership
- **Systems**: Hydro-X (environment), Aqua-X (irrigation), Tent-X (hobby), Carbon-X (CO2)
- **Effort**: HIGH
