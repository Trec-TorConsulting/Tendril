## 1. Connector
- [ ] 1.1 Create `tendril/api/app/integrations/connectors/tuya.py`
- [ ] 1.2 Implement Tuya OAuth2 token management (client credentials, 2-hour expiry refresh)
- [ ] 1.3 Implement device discovery via Tuya Cloud API
- [ ] 1.4 Implement state polling for plugs (power W, on/off) and sensors (temp, humidity)
- [ ] 1.5 Implement device toggle action for automation rules

## 2. Frontend
- [ ] 2.1 Add Tuya option to integration type selector
- [ ] 2.2 Create Tuya config form (API key, secret, data center region)
- [ ] 2.3 Create device browser showing discovered Tuya devices

## 3. Validation
- [ ] 3.1 Test OAuth2 flow and token refresh
- [ ] 3.2 Test smart plug state polling
- [ ] 3.3 Test device toggle via automation action
