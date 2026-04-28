## ADDED Requirements

### Requirement: Photo-Based Plant Diagnosis
The system SHALL accept a photo of a plant and return an AI-generated diagnosis including identified issues, confidence scores, severity levels, and grow-type-specific treatment recommendations.

#### Scenario: Beginner grower sees yellow leaves
- **WHEN** a grower uploads a photo of yellowing lower leaves on a DWC plant
- **THEN** the system returns: "Nitrogen deficiency (85% confidence), Severity: Moderate. In DWC: check pH (should be 5.5-6.5 for nitrogen uptake), increase nitrogen in nutrient solution by 25%, check root health for signs of root rot which can block nutrient uptake."

### Requirement: Plant Health Photo Log
The system SHALL maintain a timestamped log of diagnosed photos per grow, enabling growers to track plant health progression over time.

#### Scenario: Grower reviews plant health timeline
- **WHEN** a grower views the health photo log for a grow
- **THEN** the system displays a chronological timeline of photos with their diagnoses, showing how issues developed, were treated, and resolved

### Requirement: Treatment Recommendations Database
The system SHALL provide a structured database of cannabis-specific issues (deficiencies, pests, diseases) with symptoms, causes, grow-type-specific treatments, and prevention guidance.

#### Scenario: AI diagnosis links to treatment database
- **WHEN** the AI identifies powdery mildew in a photo
- **THEN** the diagnosis includes a link to the powdery mildew entry with: detailed symptoms, environmental causes (high humidity + poor airflow), treatment options (potassium bicarbonate spray, neem oil, defoliation), and prevention (VPD management, airflow, defoliation)
