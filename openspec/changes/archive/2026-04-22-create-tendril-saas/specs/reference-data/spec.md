## ADDED Requirements

### Requirement: Strain Database Integration
The system SHALL integrate with external strain databases to provide autocomplete, genetics info, and terpene profiles when users select or create strains.

#### Scenario: Strain autocomplete
- **WHEN** a user types a strain name in the strain selector (bucket creation, grow setup)
- **THEN** the system searches the local strain cache and returns matching results with genetics (indica/sativa/hybrid %), lineage, and common terpene profiles

#### Scenario: Otreeba API sync
- **WHEN** the scheduler runs daily (or on first startup)
- **THEN** the system fetches updated strain data from the Otreeba Open Cannabis Data API and caches it locally in a `reference_strains` table

#### Scenario: Strain detail enrichment
- **WHEN** a user selects a strain from the autocomplete
- **THEN** the system displays: strain name, genetics ratio, lineage (parent strains), dominant terpenes, typical effects, average flowering time, and difficulty rating (if available)

#### Scenario: Custom strain
- **WHEN** a user creates a strain not found in the reference database
- **THEN** the custom strain is saved to the tenant's strains table with user-provided details and marked as "user-created"

#### Scenario: Community strain contribution
- **WHEN** a user grows a custom strain and records yield/quality data
- **THEN** they can optionally submit the strain (name, genetics, grow notes) for inclusion in the community database (reviewed by admin)

### Requirement: Nutrient Product Barcode Scanning
The system SHALL support barcode scanning for nutrient product lookup via the Open Food Facts API.

#### Scenario: Scan nutrient bottle
- **WHEN** a user scans a barcode on a nutrient bottle using the PWA camera
- **THEN** the system queries Open Food Facts API with the UPC/EAN code and returns the product name, brand, and any available NPK/composition data

#### Scenario: Product not found
- **WHEN** a barcode scan returns no result from Open Food Facts
- **THEN** the user can manually enter the product name and brand, and optionally contribute the barcode to the database

#### Scenario: Nutrient product library
- **WHEN** a user has previously scanned or entered nutrient products
- **THEN** the products are saved to a `nutrient_products` table for reuse across grows without re-scanning

### Requirement: Reference Data Seed Library
The system SHALL ship with curated seed data for common grow terminology and reference lists.

#### Scenario: Grow media types
- **WHEN** a user selects a grow media
- **THEN** they can choose from a pre-populated list: Hydroton/Clay Pebbles, Rockwool, Coco Coir, Perlite, Vermiculite, Peat Moss, Super Soil, Living Soil, LECA, Mapito, Oasis Cubes, Growstones, Rice Hulls, Pumice

#### Scenario: Growth stages
- **WHEN** the system tracks growth stages
- **THEN** it uses the standard progression: Germinating → Seedling → Early Veg → Late Veg → Pre-Flower → Early Flower → Mid Flower → Late Flower → Harvest Ready → Drying → Curing

#### Scenario: Nutrient brands and lines
- **WHEN** a user selects a nutrient line for feeding schedules
- **THEN** they can choose from pre-populated brands: General Hydroponics (Flora series, FloraNova, MaxiGro/Bloom), Fox Farm (Trio, Dirty Dozen), Advanced Nutrients (pH Perfect, Sensi), Botanicare (Pure Blend, Kind), Canna (Coco, Aqua, Terra), Athena (Pro Line, Cleanse), Jack's Nutrients (321), Dyna-Gro (Foliage-Pro, Bloom)

#### Scenario: Terpene database
- **WHEN** the system displays terpene profiles for strains
- **THEN** it references a curated list of ~20 terpenes with: name, aroma description, common effects, boiling point, and which strains commonly express it

#### Scenario: Light types
- **WHEN** a user configures tent lighting
- **THEN** they can choose from: LED (Full Spectrum, Quantum Board, COB, Bar), HPS (High Pressure Sodium), MH (Metal Halide), CMH/LEC (Ceramic Metal Halide), CFL, T5 Fluorescent, Sunlight (outdoor) — each with typical PPFD ranges and wattage recommendations per sq ft
