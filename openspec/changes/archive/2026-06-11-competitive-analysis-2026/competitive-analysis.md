# Competitive Analysis: Tendril vs 12 Ag-Tech Platforms

**Date**: April 28, 2026
**Scope**: Deep dive — feature comparison, UI learnings, gap identification
**Deliverable**: Spreadsheet-style comparison + OpenSpec proposals for gaps

---

## Feature Comparison Matrix

### Legend
- ✅ = Has feature (robust)
- 🟡 = Partial / basic implementation
- ❌ = Does not have
- N/A = Not applicable to platform's scope

---

### 1. CANNABIS-SPECIFIC FEATURES

| Feature | Tendril | GrowLink | GrowDirector | farmOS | Others |
|---------|---------|----------|--------------|--------|--------|
| **Grow type configs (DWC, NFT, coco, etc.)** | ✅ (12 types, deep) | ❌ (generic) | ❌ (generic CEA) | ❌ | ❌ across all |
| **Crop steering (veg→gen)** | 🟡 (in config) | ✅ (built-in) | ✅ (recipe-based) | ❌ | ❌ across all |
| **Strain/cultivar management** | ✅ (strain model) | 🟡 (basic) | ❌ | 🟡 (assets) | ❌ across all |
| **Cannabis growth stages (12-stage)** | ✅ (per type) | 🟡 (generic) | 🟡 (recipes) | ❌ | ❌ across all |
| **Nutrient schedule per type** | ✅ (per config) | ✅ (fertigation) | ✅ (fertigation) | ❌ | ❌ across all |
| **Reservoir management** | ✅ (bucket model) | ✅ (integrated) | ✅ (irrigation) | ❌ | ❌ across all |
| **Drying/curing tracking** | ✅ (stages 11-12) | ❌ | ❌ | ❌ | ❌ across all |
| **Trichome/harvest timing** | ✅ (in config) | ❌ | ❌ | ❌ | ❌ across all |
| **Multi-tent management** | ✅ (tent model) | ✅ (rooms) | ✅ (zones) | 🟡 (areas) | ❌ across all |
| **Light schedule (12/12, 18/6)** | ✅ (per stage) | ✅ (automated) | ✅ (DLI-based) | ❌ | ❌ across all |

**Tendril advantage**: Only platform with deep, per-grow-type specialized configs. No competitor differentiates between DWC, NFT, Kratky, etc. at the guidance/config level.

---

### 2. ENVIRONMENT & SENSOR MONITORING

| Feature | Tendril | GrowLink | GrowDirector | Climate FV | AGMRI | AGRIVI |
|---------|---------|----------|--------------|-----------|-------|--------|
| **Temp/humidity sensors** | ✅ (ESP32) | ✅ (proprietary) | ✅ (proprietary) | ❌ | ❌ | ✅ (IoT) |
| **Soil moisture** | ✅ (capacitive) | ✅ | ✅ | ❌ | ❌ | ✅ |
| **pH/EC monitoring** | 🟡 (manual log) | ✅ (automated) | ✅ (automated) | ❌ | ❌ | ❌ |
| **CO2 monitoring** | 🟡 (sensor ready) | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Light (PAR/DLI)** | ❌ | ✅ | ✅ (DLI targets) | ❌ | ❌ | ❌ |
| **VPD calculation** | 🟡 (derivable) | ✅ (real-time) | ✅ | ❌ | ❌ | ❌ |
| **Substrate weight** | ❌ | ✅ | 🟡 | ❌ | ❌ | ❌ |
| **Water temp** | ❌ | ✅ | 🟡 | ❌ | ❌ | ❌ |
| **Real-time alerts** | ✅ (MQTT) | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Historical charts** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Automated equipment control** | ❌ | ✅ (core feature) | ✅ (core feature) | ❌ | ❌ | ❌ |

**Gap identified**: Tendril lacks automated equipment control (lights, fans, pumps via relay). GrowLink and GrowDirector's core value is turning sensor data into equipment actions.

---

### 3. AI & INTELLIGENCE

| Feature | Tendril | Plantix | Cropin | AGMRI | Climate FV | AGRIVI |
|---------|---------|---------|--------|-------|-----------|--------|
| **AI grow assistant** | ✅ (Ollama/Gemini) | ❌ | 🟡 (enterprise) | ❌ | ❌ | ✅ (WhatsApp) |
| **Photo disease detection** | ❌ | ✅ (core feature) | ❌ | ✅ (aerial) | ❌ | ❌ |
| **Predictive yield** | ❌ | ❌ | ✅ (satellite) | ✅ (field-level) | ✅ (seed scripts) | ❌ |
| **AI nutrient recommendations** | 🟡 (context) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Pest/disease library** | ❌ | ✅ (extensive) | ❌ | ✅ (field) | ❌ | ✅ |
| **Natural language chat** | ✅ (Ollama) | ❌ | ❌ | ❌ | ❌ | ✅ (WhatsApp bot) |
| **Computer vision (plant health)** | ❌ | ✅ (mobile cam) | ✅ (satellite) | ✅ (aerial) | ✅ (imagery) | ❌ |
| **GDD-based predictions** | 🟡 (in config) | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Local/edge AI** | ✅ (Ollama/Jetson) | ❌ | ❌ | ❌ | ❌ | ❌ |

**Tendril advantage**: Local AI on Jetson (privacy, no cloud dependency). **Gap**: No computer vision / photo-based plant health detection.

---

### 4. OUTDOOR & FIELD FEATURES

| Feature | Tendril | farmOS | LandPKS | AGMRI | Climate FV | JD Ops | AGRIVI |
|---------|---------|--------|---------|-------|-----------|--------|--------|
| **Weather integration** | 🟡 (planned) | 🟡 | 🟡 (climate) | ✅ | ✅ | ✅ | ✅ |
| **Soil testing/tracking** | ✅ (outdoor module) | ✅ (logs) | ✅ (core) | ❌ | ❌ | ❌ | ✅ |
| **Plot/field mapping** | ✅ (grid designer) | ✅ (areas/maps) | ✅ (GPS) | ✅ (satellite) | ✅ (field maps) | ✅ (boundary) | ✅ |
| **Companion planting** | 🟡 (planned) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Pest scouting** | ✅ (IPM routes) | ✅ (observations) | ❌ | ✅ (aerial) | ❌ | ❌ | ✅ |
| **Harvest yield tracking** | ✅ (per-plant) | ✅ (harvest logs) | ❌ | ✅ (yield maps) | ✅ (yield data) | ✅ (yield docs) | ✅ |
| **Satellite/aerial imagery** | ❌ | ❌ | ✅ (NDVI) | ✅ (core) | ✅ (core) | ✅ | ✅ |
| **Hardiness zones** | 🟡 (planned) | ❌ | ✅ (core) | ❌ | ❌ | ❌ | ❌ |
| **GDD tracking** | 🟡 (planned) | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Irrigation planning** | 🟡 (planned) | ✅ (water logs) | ❌ | ❌ | ❌ | ✅ | ✅ |

---

### 5. BUSINESS & OPERATIONS

| Feature | Tendril | AGRIVI | FarmKeep | farmOS | Climate FV | JD Ops |
|---------|---------|--------|----------|--------|-----------|--------|
| **Cost/ROI tracking** | ❌ | ✅ (core) | ✅ | 🟡 | ❌ | ❌ |
| **Task management** | ✅ (tasks model) | ✅ | ✅ | ✅ (logs) | ❌ | ❌ |
| **Team/staff management** | ✅ (multi-tenant) | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Inventory management** | ❌ | ✅ | ✅ (livestock) | ✅ (assets) | ❌ | ❌ |
| **Financial reporting** | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Compliance/traceability** | ❌ | ✅ (core) | ❌ | ❌ | ❌ | ❌ |
| **Season comparison** | ❌ | ✅ | ❌ | ✅ (logs) | ✅ | ✅ |
| **Export/reports** | ❌ | ✅ | ✅ (CSV) | ✅ | ✅ | ✅ |
| **Multi-site management** | ✅ (tenant) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Equipment tracking** | ❌ | ✅ | ❌ | ✅ (assets) | ✅ | ✅ (core) |

---

### 6. PLATFORM & TECHNICAL

| Feature | Tendril | GrowLink | GrowDirector | farmOS | Climate FV |
|---------|---------|----------|--------------|--------|-----------|
| **PWA / mobile** | ✅ (PWA) | ✅ (native iOS) | ✅ (web) | ✅ (responsive) | ✅ (native) |
| **Offline support** | ❌ | 🟡 | ❌ | ❌ | ✅ (Drive) |
| **Open source** | ✅ (AGPL) | ❌ | ❌ | ✅ (GPL-2) | ❌ |
| **Self-hosted** | ✅ (k3s) | ❌ (cloud) | ❌ (cloud) | ✅ (Docker) | ❌ (cloud) |
| **REST API** | ✅ | 🟡 | 🟡 | ✅ (JSON:API) | ✅ |
| **MQTT/IoT native** | ✅ (EMQX) | ✅ (proprietary) | ✅ | ❌ | ❌ |
| **Third-party integrations** | ❌ | ✅ (hundreds) | 🟡 | ✅ (modules) | ✅ (60+) |
| **Webhooks/events** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Data import/export** | ❌ | 🟡 | ❌ | ✅ | ✅ |
| **Multi-language** | ❌ | ❌ | ❌ | ✅ (Drupal i18n) | 🟡 |

---

## GENERAL AG INSIGHTS (Transferable to Tendril)

### From Cropin (Enterprise AI)
- **Crop Knowledge Grid**: Massive database of crop-specific data (growth patterns, disease susceptibility, optimal conditions). Tendril equivalent: our grow type configs serve this purpose but could be expanded.
- **Supply chain traceability**: QR code from seed to shelf. Cannabis relevance: seed-to-sale compliance tracking.
- **Satellite/NDVI integration**: Remote sensing for outdoor grows. Applicable to outdoor soil grows at scale.

### From Plantix (AI Vision)
- **Photo-based disease detection**: Take photo → instant diagnosis + treatment. This is the #1 missing AI feature in Tendril. 100M+ crop questions answered.
- **Treatment library**: Structured database of diseases, pests, and treatments with photos.
- **Community Q&A**: Social/expert network for grower questions.

### From AGMRI (Aerial Analytics)
- **Post-season analytics**: Analyze what happened and why after harvest. Identify what impacted yield.
- **Nitrogen management**: Proactive nutrient management through sensing. Cannabis equivalent: proactive deficiency detection.

### From Climate FieldView (Data Platform)
- **60+ partner integrations**: Ecosystem approach — connect with any hardware/software.
- **Seed scripts / variable rate**: Adjust inputs per zone/area. Cannabis equivalent: per-plant nutrient adjustments.
- **Offline-first with sync**: FieldView Drive works offline, syncs when connected. Critical for PWA.

### From John Deere Operations Center
- **Fleet management**: Track equipment across sites. Cannabis equivalent: equipment maintenance scheduling.
- **Yield documentation**: Standardized yield data collection. Cannabis: standardized harvest logs.
- **Data sharing with advisors**: Share access with consultants/agronomists.

### From AGRIVI (Farm Management)
- **AI advisory via WhatsApp/Viber**: Meet farmers where they are. Cannabis equivalent: Tendril AI accessible via messaging.
- **ROI calculator**: Input costs vs yield value per grow. Missing entirely from Tendril.
- **Compliance/regulatory**: Built-in compliance workflows. Cannabis: state-specific compliance.
- **IoT plug-and-play**: Simple sensor onboarding. Tendril has MQTT but could improve onboarding.

### From farmOS (Open Source)
- **JSON:API standard**: Industry-standard API format. Tendril uses REST but could benefit from standardization.
- **Module/plugin system**: Community can extend. Tendril is monolithic currently.
- **Data import/export**: CSV, GeoJSON, etc. Tendril has no import/export.

### From FarmKeep (UX)
- **Simplicity-first UX**: Task management, record keeping designed for people who hate software.
- **Breeding/genetics tracking**: Track lineage, cross-pollination. Cannabis: strain breeding program tracking.

### From LandPKS (Soil Science)
- **Soil ID from location**: Auto-identify soil type from GPS coordinates using USDA database.
- **Visual soil health indicators**: Photo-based soil assessment.
- **Soil texture classification**: Field-based soil texture test (ribbon test protocol).

---

## IDENTIFIED FEATURE GAPS (Priority Order)

### P0 — Critical Missing Features

| # | Gap | Source Inspiration | Cannabis Relevance | Impact |
|---|-----|-------------------|-------------------|--------|
| 1 | **Photo-based plant health AI** | Plantix, AGMRI | Detect deficiencies, pests, diseases from phone photo | Game-changer for beginners |
| 2 | **Cost/ROI tracking per grow** | AGRIVI, FarmKeep | Input costs, electricity, nutrients vs harvest value | Essential for commercial |
| 3 | **Data export (CSV, PDF reports)** | All competitors | Compliance, sharing with partners, record keeping | Table stakes |
| 4 | **Offline PWA support** | Climate FieldView | Works in grow room with no signal, syncs when connected | Critical for basements/warehouses |

### P1 — High Value Features

| # | Gap | Source Inspiration | Cannabis Relevance | Impact |
|---|-----|-------------------|-------------------|--------|
| 5 | **Equipment control via relay** | GrowLink, GrowDirector | Turn on/off lights, fans, pumps based on sensor readings | Commercial differentiator |
| 6 | **VPD real-time dashboard** | GrowLink, GrowDirector | Calculated from temp/humidity, displayed in real-time | Most requested by growers |
| 7 | **Season-over-season comparison** | AGRIVI, Climate FV, farmOS | Compare this grow vs last grow: yield, timeline, issues | Learning from history |
| 8 | **Treatment/spray log** | Plantix, AGRIVI | Track what was applied, when, re-entry intervals | Compliance + IPM |
| 9 | **Pest/disease visual library** | Plantix, AGRIVI | Photo database of common cannabis problems | Education tool |
| 10 | **Notification channels (SMS, push, email)** | GrowLink, AGRIVI | Alert grower of critical conditions through multiple channels | Safety net |

### P2 — Valuable Additions

| # | Gap | Source Inspiration | Cannabis Relevance | Impact |
|---|-----|-------------------|-------------------|--------|
| 11 | **PAR/DLI light tracking** | GrowLink, GrowDirector | Measure actual light delivery, optimize placement | Precision growing |
| 12 | **Inventory management** | AGRIVI, farmOS, FarmKeep | Track nutrient stock, supplies, equipment | Operational efficiency |
| 13 | **Compliance/seed-to-sale** | AGRIVI (traceability) | State cannabis regulations, batch tracking | Legal requirement |
| 14 | **Community/social features** | Plantix | Share grows, ask questions, learn from others | Engagement + retention |
| 15 | **Third-party integrations** | Climate FV, GrowLink | Connect to existing hardware (Trolmaster, BlueLab, Aroya) | Hardware agnostic |
| 16 | **Data import (migrate from other apps)** | farmOS | Import historical data from spreadsheets/other apps | Onboarding |
| 17 | **Breeding/genetics tracker** | FarmKeep | Track strain crosses, phenotype notes, lineage | Breeders |
| 18 | **Multi-language support** | farmOS, AGRIVI | Serve global cannabis community | Market expansion |

---

## UI/UX LEARNINGS

### From GrowLink
- **Blueprint system**: Save grow room configurations as reusable templates. Start a new grow from a proven blueprint. Tendril equivalent: "grow templates" — save a complete setup and clone it.
- **Single dashboard for everything**: Climate + irrigation + nutrients on one screen. No tab-switching.

### From Plantix
- **Camera-first UX**: Open app → point camera → get answer. Minimum friction for disease detection.
- **Free tier drives adoption**: 100M+ questions = massive user base. Free core + premium add-ons.

### From AGRIVI
- **ROI calculator as marketing tool**: Free on website, converts visitors. Shows value before signup.
- **WhatsApp bot**: AI advisor in the app growers already use. Brilliant distribution strategy.

### From FarmKeep
- **Mobile-first, web second**: Built for the field (or grow room). Desktop is an afterthought. This is right.
- **Family/team sharing**: Simple invite link, role-based access. No complex tenant setup.

### From Climate FieldView
- **Hardware + software bundle**: FieldView Drive (hardware dongle) auto-captures data. Tendril equivalent: ESP32 pre-configured and ready to connect.
- **Dealer channel**: Sell through ag dealers. Cannabis: sell through hydro shops.

---

## PLATFORM-BY-PLATFORM SUMMARY

| Platform | Focus | Key Strength | Tendril Takeaway | Pricing |
|----------|-------|-------------|-----------------|---------|
| **GrowLink** | Cannabis cultivation automation | Equipment control + crop steering | #1 direct competitor. We beat on grow type depth. They beat on hardware control. | Enterprise (contact sales) |
| **GrowDirector** | CEA automation (cannabis incl.) | Modular, industrial-grade control | Similar to GrowLink. Hardware-heavy. Config recipes are similar to our grow type configs. | Enterprise (contact sales) |
| **Cropin** | Enterprise agriculture | AI-first, satellite imagery, supply chain | Too enterprise/field-crop for direct comparison. Crop Knowledge Grid concept validates our grow type config approach. | Enterprise SaaS |
| **Plantix** | Mobile crop diagnosis | Photo-based AI disease detection | **Steal this**: photo diagnosis is our #1 missing AI feature. 100M users proves demand. | Free (B2B APIs for revenue) |
| **AGRIVI** | Farm management + traceability | Complete business management (costs, compliance, IoT) | ROI tracking, compliance, and WhatsApp AI are gaps we should fill. | Tiered SaaS |
| **FarmKeep** | Livestock/homestead management | Simple record keeping UX | Not directly competitive (animal-focused). UX simplicity and mobile-first approach worth studying. | Freemium mobile app |
| **farmOS** | Open-source farm records | Extensibility, JSON:API, community | Closest open-source peer. Import/export and module system are worth considering. | Free (self-hosted) |
| **LandPKS** | Soil/land science | USDA soil database, GPS-based soil ID | Soil ID integration would enhance outdoor soil grow type. | Free (USDA funded) |
| **AGMRI** | Aerial imagery analytics | Field-level crop health from imagery | Post-season analytics concept transfers. Not directly applicable to indoor cannabis. | Seasonal subscription |
| **Climate FieldView** | Row crop data platform | 60+ integrations, offline-first | Offline PWA and integration ecosystem are top learnings. | $499-999/yr |
| **John Deere Ops** | Equipment + field management | Fleet tracking, yield documentation | Equipment maintenance scheduling concept transfers. | Included w/ JD equipment |
| **WiseYield** | (Unable to access) | — | — | — |
