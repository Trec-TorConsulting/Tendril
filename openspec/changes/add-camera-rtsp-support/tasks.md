## 1. Backend
- [ ] 1.1 Add RTSP camera type to device model
- [ ] 1.2 Implement RTSP snapshot capture via ffmpeg subprocess
- [ ] 1.3 Create snapshot scheduler (configurable interval per camera)
- [ ] 1.4 Store snapshots in MinIO (same path as Frigate snapshots)
- [ ] 1.5 Implement timelapse generation from stored snapshots

## 2. Frontend
- [ ] 2.1 Add RTSP camera to device type selector
- [ ] 2.2 Create RTSP config form (URL, username, password, snapshot interval)
- [ ] 2.3 Add "Test Connection" button that grabs a single frame preview
- [ ] 2.4 Timelapse viewer on grow detail page

## 3. Infrastructure
- [ ] 3.1 Ensure ffmpeg is in the API container image
- [ ] 3.2 Handle RTSP auth (username:password in URL)

## 4. Validation
- [ ] 4.1 Test snapshot capture from various RTSP camera brands
- [ ] 4.2 Test timelapse generation
- [ ] 4.3 Verify AI visual analysis works with RTSP snapshots
