# Tasks: Refactor Task Engine

## Implementation Checklist

### Backend — Database
- [x] Create Alembic migration adding `routine` (String(20), nullable) and `estimated_minutes` (Integer, nullable) to `tasks` table
- [x] Update Task model in `api/app/commercial/models.py` with new fields

### Backend — Task Generator Rewrite
- [x] Rewrite `TASK_TEMPLATES` with corrected intervals per grow type, routine assignments, estimated durations, and brief/detail descriptions
- [x] Add `AUTOMATION_SUPPRESSIONS` mapping for conditional task suppression
- [x] Add new task categories: `ipm_spray`, `equipment_check`, `meter_calibration`, `photo_documentation`, `nutrient_prep`, `deep_clean`, `carbon_filter`, `air_stone`, `light_check`
- [x] Update `generate_tasks_for_grow()` to assign timezone-aware due times based on routine (morning/evening/weekly)
- [x] Add logic to check tenant automation settings and suppress automated tasks
- [x] Update task description generation to use brief/detail format (brief in title context, detail in description)

### Backend — Schemas
- [x] Update task response schema to include `routine` and `estimated_minutes`

### Frontend
- [x] Add new category labels for new task types
- [x] Display routine badge (Morning Check, Evening, Weekly, etc.) on task cards
- [x] Display estimated duration badge on task cards
- [x] Group tasks by routine in list view when multiple tasks share the same routine + due date

### Testing
- [x] Unit tests for corrected task intervals per grow type
- [x] Unit test for automation suppression logic
- [x] Unit test for timezone-aware due time calculation
