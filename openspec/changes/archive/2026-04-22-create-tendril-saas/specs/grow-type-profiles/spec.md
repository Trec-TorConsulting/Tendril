## ADDED Requirements

### Requirement: Grow Type System
The system SHALL maintain a registry of grow types, each with a profile defining relevant sensors, UI fields, health check prompts, feeding defaults, automation capabilities, alert thresholds, and contextual guidance.

#### Scenario: Grow type selection
- **WHEN** a user creates a grow cycle
- **THEN** they select a grow type from: DWC, RDWC, NFT, Ebb & Flow, Drip/Top Feed, Aeroponics, Kratky, Coco Coir, Rockwool, Soil, Outdoor Soil, Outdoor Container
- **AND** the selected grow type determines which sensors, fields, questions, automations, and guidance are shown throughout the app

#### Scenario: Grow type defaults applied
- **WHEN** a grow type is selected
- **THEN** the system pre-fills target ranges (pH, EC, water temp, reservoir change interval, etc.) from the grow type profile
- **AND** the user can override any default

#### Scenario: Grow type changes UI
- **WHEN** a grow is active with a specific type
- **THEN** the dashboard, bucket detail, health checks, feeding schedules, alerts, and AI chat all adapt their terminology, questions, fields, and guidance to match the grow type

### Requirement: Grow Type Profiles Registry
The system SHALL define the following profiles as seed data. Each profile specifies what is relevant for that grow type.

---

#### Profile: DWC (Deep Water Culture)

**Category**: Hydroponic (active)
**Description**: Plants sit in net pots above aerated nutrient solution. Roots submerged 24/7.

**Terminology**:
- Container: "Bucket"
- Growing space: "Tent"
- Container contents: "Reservoir"
- Plant holder: "Net pot"
- Growing medium: "Hydroton / Clay pebbles"

**Sensor Kit**: Hydro Kit — pH probe, EC/TDS meter, water temp sensor, dissolved oxygen sensor, water level float sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, water temp, dissolved oxygen, water level, ambient temp, ambient humidity
**Primary Sensors** (dashboard gauges): pH, EC, water temp, water level
**Irrelevant Sensors**: soil moisture, soil temp, rain gauge

**Unique Fields**:
- Air stone status (on/off)
- Reservoir size (gallons/liters)
- Reservoir change interval (default: 7 days)
- Top feed / drip ring active (yes/no)

**pH Range**: 5.5 – 6.2
**EC Range**: Stage-dependent (seedling 0.4, veg 0.8-1.2, flower 1.2-1.8)
**Water Temp**: 62–70°F (17–21°C)

**Health Check Focus**:
- Root health (white = healthy, brown = root rot)
- Water clarity and color
- Air stone bubbling activity
- Water level (should cover roots but not stem)
- Dissolved oxygen levels
- Algae growth on reservoir/net pots

**Key Questions to Ask User**:
- When did you last change the reservoir?
- Are your air stones running?
- Any slime on the roots?
- Water color/clarity?

**Automations Available**:
- pH auto-dosing (pH up/down pumps)
- EC auto-dosing (nutrient concentrate pump)
- Water level top-off (float valve or pump)
- Reservoir change reminder (configurable days)
- Water temp alert (chiller/heater trigger)
- Dissolved oxygen alert

**Feeding Approach**: Continuous — nutrients always in reservoir. Weekly reservoir change with fresh mix.
**Nutrient Strength**: 50-75% of bottle recommendation (roots always submerged = constant uptake)

**Common Problems**: Root rot, pH swings, water temp too high, algae, pump failure
**AI Prompt Context**: "DWC grow — roots are submerged in aerated nutrient solution 24/7. Monitor root health, water clarity, dissolved oxygen, and reservoir freshness."

---

#### Profile: RDWC (Recirculating DWC)

**Category**: Hydroponic (active)
**Description**: Connected DWC buckets sharing a central reservoir via circulation pump. Uniform nutrient distribution.

**Terminology**:
- Container: "Site" / "Bucket"
- Growing space: "Tent" / "Room"
- Container contents: "Reservoir"
- Shared reservoir: "Control bucket" / "Epicenter"
- Plant holder: "Net pot"
- Growing medium: "Hydroton / Clay pebbles"

**Sensor Kit**: Hydro Kit + Flow — pH probe, EC/TDS meter, water temp sensor, dissolved oxygen sensor, water level float sensor, flow rate sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, water temp, dissolved oxygen, water level, flow rate, ambient temp, ambient humidity
**Primary Sensors**: pH, EC, water temp, flow rate
**Irrelevant Sensors**: soil moisture, soil temp, rain gauge

**Unique Fields**:
- Central reservoir size (gallons/liters)
- Number of connected sites
- Circulation pump status
- Return line flow rate
- Reservoir change interval (default: 10 days)

**pH Range**: 5.5 – 6.2
**EC Range**: Same as DWC
**Water Temp**: 62–70°F (17–21°C)

**Health Check Focus**:
- All DWC checks PLUS:
- Circulation flow (blockages, uneven distribution)
- Uniform pH/EC across all sites
- Return line clogs
- Central reservoir level

**Key Questions to Ask User**:
- Is the circulation pump running?
- Are all sites getting equal flow?
- Any blockage in return lines?
- When did you last clean the system?

**Automations Available**:
- All DWC automations PLUS:
- Circulation pump monitor (alert on failure)
- Flow rate deviation alert
- Cross-site pH/EC variance alert

**Feeding Approach**: Same as DWC but dosed at central reservoir
**Nutrient Strength**: 50-75%

**Common Problems**: All DWC problems + uneven distribution, line clogs, pump failure
**AI Prompt Context**: "RDWC grow — multiple connected DWC sites sharing a central reservoir via circulation pump. Check for uniform distribution, flow issues, and all standard DWC concerns."

---

#### Profile: NFT (Nutrient Film Technique)

**Category**: Hydroponic (active)
**Description**: Thin film of nutrient solution flows continuously over bare roots in a sloped channel.

**Terminology**:
- Container: "Channel" / "Gully"
- Growing space: "Tent" / "Room"
- Container contents: "Nutrient film"
- Plant holder: "Net pot" / "Cube"
- Growing medium: "Rockwool starter cube" (roots grow bare in channel)

**Sensor Kit**: Hydro Kit + Flow — pH probe, EC/TDS meter, water temp sensor, flow rate sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, water temp, flow rate, ambient temp, ambient humidity
**Primary Sensors**: pH, EC, flow rate
**Irrelevant Sensors**: water level (channels don't fill), dissolved oxygen (roots exposed to air), soil moisture, soil temp

**Unique Fields**:
- Channel count and length
- Flow rate (L/min target)
- Reservoir size
- Pump status
- Reservoir change interval (default: 7 days)

**pH Range**: 5.5 – 6.5
**EC Range**: Seedling 0.4, veg 0.8-1.4, flower 1.2-2.0

**Health Check Focus**:
- Root mat health (should be white, filling channel but not blocking flow)
- Flow uniformity across channels
- No dry spots (pump failure = roots dry in minutes)
- Channel slope and drainage
- Reservoir level

**Key Questions to Ask User**:
- Is the pump running continuously?
- Any channels running dry?
- Root mat blocking flow in any channel?
- Reservoir level adequate?

**Automations Available**:
- pH auto-dosing
- EC auto-dosing
- Flow rate monitoring (CRITICAL — pump failure kills plants fast)
- Pump failure alert (HIGH PRIORITY — minutes matter)
- Reservoir level alert

**Feeding Approach**: Continuous flow from reservoir. Same weekly change cycle.
**Nutrient Strength**: 50-75%

**Common Problems**: Pump failure (lethal fast), root blockage, uneven flow, salt buildup in channels
**AI Prompt Context**: "NFT grow — thin nutrient film flows over bare roots in channels. Pump failure is critical (roots dry in minutes). Monitor flow rate, root mat health, and channel drainage."

---

#### Profile: Ebb & Flow (Flood and Drain)

**Category**: Hydroponic (active)
**Description**: Grow tray periodically floods with nutrient solution then drains back to reservoir.

**Terminology**:
- Container: "Tray" / "Table"
- Growing space: "Tent" / "Room"
- Container contents: "Flood tray"
- Plant holder: "Pot" / "Net pot"
- Growing medium: "Hydroton" / "Rockwool" / "Perlite"

**Sensor Kit**: Hydro Kit — pH probe, EC/TDS meter, water temp sensor, water level float sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, water temp, ambient temp, ambient humidity
**Primary Sensors**: pH, EC, water temp
**Irrelevant Sensors**: dissolved oxygen, continuous water level (intermittent by design), soil moisture

**Unique Fields**:
- Flood frequency (times per day, default: 4-6)
- Flood duration (minutes, default: 15)
- Grow media type (hydroton, rockwool, perlite)
- Tray size
- Reservoir size
- Reservoir change interval (default: 7-10 days)

**pH Range**: 5.5 – 6.5
**EC Range**: Seedling 0.4, veg 0.8-1.4, flower 1.2-1.8

**Health Check Focus**:
- Media moisture between floods (not too dry, not waterlogged)
- Drain timing (should fully drain)
- Overflow protection working
- Root health in media
- Salt buildup on media surface

**Key Questions to Ask User**:
- Flood cycle timing (how often, how long)?
- Does the tray drain completely?
- Any overflow issues?
- Media staying moist between floods?

**Automations Available**:
- Flood cycle timer (schedule floods)
- pH auto-dosing
- EC auto-dosing
- Drain confirmation (water should return to reservoir)
- Overflow alert
- Adjust flood frequency by growth stage (more frequent in flower)

**Feeding Approach**: Intermittent — nutrients delivered during flood cycles
**Nutrient Strength**: 60-80%

**Common Problems**: Overflow, uneven drainage, salt buildup, timer failure, root rot if not draining
**AI Prompt Context**: "Ebb & Flow grow — tray floods periodically and drains back. Check flood/drain cycle timing, media moisture between floods, drainage completeness, and salt buildup."

---

#### Profile: Drip / Top Feed

**Category**: Hydroponic (active)
**Description**: Nutrient solution dripped onto growing media from above via emitters. Runoff collected or recirculated.

**Terminology**:
- Container: "Pot" / "Slab"
- Growing space: "Tent" / "Room"
- Container contents: "Media"
- Plant holder: "Pot"
- Growing medium: "Coco" / "Rockwool" / "Perlite" / "Hydroton"
- Drainage: "Runoff"

**Sensor Kit**: Media Kit — pH probe (input), EC/TDS meter (input), runoff pH probe, runoff EC meter, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, runoff pH, runoff EC, ambient temp, ambient humidity
**Primary Sensors**: pH (input), EC (input), runoff pH, runoff EC
**Irrelevant Sensors**: water level, dissolved oxygen, soil moisture (use runoff instead)

**Unique Fields**:
- Drip frequency (times per day)
- Drip duration (minutes per session)
- Grow media (coco, rockwool, perlite, hydroton)
- Recirculating or drain-to-waste
- Emitter count and GPH
- Reservoir size (if recirculating)
- Target runoff % (typically 10-20%)

**pH Range**: 5.5 – 6.5
**EC Range**: Seedling 0.4, veg 0.8-1.4, flower 1.2-2.0

**Health Check Focus**:
- Emitter blockage (all dripping evenly?)
- Runoff volume and pH/EC (indicates salt buildup)
- Media moisture level
- Input vs runoff EC delta (should be <0.3)

**Key Questions to Ask User**:
- All emitters flowing?
- What's your runoff percentage?
- Input EC vs runoff EC?
- Media drying out between feeds?

**Automations Available**:
- Drip timer (schedule feed events)
- pH auto-dosing (input reservoir)
- EC auto-dosing (input reservoir)
- Runoff EC alert (if delta from input > 0.3, flush needed)
- Emitter blockage detection (flow sensor per line)
- Stage-based frequency adjustment

**Feeding Approach**: Scheduled drip events. More frequent in flower. Runoff management critical.
**Nutrient Strength**: 75-100% (less contact time than DWC)

**Common Problems**: Clogged emitters, uneven distribution, salt buildup in media, over/under watering
**AI Prompt Context**: "Drip/Top Feed grow — nutrient solution delivered via drip emitters onto media. Monitor emitter flow, runoff pH/EC delta, media moisture, and feed frequency."

---

#### Profile: Aeroponics

**Category**: Hydroponic (active)
**Description**: Roots suspended in air and misted with fine nutrient spray at high pressure.

**Terminology**:
- Container: "Chamber" / "Root chamber"
- Growing space: "Tent" / "Room"
- Container contents: "Mist zone"
- Plant holder: "Net pot" / "Collar"
- Growing medium: "None" (bare roots in air)
- Key hardware: "Nozzle" / "Mister"

**Sensor Kit**: Aero Kit — pH probe, EC/TDS meter, water temp sensor, pressure sensor (PSI), ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, water temp, mist pressure, ambient temp, ambient humidity
**Primary Sensors**: pH, EC, mist pressure
**Irrelevant Sensors**: water level (roots in air), soil moisture, soil temp

**Unique Fields**:
- Mist cycle (on seconds / off seconds, e.g., 5s on / 3min off)
- Nozzle pressure (PSI)
- Nozzle count
- Reservoir size
- Reservoir change interval (default: 5-7 days)

**pH Range**: 5.5 – 6.2
**EC Range**: Seedling 0.3, veg 0.6-1.0, flower 1.0-1.6 (LOWER than other hydro — fine mist = high absorption)

**Health Check Focus**:
- Nozzle blockage (CRITICAL — roots dry in seconds)
- Mist coverage uniformity
- Root health (should be white, fuzzy, aerial)
- Reservoir cleanliness (fine nozzles clog easily)
- Pressure consistency

**Key Questions to Ask User**:
- All nozzles misting?
- Mist cycle timing?
- Any roots drying out?
- System pressure reading?

**Automations Available**:
- Mist cycle timer (high-frequency on/off)
- pH auto-dosing
- EC auto-dosing
- Pressure monitoring (alert on drop = nozzle clog or pump issue)
- Nozzle failure alert (CRITICAL — seconds matter)
- Reservoir temp monitoring

**Feeding Approach**: High-frequency mist cycles. Very low EC. Reservoir changes more frequent.
**Nutrient Strength**: 40-60% (fine mist = maximum absorption)

**Common Problems**: Nozzle clogs (lethal fast), pressure loss, root drying, biofilm, pump failure
**AI Prompt Context**: "Aeroponic grow — roots misted with fine nutrient spray. Nozzle/pump failure is critical (roots dry in seconds). Monitor pressure, nozzle coverage, root health, and mist timing."

---

#### Profile: Kratky (Passive Hydro)

**Category**: Hydroponic (passive)
**Description**: No pumps or electricity. Roots grow into static nutrient solution as water level drops, creating an air gap.

**Terminology**:
- Container: "Container" / "Jar" / "Tote"
- Growing space: "Tent" / "Shelf" / "Window"
- Container contents: "Nutrient solution"
- Plant holder: "Net pot"
- Growing medium: "Hydroton" / "Perlite"
- Key concept: "Air gap" (space between water surface and net pot)

**Sensor Kit**: Kratky Kit (minimal) — pH probe, EC/TDS meter, water level float sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, water temp, water level, ambient temp, ambient humidity
**Primary Sensors**: pH, water level
**Irrelevant Sensors**: dissolved oxygen (air gap provides O2), flow rate, pressure, soil moisture

**Unique Fields**:
- Container size (gallons/liters)
- Initial fill level
- Current water level (manual or sensor)
- Target air gap (inches/cm above water line)
- Refill strategy (top-off or full change)

**pH Range**: 5.5 – 6.5
**EC Range**: Seedling 0.5, veg 1.0-1.6, flower 1.4-2.0 (HIGHER — no reservoir changes, nutrients deplete)

**Health Check Focus**:
- Water level (must maintain air gap — NEVER refill to top)
- Root zone (upper roots should be dry/aerial, lower submerged)
- Algae growth (no circulation = higher risk)
- Water color (darkening = depletion)
- Container light-blocking (prevent algae)

**Key Questions to Ask User**:
- Current water level?
- How much air gap above the water line?
- Any algae visible?
- Water color still clear/light?

**Automations Available**:
- Water level monitoring (alert if too high — kills air roots)
- pH drift alert (no circulation = faster drift)
- EC depletion alert (nutrient consumption tracking)
- Refill reminder (based on consumption rate)
- NO auto-dosing recommended (disrupts Kratky equilibrium)

**Feeding Approach**: Set-and-forget. Initial nutrient mix at planting. Top-off with diluted solution only when water drops below critical level. Never refill to top.
**Nutrient Strength**: 75-100% (no changes, nutrients must last)

**Common Problems**: Refilling too high (drowns air roots), algae, pH drift, nutrient depletion
**AI Prompt Context**: "Kratky passive hydro — NO pumps. Plants rely on air gap above water line for oxygen. NEVER refill to top level. Monitor water level drop, pH drift, and algae. Minimal intervention is the design."

---

#### Profile: Coco Coir

**Category**: Soilless media
**Description**: Growing in coconut fiber (coco coir). Functions like hydro with media buffer. Hand-watered or drip-fed.

**Terminology**:
- Container: "Pot"
- Growing space: "Tent" / "Room"
- Container contents: "Media" / "Coco"
- Plant holder: "Pot" (direct plant)
- Growing medium: "Coco coir" / "Coco-perlite mix"
- Drainage: "Runoff"
- Key supplement: "CalMag"

**Sensor Kit**: Media Kit — pH probe (input), EC/TDS meter (input), runoff pH probe, runoff EC meter, soil moisture sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, runoff pH, runoff EC, media moisture, ambient temp, ambient humidity
**Primary Sensors**: pH (input), runoff EC, media moisture
**Irrelevant Sensors**: water level, dissolved oxygen, water temp (not submerged)

**Unique Fields**:
- Pot size
- Coco brand/type (buffered vs unbuffered)
- Perlite ratio (e.g., 70/30 coco/perlite)
- Watering method (hand, drip, bottom feed)
- Watering frequency (times per day)
- Target runoff % (10-20%)
- CalMag supplementation (yes/no — coco locks out calcium)

**pH Range**: 5.8 – 6.2
**EC Range**: Seedling 0.4, veg 0.8-1.4, flower 1.4-2.2

**Health Check Focus**:
- Runoff pH/EC vs input (salt buildup indicator)
- Media moisture consistency (should never fully dry)
- CalMag deficiency signs (yellow spots, brown edges)
- Root health at pot edges
- Frequency appropriateness (coco dries faster than soil)

**Key Questions to Ask User**:
- Watering frequency?
- Input pH and EC?
- Runoff pH and EC?
- Using CalMag supplement?
- Coco pre-buffered?

**Automations Available**:
- Watering schedule (timer-based drip or pump)
- pH auto-dosing (input reservoir)
- EC auto-dosing (input reservoir)
- Runoff EC alert (flush if delta > 0.3-0.5 from input)
- Dry-back monitoring (media moisture sensor)
- CalMag reminder (every watering for unbuffered coco)
- Frequency adjustment by growth stage

**Feeding Approach**: Feed every watering (no plain water for coco). Multiple times daily in flower. Target 10-20% runoff.
**Nutrient Strength**: 75-100%

**Common Problems**: CalMag deficiency (coco-specific), salt buildup, overwatering in seedling stage, drying out in flower
**AI Prompt Context**: "Coco coir grow — soilless media requiring nutrient solution every watering. CalMag supplementation critical (coco binds calcium). Monitor runoff EC vs input EC, never let coco dry fully, and increase watering frequency as plants grow."

---

#### Profile: Rockwool

**Category**: Soilless media
**Description**: Growing in mineral wool cubes/slabs. Excellent water retention and air ratio. Common in commercial grows.

**Terminology**:
- Container: "Slab" / "Cube" / "Block"
- Growing space: "Tent" / "Room" / "Greenhouse"
- Container contents: "Slab"
- Plant holder: "Cube" (starter cube placed on slab)
- Growing medium: "Rockwool" / "Stonewool"
- Drainage: "Runoff" / "Drain"
- Key concept: "Dry-back" (moisture loss between irrigations)

**Sensor Kit**: Media Kit + Scale — pH probe (input), EC/TDS meter (input), runoff pH probe, runoff EC meter, slab moisture sensor, ambient temp/humidity (DHT22)

**Relevant Sensors**: pH, EC/PPM, runoff pH, runoff EC, slab moisture/weight, ambient temp, ambient humidity
**Primary Sensors**: pH (input), EC (input), slab moisture
**Irrelevant Sensors**: water level, dissolved oxygen, soil temp

**Unique Fields**:
- Cube/slab size
- Watering method (drip, hand)
- Shots per day (number of irrigation events)
- Shot volume (mL per event)
- Target slab moisture % (dry-back strategy)
- Slab weight tracking (wet weight vs dry weight)

**pH Range**: 5.5 – 6.0 (rockwool naturally high pH — pre-soak to lower)
**EC Range**: Seedling 0.4, veg 0.8-1.4, flower 1.4-2.2

**Health Check Focus**:
- Slab moisture and dry-back % (crop steering)
- Runoff pH/EC
- Algae on exposed rockwool (cover with plastic)
- Root growth into slab (check edges)
- Shot timing and volume

**Key Questions to Ask User**:
- How many irrigation shots per day?
- Dry-back percentage overnight?
- Slab covered (algae prevention)?
- Pre-soaked rockwool before use?

**Automations Available**:
- Irrigation shot scheduling (precise timing)
- Dry-back monitoring and alerts
- Crop steering automation (generative vs vegetative via dry-back %)
- pH auto-dosing
- EC auto-dosing
- Runoff EC alert
- Shot volume adjustment by growth stage

**Feeding Approach**: Precision irrigation. Multiple small shots per day. Crop steering via dry-back percentage (high dry-back = generative/flower push, low dry-back = vegetative growth).
**Nutrient Strength**: 75-100%

**Common Problems**: pH too high if not pre-soaked, algae on exposed surfaces, overwatering, poor dry-back strategy
**AI Prompt Context**: "Rockwool grow — precision irrigation in mineral wool slabs. Crop steering via dry-back percentage is key. Monitor slab moisture, shot timing/volume, runoff pH/EC, and cover exposed rockwool to prevent algae."

---

#### Profile: Soil

**Category**: Traditional media
**Description**: Growing in organic or amended soil. Most forgiving medium. Slower nutrient uptake.

**Terminology**:
- Container: "Pot" / "Planter"
- Growing space: "Tent" / "Room" / "Garden"
- Container contents: "Soil"
- Plant holder: "Pot" (direct plant)
- Growing medium: "Soil" / "Super soil" / "Living soil"
- Feeding: "Watering" / "Feeding" / "Top dressing" (organic)
- Key concept: "Wet/dry cycle"

**Sensor Kit**: Soil Kit — soil moisture sensor, soil pH probe (optional), runoff pH probe, runoff EC meter, ambient temp/humidity (DHT22)

**Relevant Sensors**: soil moisture, soil pH (if available), runoff pH, runoff EC, ambient temp, ambient humidity
**Primary Sensors**: soil moisture, ambient temp, ambient humidity
**Irrelevant Sensors**: water temp, dissolved oxygen, water level, EC (unless feeding synthetic)

**Unique Fields**:
- Pot size
- Soil type (super soil, living soil, amended, peat-based)
- Organic or synthetic nutrients
- Watering method (hand, drip)
- Wet/dry cycle preference
- Compost tea schedule
- Top dress schedule (for organic)
- Beneficial microbe inoculation

**pH Range**: 6.0 – 7.0 (HIGHER than hydro)
**EC Range**: Organic: not measured (soil buffers). Synthetic: seedling 0.3, veg 0.6-1.0, flower 1.0-1.6

**Health Check Focus**:
- Soil moisture (wet/dry cycling is beneficial)
- Pot weight (lift test)
- Topsoil condition (compaction, salt crust, beneficial fungal growth)
- Pest presence (soil bugs — fungus gnats, etc.)
- Leaf color and texture (deficiency signs appear slower in soil)
- Root bound signs (roots circling pot bottom)

**Key Questions to Ask User**:
- Organic or synthetic nutrients?
- When did you last water?
- Pot weight (heavy or light)?
- Any bugs in the soil?
- Top dressed recently?
- Using mycorrhizae or beneficial microbes?

**Automations Available**:
- Watering schedule (less frequent than hydro — wait for dry-back)
- Soil moisture monitoring
- Watering reminder (based on soil moisture sensor)
- Top dress reminder (every 2-4 weeks for organic)
- Compost tea brew reminder
- Pest check reminder
- pH runoff alert (if measuring)
- NO pH auto-dosing (soil self-buffers)

**Feeding Approach**: Wet/dry cycle. Water when top inch is dry or pot feels light. Feed every other watering (synthetic) or rely on soil amendments (organic). Flush before harvest.
**Nutrient Strength**: 50-75% for synthetic. N/A for living soil.

**Common Problems**: Overwatering (#1 beginner mistake), fungus gnats, nutrient lockout from pH issues, root bound, slow deficiency detection
**AI Prompt Context**: "Soil grow — traditional media with natural buffering. Wet/dry cycle is important (do NOT keep constantly wet like hydro). Watch for overwatering, pest presence, and slower-developing deficiency signs. If organic/living soil, minimal intervention is correct."

---

#### Profile: Outdoor Soil

**Category**: Outdoor
**Description**: Plants grown directly in ground soil or raised beds outdoors. Weather-dependent.

**Terminology**:
- Container: "Plot" / "Bed" / "Site"
- Growing space: "Garden" / "Plot" / "Field" / "Greenhouse" / "Hot House"
- Container contents: "Ground soil"
- Plant holder: N/A (direct in ground)
- Growing medium: "Native soil" / "Amended soil"
- Feeding: "Amending" / "Top dressing" / "Watering"
- Key concept: "Photoperiod" (daylight hours trigger flowering)

**Sensor Kit**: Outdoor Kit — soil moisture sensor, soil temp sensor, ambient temp/humidity (DHT22). Weather data from Open-Meteo API (no hardware needed for temp/humidity/UV/rain/wind)

**Relevant Sensors**: ambient temp (from weather), humidity (from weather), UV index, soil moisture, soil temp
**Primary Sensors**: weather conditions, soil moisture
**Irrelevant Sensors**: pH (ground soil is hard to adjust), EC, water temp, dissolved oxygen, water level

**Unique Fields**:
- Plot size / raised bed dimensions
- Native soil type (clay, loam, sandy)
- Soil amendments added
- Sun exposure (full sun, partial shade)
- Companion planting (yes/no, what)
- Pest deterrent methods
- Irrigation method (hand, drip, sprinkler, rain-fed)
- Frost protection available (row cover, greenhouse, none)
- Photoperiod tracking (auto from lat/lon)

**pH Range**: 6.0 – 7.0 (hard to adjust in-ground — amend at planting)
**EC Range**: Not typically measured outdoors

**Health Check Focus**:
- Weather impact assessment (frost risk, heat stress, rain/mold, wind damage, UV burn)
- Pest/animal damage (deer, rabbits, caterpillars, aphids, spider mites)
- Sun exposure adequacy (min 6 hours direct)
- Soil condition and moisture
- Plant structure (staking, topping, training for wind resistance)
- Mold/mildew risk (humidity + poor airflow from weather)

**Key Questions to Ask User**:
- Recent weather events (storms, frost, heatwave)?
- Any pest or animal damage visible?
- Soil moisture level?
- Hours of direct sunlight?
- Any support structures in place?

**Automations Available**:
- Weather monitoring and alerts (from Open-Meteo)
- Frost warning (based on forecast)
- Watering reminder (based on weather + soil moisture — skip if rain expected)
- Photoperiod tracking (auto-calculate flower trigger from latitude)
- Pest check reminders (weekly)
- Harvest window estimation (based on strain + photoperiod + weather)
- Rain/mold alert (humidity + rain combo)
- Smart irrigation skip (don't water if rain >5mm expected in 24h)

**Feeding Approach**: Amend soil before planting. Top dress or liquid feed monthly. Rain provides most water. Supplement in dry periods only.
**Nutrient Strength**: Minimal synthetic input. Rely on soil biology.

**Common Problems**: Pests/animals, weather damage, light dep timing (flowering too early/late), mold in humid climates, theft
**AI Prompt Context**: "Outdoor soil grow — weather-dependent, in-ground or raised bed. Factor in current weather (temp, humidity, UV, rain, wind) when evaluating health. Watch for pest/animal damage, weather stress, photoperiod-triggered flowering, and mold risk in humid weather."

---

#### Profile: Outdoor Container

**Category**: Outdoor
**Description**: Plants in containers (fabric pots, plastic pots) outdoors. Combines container control with outdoor weather.

**Terminology**:
- Container: "Pot" / "Container" / "Fabric pot"
- Growing space: "Patio" / "Deck" / "Garden" / "Greenhouse" / "Hot House"
- Container contents: "Media" / "Soil" / "Coco"
- Plant holder: "Pot" (direct plant)
- Growing medium: Depends on media ("Soil", "Coco-perlite", etc.)
- Feeding: "Watering" / "Feeding"
- Key concept: "Mobility" (can move indoors for weather)

**Sensor Kit**: Outdoor Kit — soil moisture sensor, soil temp sensor, ambient temp/humidity (DHT22). Weather data from Open-Meteo API. Runoff pH/EC probes if using synthetic nutrients

**Relevant Sensors**: ambient temp (weather), humidity (weather), UV, soil moisture, runoff pH, runoff EC
**Primary Sensors**: weather conditions, soil moisture
**Irrelevant Sensors**: water temp, dissolved oxygen, water level

**Unique Fields**:
- All Outdoor Soil fields PLUS:
- Container size (gallons)
- Media type (soil, coco, perlite mix)
- Mobility (can move indoors for weather?)
- Saucer/tray (catching runoff?)

**pH Range**: Depends on media (soil: 6.0-7.0, coco: 5.8-6.2)
**EC Range**: Depends on media (soil: minimal, coco: standard hydro EC)

**Health Check Focus**:
- All Outdoor Soil checks PLUS:
- Root bound (containers limit root space)
- Container temp (black pots in sun = root cooking)
- Drainage adequacy
- Pot size vs plant size

**Key Questions to Ask User**:
- Outdoor Soil questions PLUS:
- Container color (dark pots overheat in sun)?
- Can you move plants indoors during bad weather?
- Root bound signs (roots out of drainage holes)?
- Container size adequate for plant?

**Automations Available**:
- All Outdoor Soil automations PLUS:
- Container temp alert (if using soil temp sensor)
- Root bound reminder (based on container size vs days in veg)
- Move-indoors alert (severe weather warning)
- Watering frequency higher than in-ground (containers dry faster)

**Feeding Approach**: Like soil/coco (depends on media) but more frequent watering than in-ground.
**Nutrient Strength**: Depends on media choice.

**Common Problems**: All outdoor soil + root bound, container overheating, faster drying, wind toppling
**AI Prompt Context**: "Outdoor container grow — potted plants outside, weather-dependent. Container-specific concerns include root binding, pot overheating in direct sun, and faster drying than in-ground. Factor in weather data for health assessment."

---

### Requirement: Grow-Type-Aware UI Adaptation
The system SHALL dynamically show or hide UI elements, fields, questions, and guidance based on the active grow type.

#### Scenario: Sensor dashboard adaptation
- **WHEN** the dashboard displays sensor gauges for a bucket
- **THEN** only sensors marked as "relevant" in the grow type profile are shown (e.g., no water level gauge for NFT, no dissolved oxygen for Coco)

#### Scenario: Bucket creation fields
- **WHEN** a user creates a bucket for a grow with a specific type
- **THEN** the form shows only fields relevant to that grow type (e.g., reservoir size for DWC, pot size for soil, channel position for NFT)

#### Scenario: Contextual help text
- **WHEN** a user views any input field or sensor reading
- **THEN** tooltips and help text are tailored to the grow type (e.g., pH help for DWC says "Hydro pH range 5.5-6.2" while soil says "Soil pH range 6.0-7.0")

#### Scenario: Health check form
- **WHEN** a user submits manual health check observations
- **THEN** the form shows questions relevant to the grow type (e.g., DWC asks about root color and air stones; soil asks about soil moisture and bugs)

### Requirement: Grow-Type-Aware AI Context
The system SHALL inject the grow type profile's AI prompt context into all AI interactions (health checks, chat, coach tips, insights).

#### Scenario: Health check prompt injection
- **WHEN** the AI performs a health check for a tent
- **THEN** the system prompt includes the grow type's AI prompt context string so the AI knows what to look for and what advice is appropriate

#### Scenario: Chat context
- **WHEN** a user asks a question in AI chat
- **THEN** the system includes the grow type profile context so answers are relevant (e.g., don't suggest checking air stones for a soil grow)

#### Scenario: Coach tips
- **WHEN** the AI generates a coach tip
- **THEN** the tip is relevant to the grow type (e.g., DWC: "Check your dissolved oxygen levels" vs Soil: "Time to check if the top inch of soil is dry")

### Requirement: Grow-Type-Aware Feeding Defaults
The system SHALL suggest feeding schedules, nutrient strengths, and watering patterns based on the grow type.

#### Scenario: Feeding schedule suggestion
- **WHEN** a user assigns a feeding schedule to a bucket
- **THEN** the system adjusts nutrient strength recommendations based on grow type (e.g., 50-75% for DWC, 75-100% for coco, N/A for living soil)

#### Scenario: Watering pattern
- **WHEN** the system generates watering reminders or irrigation schedules
- **THEN** the frequency and pattern match the grow type (e.g., continuous for DWC, wet/dry cycle for soil, multiple daily shots for rockwool, mist cycles for aeroponics)

### Requirement: Grow-Type-Aware Alerts and Thresholds
The system SHALL use grow-type-specific default thresholds for sensor alerts.

#### Scenario: pH alert thresholds
- **WHEN** a bucket's pH alert is configured with default thresholds
- **THEN** the defaults come from the grow type profile (5.5-6.2 for DWC, 6.0-7.0 for soil, 5.8-6.2 for coco)

#### Scenario: Critical timing alerts
- **WHEN** a grow type has time-critical failures (NFT pump, aero nozzle)
- **THEN** those alerts are marked as CRITICAL priority with immediate notification on all channels

#### Scenario: Irrelevant alerts suppressed
- **WHEN** a sensor type is marked "irrelevant" for a grow type
- **THEN** no alerts are generated for that sensor type and it does not appear in alert configuration

### Requirement: Grow-Type-Aware Terminology
The system SHALL adapt all UI labels, tooltips, headings, notifications, and AI responses to use the correct terminology for the active grow type.

#### Scenario: Container label adaptation
- **WHEN** a user views their grow
- **THEN** the generic "bucket" concept is labeled according to the grow type's terminology (e.g., "Bucket" for DWC, "Channel" for NFT, "Pot" for Coco/Soil, "Plot" for Outdoor Soil, "Chamber" for Aeroponics, "Tray" for Ebb & Flow, "Slab" for Rockwool)

#### Scenario: Growing space label adaptation
- **WHEN** a user views the tent/zone/garden
- **THEN** the growing space is labeled per grow type (e.g., "Tent" for indoor hydro, "Garden" for outdoor soil, "Patio" for outdoor container, "Room" for commercial setups)

#### Scenario: AI uses correct terminology
- **WHEN** the AI generates health checks, coach tips, or chat responses
- **THEN** it uses the grow type's terminology (e.g., DWC: "Check your bucket's reservoir"; Outdoor Soil: "Check your plot's soil moisture"; NFT: "Check your channel's flow rate")

#### Scenario: Notifications use correct terminology
- **WHEN** a notification or alert fires
- **THEN** the message uses grow-type terms (e.g., "Bucket #3 pH low" for DWC vs "Pot #3 pH low" for Coco vs "Channel #3 flow stopped" for NFT)

### Requirement: Sensor Kit Per Grow Type
The system SHALL define a sensor kit configuration per grow type, specifying which physical sensors are included in that kit SKU. One sensor kit is paired per plant/bucket/site.

#### Scenario: Kit pairing
- **WHEN** a user pairs a sensor kit via QR code
- **THEN** the system identifies the kit type and validates it matches the grow type's expected sensor set

#### Scenario: Kit SKU variants
- **WHEN** sensor kits are sold
- **THEN** each grow type category maps to a kit variant:
  - **Hydro Kit**: pH, EC/TDS, water temp, dissolved oxygen, water level, ambient temp/humidity
  - **Hydro Kit + Flow**: Hydro Kit + flow rate sensor (for RDWC, NFT)
  - **Aero Kit**: pH, EC/TDS, water temp, pressure sensor, ambient temp/humidity
  - **Media Kit**: pH (input), EC/TDS (input), runoff pH, runoff EC, soil/media moisture, ambient temp/humidity
  - **Soil Kit**: soil moisture, soil pH (optional), runoff pH, runoff EC, ambient temp/humidity
  - **Outdoor Kit**: soil moisture, soil temp, ambient temp/humidity (weather from API)
  - **Kratky Kit**: pH, EC/TDS, water level, ambient temp/humidity (minimal — passive system)

#### Scenario: Sensor-per-plant model
- **WHEN** a user has multiple plants/buckets/sites
- **THEN** each plant gets its own sensor kit paired to its bucket, enabling per-plant monitoring

### Requirement: Custom Grow Types
The system SHALL allow users to create custom grow types based on an existing profile template (Pro and Commercial tiers).

#### Scenario: Create custom type
- **WHEN** a Pro or Commercial tier user creates a custom grow type
- **THEN** they select a base profile to fork (e.g., "Based on DWC"), give it a name (e.g., "Hempy Bucket"), and can customize: terminology, relevant sensors, pH/EC ranges, unique fields, health check questions, AI prompt context, available automations, and feeding defaults

#### Scenario: Custom type validation
- **WHEN** a user saves a custom grow type
- **THEN** the system validates that at least one sensor is marked relevant, pH range is valid (min < max), and the AI prompt context is not empty

#### Scenario: Share custom type
- **WHEN** a user creates a useful custom grow type
- **THEN** they can optionally submit it for inclusion in the global profile registry (reviewed by admin)

#### Scenario: Tier gating
- **WHEN** a Seedling or Grower tier user attempts to create a custom grow type
- **THEN** the system returns 403 with an upgrade prompt
