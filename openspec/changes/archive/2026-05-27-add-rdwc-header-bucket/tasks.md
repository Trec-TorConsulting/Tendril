## 1. Backend — Bucket Role & Propagation

- [x] 1.1 Add `role` column (VARCHAR(20), default 'site') to Bucket model
- [x] 1.2 Create migration 0033 to add role column to buckets table
- [x] 1.3 Update BucketCreate, BucketUpdate, BucketResponse schemas with role field
- [x] 1.4 Implement `propagate_header_bucket_readings()` standalone function in base connector
- [x] 1.5 Wire propagation into Tuya connector persist_readings (method call)
- [x] 1.6 Wire propagation into Pulse connector write_pulse_readings (standalone call)
- [x] 1.7 Wire propagation into Ecowitt connector write_ecowitt_readings (standalone call)

## 2. Frontend — Bucket Role UI

- [x] 2.1 Add `role` field to BucketResponse interface in api.ts
- [x] 2.2 Add `role` param to createBucket and updateBucket functions
- [x] 2.3 Pass growType prop to BucketsTab component
- [x] 2.4 Add role selector (Site / Header) to Add Bucket dialog for RDWC grows
- [x] 2.5 Add role selector to Edit Bucket dialog for RDWC grows
- [x] 2.6 Display "Header" badge on bucket cards with role=header

## 3. Frontend — Edit Device Map Target

- [x] 3.1 Add EditDeviceMapDialog component with tent/bucket selectors
- [x] 3.2 Replace delete-only button with dropdown menu (Edit Target / Remove)
- [x] 3.3 Wire editDeviceMap state and dialog rendering

## 4. Verification

- [x] 4.1 TypeScript compiles with zero errors
- [x] 4.2 Ruff lint passes
- [x] 4.3 Pushed to main, deployed via GH Actions
