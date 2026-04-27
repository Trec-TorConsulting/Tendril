## ADDED Requirements

### Requirement: Photo Comparison
The system SHALL support side-by-side photo comparison for a tent or bucket, pulling from stored health check snapshots and user-uploaded photos.

#### Scenario: Side-by-side comparison
- **WHEN** a user opens the photo compare view and selects two dates
- **THEN** the snapshots from those dates are displayed side-by-side with a slider

#### Scenario: Quick compare
- **WHEN** a user clicks "Compare to 1 week ago" in the bucket detail view
- **THEN** the most recent snapshot is shown alongside the snapshot from approximately 7 days earlier
