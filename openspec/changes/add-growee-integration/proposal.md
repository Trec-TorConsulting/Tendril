# Change: Add Growee Integration

## Why
Growee makes WiFi-connected auto-dosing systems for hydroponics (auto pH up/down + nutrient dosing). If API access can be secured via partnership, this is the holy grail for hydro growers — Tendril AI feeding advice could directly trigger Growee dosing.

## What Changes
- New Growee connector (pending API access)
- Polls Growee cloud for pH/EC/temp readings and dosing events
- Future: bi-directional — Tendril AI sends dose commands to Growee

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- **BLOCKED**: No public API documented — requires partnership inquiry
- No breaking changes

## Integration Details
- **API Status**: No public developer API found. Cloud dashboard exists.
- **Action Required**: Contact Growee (info@growee.com) for API partnership
- **Products**: Growee Pro ($450), Growee Master ($650)
- **Data**: pH, EC, water temp, dosing events, nutrient levels
- **Effort**: MEDIUM-HIGH (API access uncertain)
