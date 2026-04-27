## ADDED Requirements

### Requirement: Garden Plot Grid Designer
The system SHALL provide an interactive 2D grid layout editor for outdoor soil grows where users can visually design their garden beds, place plants, companion plants, sensors, and irrigation lines on a grid.

#### Scenario: Create garden plot grid
- **WHEN** a user creates an outdoor_soil grow and opens the Garden Plot tab
- **THEN** they can define grid dimensions (rows × cols), cell size, and orientation
- **AND** the grid is persisted and rendered as an interactive visual layout

#### Scenario: Place plants on grid
- **WHEN** a user clicks a grid cell and selects "Plant"
- **THEN** they can assign a strain/plant to that cell, creating a linked bucket record
- **AND** the cell displays the plant name and strain info

#### Scenario: Place companion plants on grid
- **WHEN** a user clicks a grid cell and selects "Companion"
- **THEN** they can choose from a companion plant database
- **AND** compatibility indicators show green/red borders for neighboring plants

#### Scenario: Place sensors on grid
- **WHEN** a user clicks a grid cell and selects "Sensor"
- **THEN** they can assign a registered device to that zone
- **AND** sensor readings are associated with nearby plants

#### Scenario: Mobile-friendly grid interaction
- **WHEN** a user accesses the plot designer on a mobile device
- **THEN** touch gestures (tap, pinch-zoom) work for cell selection and grid navigation

---

### Requirement: Soil Health Tracking
The system SHALL allow users to log soil tests, track soil health over time, and receive amendment recommendations.

#### Scenario: Log soil test results
- **WHEN** a user submits a soil test via `POST /v1/grows/{id}/soil-tests` with pH, N-P-K, organic matter %, CEC, and micronutrients
- **THEN** the test is stored with timestamp and source (lab, home kit, or sensor)

#### Scenario: View soil health trends
- **WHEN** a user opens the Soil Dashboard
- **THEN** they see charts showing pH, nitrogen, phosphorus, and potassium trends over all logged tests

#### Scenario: Soil amendment tracking
- **WHEN** a user logs a soil amendment (type, product, quantity, area, cost)
- **THEN** it appears on the amendment timeline and is factored into soil health analysis

---

### Requirement: Outdoor Intelligence Suite
The system SHALL provide weather integration, frost alerts, GDD tracking, sun mapping, and moon phase data for outdoor grows.

#### Scenario: Current weather and forecast
- **WHEN** a user views an outdoor grow with lat/lng set on the tent
- **THEN** they see current conditions and a 7-day forecast from OpenWeather API

#### Scenario: Growing Degree Days accumulation
- **WHEN** the scheduler runs daily for an active outdoor grow
- **THEN** it calculates GDD contribution as `max(0, (high + low) / 2 - base_temp)` and accumulates it
- **AND** the UI shows a progress bar of accumulated GDD vs. strain maturity target

#### Scenario: Frost alert notification
- **WHEN** the weather forecast shows temperatures below 32°F in the next 48 hours
- **THEN** the system sends a push notification warning the user

#### Scenario: Rain-based irrigation skip
- **WHEN** rainfall forecast exceeds 0.5" in the next 24 hours
- **THEN** watering reminder tasks are suppressed with a "Rain expected" note

#### Scenario: Moon phase calendar
- **WHEN** a user views the outdoor intelligence panel
- **THEN** they see the current moon phase and upcoming phases for planting guidance

#### Scenario: Manual rain gauge entry
- **WHEN** a user submits a manual rainfall reading
- **THEN** it supplements API weather data in the rain accumulator

---

### Requirement: Companion Planting System
The system SHALL provide a companion planting database with compatibility checking and recommendations.

#### Scenario: Check companion compatibility
- **WHEN** a user queries `GET /v1/companion-plants/check?plant=cannabis&neighbor=basil`
- **THEN** the system returns compatibility status (beneficial, harmful, neutral) with explanation

#### Scenario: Auto-suggest companions
- **WHEN** a user places a plant on the grid
- **THEN** the system suggests beneficial companion plants for adjacent cells

#### Scenario: Visual compatibility indicators
- **WHEN** the plot grid renders with plants and companions placed
- **THEN** cell borders show green for beneficial pairings and red for harmful pairings

---

### Requirement: Pest & Disease Field Scouting
The system SHALL provide a field scouting log for pest and disease observations with photo documentation and IPM tracking.

#### Scenario: Log pest observation
- **WHEN** a user creates a pest scout entry with type, species, severity, grid location, and optional photo
- **THEN** the observation is stored and visible on both the scout log and the plot grid

#### Scenario: Treatment tracking
- **WHEN** a user logs a treatment applied to a pest observation
- **THEN** the treatment type, product, and re-entry interval are recorded

#### Scenario: Beneficial insect tracking
- **WHEN** a user logs a beneficial insect observation (e.g., ladybugs, predator mites)
- **THEN** it is tracked separately and contributes to the IPM health score

---

### Requirement: Harvest Yield Tracking
The system SHALL track per-plant harvest yields with wet/dry/trim weights and provide analytics across seasons.

#### Scenario: Log per-plant harvest
- **WHEN** a user logs harvest data for a plant (wet weight, dry weight, trim weight, quality rating, trichome stage)
- **THEN** the yield is stored and associated with the specific bucket/plant

#### Scenario: Yield analytics
- **WHEN** a user views the harvest dashboard
- **THEN** they see total yield, average per plant, yield per square foot, and comparison to previous seasons

#### Scenario: Cost/ROI calculation
- **WHEN** a user has logged amendment costs and harvest yields
- **THEN** the system calculates input cost vs. output value for ROI analysis

---

### Requirement: Season Timeline
The system SHALL display a visual Gantt-style timeline showing grow stages, milestones, weather events, and GDD progression for the current season.

#### Scenario: View season timeline
- **WHEN** a user opens the Season Timeline tab
- **THEN** they see a horizontal timeline with stage bars (seedling → veg → flower → harvest)
- **AND** milestone markers, weather event overlays, and a GDD progression line

#### Scenario: Season comparison
- **WHEN** a user has completed multiple outdoor soil grows
- **THEN** they can compare timelines side-by-side to identify patterns and improvements

---

### Requirement: Irrigation Zone Management
The system SHALL support mapping irrigation zones to plot grid areas and tracking water usage.

#### Scenario: Define irrigation zones
- **WHEN** a user assigns irrigation zone labels to plot grid cells
- **THEN** the zones are visualized on the grid and linked to soil moisture sensors

#### Scenario: Water usage tracking
- **WHEN** sensor data or manual entries log water delivery per zone
- **THEN** the system tracks cumulative water usage and shows efficiency metrics

---

### Requirement: Outdoor-Specific Terminology
The system SHALL dynamically adapt UI labels and terminology based on grow type, replacing indoor-centric terms with outdoor-appropriate vocabulary.

#### Scenario: Outdoor soil terminology
- **WHEN** a grow has `grow_type === "outdoor_soil"`
- **THEN** "Bucket" displays as "Plant", "Tent" displays as "Garden", "Position" displays as "Plot Location", and "Add Bucket" displays as "Add Plant"

#### Scenario: Help text adaptation
- **WHEN** empty states or tooltips are shown in an outdoor soil grow
- **THEN** they reference outdoor concepts (soil, beds, weather) instead of indoor concepts (reservoirs, nutrient solution)
