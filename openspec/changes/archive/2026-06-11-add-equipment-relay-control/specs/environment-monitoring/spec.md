## ADDED Requirements

### Requirement: Controllable Equipment Management
The system SHALL provide a multi-protocol equipment control layer that allows tenants to register, configure, and control relay/outlet/dimmer devices associated with their grow tents.

#### Scenario: Register a Tasmota relay
- **WHEN** a tenant creates equipment with `protocol: "tasmota_mqtt"` and `protocol_config: {mqtt_topic: "exhaust_fan"}`
- **THEN** the system stores the equipment record with initial state `{is_on: false}` and enables control commands

#### Scenario: Register a Shelly smart plug
- **WHEN** a tenant creates equipment with `protocol: "shelly_http"` and `protocol_config: {ip_address: "192.168.1.50", generation: 2, channel: 0}`
- **THEN** the system stores the equipment record and verifies connectivity via test-connection

#### Scenario: List tenant equipment
- **WHEN** a tenant requests their equipment list
- **THEN** the system returns all controllable equipment for the tenant with current state, sorted by tent association

#### Scenario: Delete equipment
- **WHEN** a tenant deletes equipment
- **THEN** the system sends an OFF command (if currently on), removes the record, and cascades deletion to state logs

### Requirement: Equipment Command Dispatch
The system SHALL dispatch control commands to equipment via the appropriate protocol adapter, validate safety interlocks before execution, and log all state transitions.

#### Scenario: Turn relay ON via API
- **WHEN** a user sends `POST /v1/equipment/{id}/command` with `{action: "on"}`
- **THEN** the system validates interlocks, publishes the protocol-appropriate command, updates `requested_state`, and logs the state change with source "user"

#### Scenario: Turn relay OFF via API
- **WHEN** a user sends `POST /v1/equipment/{id}/command` with `{action: "off"}`
- **THEN** the system publishes the off command, updates state, and logs the transition

#### Scenario: Set dimmer level
- **WHEN** a user sends `POST /v1/equipment/{id}/command` with `{action: "set_brightness", value: 75}`
- **THEN** the system dispatches the dimmer command via the appropriate protocol and updates state to `{is_on: true, brightness: 75}`

#### Scenario: Command blocked by interlock
- **WHEN** a user attempts to turn ON equipment that conflicts with another active device
- **THEN** the system rejects the command with HTTP 409 and detail explaining which interlock was violated

#### Scenario: Command blocked by cooldown
- **WHEN** a user attempts to turn ON equipment within its cooldown period
- **THEN** the system rejects the command with HTTP 409 and the remaining cooldown time

### Requirement: Equipment State Confirmation
The system SHALL track both requested and confirmed equipment state, updating confirmed state when the device reports back via MQTT or polling.

#### Scenario: Tasmota reports state change
- **WHEN** MQTT worker receives `stat/{topic}/RESULT` with `{"POWER":"ON"}`
- **THEN** the system updates the equipment's `confirmed_state` to `{is_on: true}`, sets `last_confirmed_at`, and logs a "device_report" state change

#### Scenario: State confirmation timeout
- **WHEN** a command is sent but no device confirmation arrives within 30 seconds
- **THEN** the system marks the equipment state as "unconfirmed" and the state remains as last confirmed

#### Scenario: Power monitoring telemetry
- **WHEN** MQTT worker receives `tele/{topic}/SENSOR` with energy data
- **THEN** the system updates confirmed_state with `power_w`, `voltage_v`, `current_ma` and logs a power reading in the state log

### Requirement: Safety Interlocks
The system SHALL enforce safety rules that prevent dangerous equipment operating conditions, enforced server-side regardless of client.

#### Scenario: Max-on duration exceeded
- **WHEN** equipment has been ON longer than its `max_on_minutes` setting
- **THEN** the scheduler watchdog automatically sends an OFF command, logs the action with source "interlock", and creates an alert

#### Scenario: Conflict detection
- **WHEN** a command would turn ON equipment that has `conflicts_with` entries currently in ON state
- **THEN** the system rejects the command before dispatch and returns the conflicting equipment details

#### Scenario: Rapid cycling prevention
- **WHEN** equipment has been toggled more than 10 times in 5 minutes
- **THEN** the system rejects further commands for 5 minutes and logs a "rapid_cycling" interlock violation

### Requirement: Automation Engine Equipment Actions
The system SHALL dispatch equipment control commands as automation rule actions, enabling sensor-threshold-driven actuation.

#### Scenario: High temperature triggers exhaust fan ON
- **WHEN** an automation rule with `action: "relay_on"` evaluates true against a sensor reading
- **THEN** the system fires the alert AND dispatches the equipment command via `send_command_from_automation()` with source "automation"

#### Scenario: Low humidity triggers humidifier OFF
- **WHEN** an automation rule with `action: "relay_off"` and `action_params: {equipment_id: UUID}` triggers
- **THEN** the system sends the OFF command to the specified equipment, respecting interlocks

#### Scenario: Schedule-based equipment control
- **WHEN** an EnvironmentSchedule reaches its on_time or off_time
- **THEN** the scheduler dispatches the appropriate command to the linked equipment with source "schedule"

### Requirement: Equipment State History
The system SHALL maintain an audit trail of all equipment state changes with attribution, timestamps, and metadata.

#### Scenario: Query state history
- **WHEN** a user requests `GET /v1/equipment/{id}/history`
- **THEN** the system returns paginated state change records with action, source, timestamps, and power readings

#### Scenario: Filter history by source
- **WHEN** a user requests history with `?source=automation`
- **THEN** the system returns only state changes triggered by automation rules
