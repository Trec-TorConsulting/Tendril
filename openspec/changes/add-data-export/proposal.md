# Change: Add Data Export (CSV, PDF Reports)

## Why
Every competitor offers data export. Tendril currently has no way to export any data. Growers need exports for: compliance records, sharing with partners/consultants, tax documentation, backup, and migration. This is table-stakes functionality identified as #3 gap in competitive analysis.

## What Changes

### New: CSV Export
- Export any list endpoint as CSV: grows, buckets, sensor readings, expenses, health photos, tasks
- `GET /v1/grows/{id}/export?format=csv` — Full grow data dump
- `GET /v1/sensor-data/{device_id}/export?format=csv&start=&end=` — Sensor history

### New: PDF Grow Report
- `GET /v1/grows/{id}/report?format=pdf` — Comprehensive grow report
- Includes: grow summary, stage timeline, sensor charts, expense summary, yield data, health photo log
- Printable format for compliance/records

### New: Bulk Export
- `GET /v1/export/all?format=csv` — Export all data for backup/migration
- Respects tenant isolation

## Impact
- Affected code: Export utilities, PDF generation (WeasyPrint or similar), new routes
- New spec: `data-export`
