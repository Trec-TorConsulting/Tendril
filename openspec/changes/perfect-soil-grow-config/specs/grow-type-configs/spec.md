## ADDED Requirements

### Requirement: Soil Organic vs Synthetic Feeding Tracks
The system SHALL provide two complete, separate nutrient management tracks for soil: organic (living soil, amendments, compost tea, top dressing) and synthetic (liquid nutrients, pH adjustment). Each track SHALL have its own feeding schedule, pH management protocol, and stage-by-stage guidance.

#### Scenario: Organic soil grower views feeding schedule
- **WHEN** a soil grower selects the organic feeding track
- **THEN** the system provides: amendment-based feeding (top dress every 2-4 weeks with dry amendments), compost tea schedule (every 2 weeks in veg, weekly in flower), no pH adjustment needed (healthy living soil self-buffers), and plain water between tea applications

#### Scenario: Synthetic soil grower views feeding schedule
- **WHEN** a soil grower selects the synthetic feeding track
- **THEN** the system provides: liquid nutrient schedule by stage (feed every other watering), pH every watering to 6.0-6.5, alternate feed/water/feed pattern, and runoff pH/EC monitoring

### Requirement: Living Soil Biology Guide
The system SHALL provide living soil education including base soil recipe, amendment guide (kelp meal, bone meal, neem meal, glacial rock dust, gypsum, worm castings), cover crop planting, mulch layer benefits, no-till technique, and soil food web education (mycorrhizae, bacteria, fungi networks).

#### Scenario: Grower building living soil from scratch
- **WHEN** a grower wants to build a living soil mix
- **THEN** the system provides: base recipe (1/3 peat or coco, 1/3 compost/worm castings, 1/3 perlite/pumice), amendment per cubic foot table (1/2 cup each: kelp meal, neem meal, crustacean meal, 1 cup glacial rock dust, 1/2 cup gypsum), and notes soil should "cook" for 2-4 weeks before planting

### Requirement: Soil Wet/Dry Cycle Management
The system SHALL provide wet/dry cycle guidance as the fundamental soil skill, including watering indicators (pot weight, finger test, moisture meter), why overwatering is the #1 mistake, watering technique, and water volume per pot size.

#### Scenario: Soil grower's plant is drooping
- **WHEN** a soil grower reports drooping leaves
- **THEN** the system asks for diagnostic: check soil moisture (finger in top 2 inches). If wet: overwatering — let soil dry before next watering, improve drainage, reduce watering frequency. If dry: underwater — water thoroughly until 10-20% runoff, ensure even distribution

### Requirement: Soil Compost Tea and Top Dressing Protocol
The system SHALL provide compost tea brewing protocol (aerobic method: compost + molasses + air pump + 24-48h), application frequency/timing, and top dressing technique (amendment selection, quantity per pot size, layering, activation with water).

#### Scenario: Organic grower wants to boost flower production
- **WHEN** an organic soil grower enters early flower
- **THEN** the system recommends: top dress with high-phosphorus amendments (bone meal, bat guano, langbeinite), brew bloom-focused compost tea (high-P compost + molasses), and increase compost tea frequency to weekly

### Requirement: Soil-Specific Pest Management
The system SHALL provide pest identification and treatment specific to soil-dwelling pests including fungus gnats (BTI, sand layer, sticky traps), root aphids (systemic treatment, beneficial nematodes), and beneficial predator introductions (predatory mites, rove beetles).

#### Scenario: Tiny flies buzzing around soil surface
- **WHEN** a soil grower reports small flies near the soil
- **THEN** the system diagnoses fungus gnats, provides layered treatment: yellow sticky traps (immediate monitoring), Mosquito Bits/BTI granules on soil surface (kills larvae), sand or diatomaceous earth top layer (prevents egg laying), let soil dry more between waterings (larvae need moisture), and neem oil soil drench for severe infestations

### Requirement: Soil Stage-by-Stage Configuration
The system SHALL provide 12-stage grow configuration for soil with dual feeding schedules (organic AND synthetic tracks), wet/dry cycle guidance per stage, top dressing schedule for organic track, and pot sizing recommendations.

#### Scenario: Soil grower in vegetative stage
- **WHEN** a soil grow is in vegetative stage
- **THEN** the system provides: organic track (top dress with balanced NPK amendments, compost tea every 2 weeks, plain water between, no pH needed) AND synthetic track (feed every other watering at 50-75% strength, pH to 6.3, water volume ~25% of pot size, let top 2 inches dry between waterings)
