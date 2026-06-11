## ADDED Requirements
### Requirement: Generic RTSP Camera Support
The system SHALL support direct RTSP camera connections for snapshot capture and timelapse generation independent of Frigate.

#### Scenario: Capture RTSP snapshot
- **WHEN** a snapshot interval elapses for a configured RTSP camera
- **THEN** the system grabs a single frame from the RTSP stream via ffmpeg and stores it in object storage

#### Scenario: Generate timelapse
- **WHEN** a user requests a timelapse for a grow with stored snapshots
- **THEN** the system concatenates periodic snapshots into an MP4 video
