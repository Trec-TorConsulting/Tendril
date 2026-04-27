# Proposal: Dynamic Task Engine — AI-Driven, Health-Reactive Tasks

## Change ID
`add-dynamic-task-engine`

## Summary
Transform the task system from static template-based generation into a dynamic, AI-driven engine that creates actionable tasks from health evaluations, alerts, sensor anomalies, and grow events. Every AI observation should translate into a concrete next step the grower can check off.

## Core Philosophy: Quality Over Quantity

**The guiding principle for all Tendril AI and task generation is quality over quantity.** The goal is to grow the best possible buds — not the biggest. Every recommendation, health check, and auto-generated task should prioritize:

- **Terpene preservation** over maximum yield (e.g., lower temps in late flower)
- **Proper flush timing** over extended feeding (clean, smooth smoke > extra grams)
- **Trichome maturity** over speed (wait for the right amber ratio)
- **Stress reduction** over aggressive training (healthy plants produce better quality)
- **Optimal harvest windows** over early chops (patience = potency)
- **Environment dialing** for resin production (VPD, light spectrum, temp swings)

This philosophy must be embedded in all AI prompts, health evaluations, and task descriptions.

## Motivation
Currently, auto-tasks are generated from a static template list every 6 hours (flush & fill, pH check, etc.). These are useful but miss the most valuable kind of task: **reactive tasks based on what the AI actually sees happening.** When a health check finds yellowing leaves, the user should get a concrete task like "Apply 2ml/gal CalMag to reservoir — nitrogen deficiency detected." When an alert fires for low dissolved oxygen, a task should appear: "Check air pump & air stone — DO dropped below 4ppm."

## Integration Points

### 1. Health Evaluation → Tasks (Primary)
After every scheduled health check (Gemini, every 12h):
- Parse `issues[]` and `actions[]` from the eval response
- Create one task per action with `source: "ai"`, `category: "health_response"`
- Link to grow_cycle_id, include the specific issue in the description
- Priority derived from health score (score < 50 → urgent, < 70 → high, < 85 → medium, else low)
- Deduplicate: don't create duplicate tasks if an unresolved task for the same issue category already exists

### 2. Alert → Urgent Tasks
When automation rules or critical grow-type alerts fire:
- Create immediate task with `source: "auto"`, `category: "alert_response"`
- Priority: urgent for critical alerts, high for warnings
- Include sensor reading and threshold in the task description
- Due date: now (critical) or +1h (warning)

### 3. Sensor Anomaly → Investigation Tasks
When sensor trends show concerning patterns:
- pH drift > 0.8 over 24h → "Investigate pH instability"
- EC rising while no feeding logged → "Check for salt buildup — flush may be needed"
- Dissolved oxygen declining trend → "Inspect air pump and air stone"
- Water level dropping > 5%/day → "Check for leaks or excessive transpiration"

### 4. Stage Transition → Preparation Tasks
When grow stage changes:
- vegetative → flowering: "Switch light to 12/12", "Adjust nutrients to bloom formula"
- flowering → late_flower: "Begin monitoring trichomes daily", "Consider lowering temps for terpene preservation"
- late_flower → flush: "Begin plain water flush", "Prepare harvest tools and drying space"

### 5. Journal Event → Follow-up Tasks
When journal entries are logged:
- Feeding: 24h follow-up "Verify pH/EC stability after feeding"
- Training (LST/HST): 3-day follow-up "Check recovery from training"
- Transplant: 48h follow-up "Monitor for transplant shock"

## Quality-Driven Task Examples

Instead of generic tasks, the AI should produce quality-focused tasks like:
- "Lower room temp to 68°F for final 2 weeks — preserves myrcene and linalool terpenes"
- "Extend flush by 2 more days — runoff EC still at 0.8, target < 0.3 for clean smoke"
- "Check trichomes with loupe — aim for 20-30% amber for peak potency on this indica"
- "Reduce light intensity 10% in final week — prevents terpene burn-off"
- "Maintain 50% humidity for dense, resinous buds — avoid the temptation to push growth"

## Non-Goals
- AI chat tool-calling to create tasks (future work)
- User-defined custom task templates (future work)
- Mobile push notifications for tasks (future work)
