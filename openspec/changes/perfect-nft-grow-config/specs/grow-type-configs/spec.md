## ADDED Requirements

### Requirement: NFT Channel Engineering Guide
The system SHALL provide channel engineering guidance including slope angle specifications (1:30 to 1:40), channel width by plant size, material selection (PVC, corrugated, commercial NFT rail), channel length limits based on salt accumulation, and optimal plant spacing per channel.

#### Scenario: Grower designs an NFT channel layout
- **WHEN** a grower is planning a 4-channel NFT setup for a 4x4 tent
- **THEN** the system provides: recommended channel length (4-6 feet max), slope of 1:30 (1 inch drop per 30 inches), 4-inch wide channels for cannabis, plant spacing of 8-12 inches, and return-to-reservoir plumbing guidance

### Requirement: NFT Flow Rate Management
The system SHALL define flow rate targets per channel (1-2 L/min for a thin 2-4mm nutrient film), pump sizing for multi-channel systems, flow uniformity verification procedures, and per-stage flow rate adjustments as root mass increases.

#### Scenario: Root mass restricts flow in late veg
- **WHEN** a grower's NFT channels show reduced flow rate due to root growth
- **THEN** the system alerts with guidance: verify flow at each channel outlet, increase pump output if available, consider gentle root trimming if flow drops below 50% of target, and notes that this is the most common NFT challenge

### Requirement: NFT Pump Failure Protocol
The system SHALL define pump failure as the highest severity event for NFT systems, with guidance that roots begin drying within 2-5 minutes of flow stoppage. The protocol SHALL include backup pump requirements, battery backup recommendations, alarm system integration, and maximum response time before plant damage.

#### Scenario: NFT pump stops running
- **WHEN** flow sensors detect zero flow in an NFT system
- **THEN** the system triggers an immediate `critical` alert: "NFT PUMP FAILURE — roots drying in minutes. Switch to backup pump immediately. If no backup, manually pour nutrient solution over roots while troubleshooting."

### Requirement: NFT Salt Accumulation Management
The system SHALL provide guidance on nutrient salt accumulation along NFT channel length, including EC gradient monitoring (inlet vs outlet), channel length limits, periodic flush schedules, and alternating flow direction techniques.

#### Scenario: EC at channel outlet significantly higher than inlet
- **WHEN** runoff EC at the end of an NFT channel measures >30% higher than inlet EC
- **THEN** the system recommends: reduce channel length or add midpoint inlets, increase flow rate, schedule plain water flush, and consider bi-directional flow timer

### Requirement: NFT Root Mat Management
The system SHALL provide root mat monitoring and management guidance specific to NFT, including signs of flow blockage, root training techniques, trimming guidance, and channel cleaning protocol between grows.

#### Scenario: NFT grower notices water pooling in mid-channel
- **WHEN** water pools visibly in the middle of an NFT channel instead of flowing evenly
- **THEN** the system diagnoses root mat blockage, provides: carefully lift channel cover to inspect, gently redirect root mass away from flow path, consider trimming if severe, increase flow rate, and notes this is normal in late veg/flower and requires ongoing monitoring

### Requirement: NFT Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration specific to NFT including rockwool cube propagation phase, channel placement timing, per-stage flow rate targets, and channel cleaning at grow end.

#### Scenario: NFT grower transitions seedlings to channels
- **WHEN** NFT seedlings in rockwool cubes develop roots extending 2-3 inches below the cube
- **THEN** the system provides channel placement instructions: set cube in channel with roots touching the nutrient film, ensure cube bottom contacts the flow, verify flow reaches all new transplants, and begin monitoring root extension into channel
