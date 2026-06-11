# Change: Add Camera RTSP Support

## Why
Tendril already has camera snapshot support via Frigate. Extend this to support generic RTSP cameras directly — many growers have standalone IP cameras that aren't routed through Frigate. Also enables timelapse generation and AI visual analysis from any RTSP-capable camera.

## What Changes
- Direct RTSP camera support in device model
- Snapshot capture from RTSP stream (ffmpeg frame grab)
- Timelapse generation from periodic snapshots
- Works alongside existing Frigate camera path

## Impact
- Affected specs: `integrations-framework`
- Extends existing camera/snapshot functionality
- No breaking changes — additive to existing Frigate path

## Integration Details
- **Protocol**: RTSP (standard IP camera protocol)
- **Snapshot Method**: `ffmpeg -i rtsp://... -frames:v 1 -f image2 -` (single frame grab)
- **Dependencies**: ffmpeg in API container
- **Cameras**: Any RTSP camera (Reolink, Amcrest, Hikvision, Wyze, etc.)
- **Timelapse**: Periodic snapshots → ffmpeg concat to MP4
- **Effort**: MEDIUM (ffmpeg integration, stream handling)
