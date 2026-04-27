## ADDED Requirements

### Requirement: Push Notifications for Environmental Alerts
The system SHALL send push notifications to subscribed devices when environmental alerts are triggered (pH/EC out of range, water level low, temperature extremes).

#### Scenario: Alert push notification
- **WHEN** an environmental alert is generated and the user has an active push subscription
- **THEN** a push notification is sent to the device with the alert severity and details

#### Scenario: Health check completion notification
- **WHEN** a scheduled or manual health check completes
- **THEN** a push notification is sent with a summary of the health evaluation
