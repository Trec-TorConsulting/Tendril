# Change: Add Seed-to-Sale Compliance Tracking

## Why
Regulated cannabis markets (NJ, CA, CO, OR, MI, MA, and expanding) require full chain-of-custody tracking from plant intake through final sale. Tendril already tracks seed-to-harvest; the "to-sale" half (packaging, lab testing, transfers, destruction) is entirely unbuilt. Adding METRC-compatible seed-to-sale tracking makes Tendril viable for licensed commercial operators — a market with high willingness-to-pay and sticky retention.

## What Changes
- New `api/app/compliance/` module with plant tagging, packages, inventory, lab testing, transfers, destruction, and compliance reporting
- New `PlantTag`, `Package`, `InventoryLedger`, `LabTest`, `Transfer`, `TransferPackage`, `Destruction`, `ComplianceEvent` database models
- Auto-create packages when a GrowCycle completes curing
- Full GPS-tracked transport manifests for transfers
- Witness + photo evidence workflow for waste destruction
- QR/barcode generation for plant tags and package labels
- METRC API adapter (NJ primary, framework supports CA/CO/OR/MI/MA)
- Immutable compliance event log (append-only, separate from mutable AuditLog)
- Individual plant tag assignment (one tag per Bucket, METRC 24-char format)
- **BREAKING**: `Yield` model gains a `package_id` FK linking harvests to packages

## Impact
- Affected specs: `bucket-monitoring` (tag assignment), `integrations-framework` (METRC adapter)
- Affected code: `api/app/grows/models.py` (Yield FK), `api/app/compliance/` (new module), `web/src/` (compliance UI pages), `api/migrations/` (new tables + FK)
- New dependency: QR code generation library (`qrcode` or `segno`)
- Billing: Commercial plan only (gated via `require_plan("commercial")`)
- Scale target: Medium commercial (50-500 plants) first release
- Self-hosting: No external service dependencies — METRC integration is opt-in via tenant config
