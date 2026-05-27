## ADDED Requirements

### Requirement: Edit Device Map Target
The system SHALL allow users to edit the target tent or bucket of an existing device mapping after creation.

#### Scenario: Edit target via dialog
- **WHEN** a user clicks "Edit Target" from the device map row dropdown
- **THEN** a dialog opens with the current tent/bucket pre-selected, allowing the user to change the target and save

#### Scenario: Update target via API
- **WHEN** PATCH `/integrations/{id}/devices/{device_id}` is called with new `tent_id` or `bucket_id`
- **THEN** the device mapping target is updated and subsequent syncs route readings to the new target
