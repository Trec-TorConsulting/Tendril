## ADDED Requirements

### Requirement: Expense Tracking Per Grow
The system SHALL allow growers to log expenses per grow with category, amount, date, and optional notes. Categories SHALL include nutrients, electricity, water, equipment, labor, rent, supplies, and other.

#### Scenario: Grower logs nutrient purchase
- **WHEN** a grower buys nutrients for a specific grow
- **THEN** the grower can log: category (nutrients), product name, amount ($45.00), date, and the system adds it to the grow's total cost

### Requirement: ROI Dashboard
The system SHALL calculate and display cost-per-gram (total expenses / dry yield), ROI percentage, cost breakdown by category, and grow-over-grow comparison.

#### Scenario: Grower views ROI after harvest
- **WHEN** a grow is harvested and expenses are logged
- **THEN** the dashboard shows: total cost ($350), total dry yield (400g), cost-per-gram ($0.88/g), estimated value at market price, ROI percentage, and category breakdown chart
