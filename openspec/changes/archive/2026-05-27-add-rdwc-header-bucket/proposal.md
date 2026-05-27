# Change: Add RDWC Header Bucket Role & Reading Propagation

## Why
In RDWC (Recirculating Deep Water Culture), a single header/control bucket holds the shared nutrient solution that circulates to all connected site buckets. Sensor readings taken at the header bucket reflect the water quality for the entire system. Users need a way to designate a header bucket so its readings automatically propagate to all site buckets, and so feeding calculations know the system volume.

## What Changes
- **Bucket role field** — New `role` column on `buckets` table (`site` default, `header`) to distinguish header/control buckets from site buckets
- **Reading propagation** — When sensor readings are written to a header bucket, they are automatically duplicated to all site buckets in the same grow cycle
- **RDWC UI** — Add/Edit bucket dialogs show a Role selector for RDWC grows; bucket cards display a "Header" badge
- **Device map editing** — Users can now edit the target (tent/bucket) of existing device mappings in the integrations page

## Impact
- Affected specs: `bucket-monitoring`, `integrations-framework`
- Affected code:
  - `api/app/grows/models.py` (role column)
  - `api/app/grows/bucket_routes.py` (schema updates)
  - `api/migrations/versions/0033_bucket_role_column.py`
  - `api/app/integrations/connectors/base.py` (propagation function)
  - `api/app/integrations/connectors/tuya.py`, `pulse.py`, `ecowitt.py` (call propagation)
  - `web/src/app/dashboard/grows/[id]/buckets-tab.tsx` (role UI)
  - `web/src/app/dashboard/integrations/page.tsx` (edit target dialog)
  - `web/src/lib/api.ts` (type updates)
- No breaking changes — existing buckets default to `role = "site"`
