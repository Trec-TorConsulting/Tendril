# Change: Add Bluelab Integration

## Why
Bluelab makes professional pH and EC monitors/controllers (Guardian, Connect) widely used in commercial hydroponics. Their Connect products have WiFi + cloud connectivity, but API access status is unclear.

## What Changes
- New Bluelab connector (pending API access)
- Polls pH, EC, and temperature from Bluelab Connect devices
- Fallback: Document manual readings entry or HA bridge path

## Impact
- Affected specs: `integrations-framework`
- Depends on: `add-integrations-framework`
- **POTENTIALLY BLOCKED**: API access status unclear — requires research/contact
- No breaking changes

## Integration Details
- **API Status**: Bluelab Connect cloud exists, developer API documentation not found publicly
- **Action Required**: Contact Bluelab (support@bluelab.com) or research HA community integration
- **Products**: Bluelab Guardian ($330), Bluelab Connect ($150+), Bluelab Pro Controller ($1500)
- **Data**: pH, EC, temperature (solution)
- **Fallback**: Route through Home Assistant bridge if HA community integration exists
- **Effort**: HIGH (API access uncertain)
