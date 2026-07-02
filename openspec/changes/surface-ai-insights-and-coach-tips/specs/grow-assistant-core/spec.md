## ADDED Requirements

### Requirement: Dashboard Coach Tip Surfacing
The system SHALL surface an AI coach tip for the selected grow on the main dashboard home, using the existing coach-tip generation and aggressive caching to avoid redundant LLM calls.

#### Scenario: Coach tip shown on dashboard
- **WHEN** a user opens the dashboard home with a selected grow
- **THEN** the system displays an AI coach tip relevant to the grow's current stage and latest sensor readings
- **AND** shows how recently the tip was generated

#### Scenario: Cached coach tip served without LLM call
- **WHEN** a coach tip for the grow was generated within its cache TTL
- **THEN** the system returns the cached tip without invoking any LLM provider

#### Scenario: Manual refresh bypasses cache
- **WHEN** the user requests a refresh of the coach tip
- **THEN** the system regenerates the tip (Ollama first, Gemini fallback) and updates the cache

### Requirement: Dashboard AI Insights Surfacing
The system SHALL surface AI insights (`harvest_predict`, `nutrient_advice`, `anomaly_scan`) on the main dashboard, gated by the grow's current stage and available data.

#### Scenario: Harvest prediction gated by stage
- **WHEN** the selected grow is in a flowering, ripening, or harvesting stage
- **THEN** the system displays a harvest prediction insight
- **AND** hides the harvest prediction insight in earlier stages

#### Scenario: Nutrient advice available in growth stages
- **WHEN** the selected grow is in an active growth stage
- **THEN** the system displays nutrient advice for the grow

#### Scenario: Anomaly scan requires recent data
- **WHEN** recent sensor readings exist for the grow
- **THEN** the system displays an anomaly scan insight
- **AND** shows an informative empty state when no recent readings exist

### Requirement: Aggressive Insight Caching with Provider Fallback
The system SHALL cache insight and coach-tip results server-side keyed by grow, insight type, and input, and SHALL prefer a local provider (Ollama) with fallback to a hosted provider (Gemini) only on cache miss.

#### Scenario: Cache miss triggers provider chain
- **WHEN** no fresh cached result exists for a requested insight
- **THEN** the system attempts generation with the local provider first
- **AND** falls back to the hosted provider if the local provider is unavailable
- **AND** stores the successful result in the cache with its generation timestamp
