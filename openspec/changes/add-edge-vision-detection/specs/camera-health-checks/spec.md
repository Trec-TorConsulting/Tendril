## ADDED Requirements

### Requirement: Detection Overlays on Snapshots
The system SHALL allow object-detection bounding boxes to be displayed over camera
snapshots and stored grow photos alongside the existing health-check imagery.

#### Scenario: Overlay detections on a health-check snapshot
- **WHEN** a health-check snapshot has associated vision detections and the user enables
  the detection overlay
- **THEN** bounding boxes with class labels and confidence are rendered over the snapshot
  without altering the stored image bytes

#### Scenario: Toggle overlay off
- **WHEN** the user disables the detection overlay
- **THEN** the snapshot is shown without bounding boxes

### Requirement: Scan Trigger From Camera View
The system SHALL let a user trigger an object-detection scan directly from the camera/tent
view, reusing the existing snapshot retrieval pipeline.

#### Scenario: Scan from tent camera view
- **WHEN** a user clicks "Scan" on a tent camera view
- **THEN** the current snapshot is captured via the existing go2rtc/Reolink pipeline and
  submitted for detection, and results are returned as bounding-box overlays

#### Scenario: Scan reuses existing snapshot fallback
- **WHEN** a scan is triggered and go2rtc is unreachable
- **THEN** the snapshot is obtained via the existing Reolink HTTP fallback before detection
  runs
