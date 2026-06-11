## 1. Partnership
- [ ] 1.1 Contact TrolMaster requesting API / developer partnership
- [ ] 1.2 Research HA community integrations as a fallback path
- [ ] 1.3 Document API endpoints once access is granted

## 2. Connector (after API access)
- [ ] 2.1 Create `tendril/api/app/integrations/connectors/trolmaster.py`
- [ ] 2.2 Implement device discovery for Hydro-X and Aqua-X systems
- [ ] 2.3 Map environment data (temp, humidity, CO2, VPD, light) to tent sensors
- [ ] 2.4 Map irrigation data (pH, EC, flow rates) to bucket sensors

## 3. Frontend
- [ ] 3.1 Add TrolMaster option to integration type selector
- [ ] 3.2 Create system-specific config form

## 4. Validation
- [ ] 4.1 Test with TrolMaster hardware (if API access granted)
