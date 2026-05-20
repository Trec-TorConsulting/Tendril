## 1. Tab Consolidation Design
- [x] 1.1 Define final tab list and groupings (target: 8-9 tabs for hydro, +1 "Field" for outdoor)
- [x] 1.2 Design sub-navigation within merged tabs (e.g., Activity tab has "Timeline" and "Readings" sub-views)
- [x] 1.3 Decide tab ordering (most-used first)

## 2. Activity Tab (Sensors + Journal merge)
- [x] 2.1 Create unified `activity-tab.tsx` component
- [x] 2.2 Implement sub-tabs: "Timeline" (journal entries) and "Readings" (sensor charts)
- [x] 2.3 Existing filter/chart functionality preserved via sub-components
- [x] 2.4 Remove standalone sensors/journal tabs from page.tsx (kept as sub-components)

## 3. Nutrition & Yield Tab (Feeding + Harvest merge)
- [x] 3.1 Create `nutrition-yield-tab.tsx` component
- [x] 3.2 Sub-tab: "Feeding" (current feeding-tab content)
- [x] 3.3 Sub-tab: "Harvest & Yields" (current harvest content)
- [x] 3.4 Remove standalone feeding and harvest tabs from page.tsx

## 4. Health & Photos Tab merge
- [x] 4.1 Create `health-photos-tab.tsx` component
- [x] 4.2 Sub-tab: "Health" (AI checks, issue log)
- [x] 4.3 Sub-tab: "Photos" (photo gallery)
- [x] 4.4 Remove standalone health and photos tabs from page.tsx

## 5. Outdoor Field Tab (consolidate outdoor-only tabs)
- [x] 5.1 Create `field-tab.tsx` for outdoor grows only
- [x] 5.2 Sub-tabs: Plot/Containers, Soil/Runoff, Field Scout, Yields, Intelligence, Irrigation, Season
- [x] 5.3 Only shown when grow_type is outdoor
- [x] 5.4 Removed 6+ standalone outdoor tabs from page.tsx

## 6. Tab Badges
- [x] 6.1 Add count badge to Tasks tab showing open task count
- [x] 6.2 Add indicator dot to Health & Photos tab when health score < 50
- [ ] 6.3 Add "overdue" indicator to Activity tab when water changes are overdue (deferred — requires bucket-level data in page state)

## 7. Final Tab Order
- [x] 7.1 Implement tab order: Overview → Buckets → Activity → Tasks → Nutrition & Yield → Health & Photos → (Field - outdoor only) → Settings
- [ ] 7.2 Ensure tab state persists when switching between grows (remember last active tab)

## 8. Testing
- [x] 8.1 TypeScript compilation passes with no errors
- [ ] 8.2 E2E test: navigate each merged tab and sub-section
- [ ] 8.3 Mobile responsiveness: verify tabs don't overflow on small screens (max 8 visible)
