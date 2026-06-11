## 1. Partnership
- [ ] 1.1 Contact Growee (info@growee.com) requesting API partnership / developer access
- [ ] 1.2 Document API endpoints, auth method, and rate limits once access is granted

## 2. Connector (after API access)
- [ ] 2.1 Create `tendril/api/app/integrations/connectors/growee.py`
- [ ] 2.2 Implement device discovery and reading polling
- [ ] 2.3 Map Growee pH/EC/temp to bucket sensor readings
- [ ] 2.4 Log dosing events to grow journal

## 3. Frontend
- [ ] 3.1 Add Growee option to integration type selector
- [ ] 3.2 Create Growee-specific config form

## 4. Validation
- [ ] 4.1 Test with real Growee device (if API access granted)
