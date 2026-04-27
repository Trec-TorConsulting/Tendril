## ADDED Requirements
### Requirement: Nutrient Brand Feed Charts
The system SHALL provide pre-built feeding schedules for popular nutrient brands that the AI uses for brand-specific feeding advice.

#### Scenario: User selects nutrient brand for a grow
- **WHEN** a user assigns a nutrient brand and chart to their grow
- **THEN** the AI feeding advice context includes that brand's week-by-week dosing schedule

#### Scenario: AI generates brand-specific feeding advice
- **WHEN** the AI generates feeding advice for a grow with an assigned nutrient chart
- **THEN** the advice references specific products and ml/gal doses from the selected brand's chart
