## 1. CSV Export
- [ ] 1.1 Create generic CSV export utility (SQLAlchemy query → CSV stream)
- [ ] 1.2 Add `?format=csv` support to list endpoints (grows, buckets, sensor-data, expenses, tasks)
- [ ] 1.3 Sensor data export with date range filtering

## 2. PDF Report
- [ ] 2.1 Add WeasyPrint or ReportLab dependency
- [ ] 2.2 Create grow report template (HTML → PDF)
- [ ] 2.3 `GET /v1/grows/{id}/report?format=pdf` endpoint
- [ ] 2.4 Include sensor data charts in PDF (matplotlib or chart image)

## 3. Bulk Export
- [ ] 3.1 `GET /v1/export/all` — ZIP of all CSVs
- [ ] 3.2 Async generation for large datasets (background task + download link)

## 4. Testing
- [ ] 4.1 CSV export format tests
- [ ] 4.2 PDF generation tests
- [ ] 4.3 Tenant isolation in exports
