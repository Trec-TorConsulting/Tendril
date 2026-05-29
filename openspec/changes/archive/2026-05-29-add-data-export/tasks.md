## 1. CSV Export
- [x] 1.1 Create generic CSV export utility (SQLAlchemy query → CSV stream)
- [x] 1.2 Add `?format=csv` support to list endpoints (grows, buckets, sensor-data, expenses, tasks)
- [x] 1.3 Sensor data export with date range filtering

## 2. PDF Report
- [x] 2.1 Add WeasyPrint dependency
- [x] 2.2 Create grow report template (HTML → PDF)
- [x] 2.3 `GET /v1/data/export/grow/{id}/report` endpoint
- [x] 2.4 Include sensor data stats, health evals, journal entries in PDF

## 3. Bulk Export
- [x] 3.1 `GET /v1/export/all` — ZIP of all CSVs
- [x] 3.2 Multi-section grow export with ZIP packaging

## 4. Testing
- [ ] 4.1 CSV export format tests
- [ ] 4.2 PDF generation tests
- [ ] 4.3 Tenant isolation in exports
