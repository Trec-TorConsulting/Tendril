## ADDED Requirements

### Requirement: Grow Diary Timeline
The system SHALL provide a week-by-week diary view for each bucket, aggregating sensor averages, journal entries, photos, and milestones into a vertical timeline.

#### Scenario: View diary
- **WHEN** a user opens the diary view for a bucket
- **THEN** a chronological timeline is displayed with weekly summaries including sensor averages, photos, journal entries, and milestone badges

#### Scenario: Add diary note
- **WHEN** a user adds a note or photo to a specific week in the diary
- **THEN** the entry is stored and appears in the timeline

---

### Requirement: Strain Library
The system SHALL maintain a searchable library of plant strains with metadata (breeder, genetics, flowering time, expected yield, THC/CBD percentages) that can be linked to buckets.

#### Scenario: Create strain
- **WHEN** a user creates a strain entry with name, breeder, and growing characteristics
- **THEN** the strain is stored and available in the bucket strain picker

#### Scenario: Auto-populate from strain
- **WHEN** a user selects a strain from the library when creating/editing a bucket
- **THEN** the strain's flowering time and expected yield are auto-populated into the bucket settings

#### Scenario: Strain grow history
- **WHEN** a user views a strain's details
- **THEN** all buckets (current and past) that used this strain are listed with their outcomes

---

### Requirement: Growth Stage Auto-Advance Suggestions
The system SHALL analyze sensor patterns and elapsed days to suggest growth stage transitions, displayed as dismissable notifications.

#### Scenario: Stage transition suggestion
- **WHEN** a bucket has been in its current stage for the expected duration
- **THEN** a suggestion notification is displayed: "Advance to [next stage]?"

#### Scenario: Auto-advance disabled
- **WHEN** auto-advance suggestions are turned off in tent settings
- **THEN** no stage transition suggestions are generated

---

### Requirement: Feeding Schedule Templates
The system SHALL support feeding schedule templates that define weekly nutrient doses per growth stage for common nutrient lines, and display the current week's recommended feeding for each bucket.

#### Scenario: Assign schedule to bucket
- **WHEN** a feeding schedule is assigned to a bucket
- **THEN** the bucket detail view shows the recommended nutrient amounts for the current week

#### Scenario: Built-in templates
- **WHEN** a user browses feeding schedules
- **THEN** pre-built templates for General Hydroponics Flora, Fox Farm, and Advanced Nutrients are available
