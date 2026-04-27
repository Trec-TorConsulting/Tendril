# Tasks: Migrate Trector Website to Frappe

**Change ID:** `migrate-trector-website-to-frappe`  
**Last Updated:** March 6, 2026

---

## Phase 1: Foundation Setup

### 1.1 CSS Framework
- [x] Create `trector-styles.css` with all custom classes
- [x] Define CSS variables for colors: `--trec-primary`, `--trec-secondary`, `--trec-gradient`
- [x] Port gradient backgrounds: `animated-gradient`, `gradient-shimmer`, `hero-gradient`
- [x] Port animations: `@keyframes float`, `bounce`, `pulseGlow`, `shimmer`, `gradientShift`
- [x] Create utility classes: `.trec-gradient-text`, `.trec-btn-primary`, `.trec-card`
- [x] Add responsive breakpoints matching Tailwind
- [x] Upload CSS to Frappe and include in Web Page template

### 1.2 Font & Icons Setup
- [x] Add Google Fonts link for Inter font family
- [x] Add Font Awesome 6 CDN link
- [x] Create icon mapping reference document
- [x] Test icons render correctly

### 1.3 Assets Upload
- [x] Download logo.svg from original site
- [x] Upload logo to Frappe File Manager
- [x] Upload any other images used (og-default.jpg, etc.)
- [x] Note file URLs for use in HTML

---

## Phase 2: Homepage Migration

### 2.1 Hero Section
- [x] Create animated gradient background with shimmer effect
- [x] Add "⭐ Trusted by 500+ Businesses" badge  
- [x] Add main heading: "Business Technology Consultant & Solutions"
- [x] Add subheading with description text
- [x] Create two CTA buttons: "Our Services →" and "Let's Chat"
- [x] Build floating stat badges:
  - [x] "32+ Years Experience" badge
  - [x] "500+ Happy Clients" badge  
  - [x] "$50M+ Saved Together" badge
- [x] Add central rocket icon with floating animation
- [x] Add pulsing glow dots (yellow, green, blue)
- [x] Test animations on desktop and mobile

### 2.2 Why Consultants Section
- [x] Add section header with "Why Choose Us" badge
- [x] Create 6 benefit cards with colored left borders:
  - [x] Objective Outside Perspective (primary border, eye icon)
  - [x] Specialized Expertise (secondary border, graduation cap icon)
  - [x] Accelerated Growth (green border, rocket icon)
  - [x] Risk Mitigation (blue border, shield icon)
  - [x] Measurable Results (orange border, chart icon)
  - [x] Time & Resource Optimization (secondary border, clock icon)
- [x] Add hover effects (translate-y, shadow)
- [x] Add quote block at bottom with lightbulb icon

### 2.3 About Section
- [x] Add "Who We Are" badge and section header
- [x] Write "Our Story" subsection with Geek Info LLC link
- [x] Write "Breaking Through Technology Barriers" subsection
- [x] Write "Our Philosophy" with 3 items:
  - [x] Simplify, Don't Complicate (rocket icon)
  - [x] Education-First Approach (users icon)
  - [x] Scalable Solutions (gears icon)
- [x] Create "Why Startups Choose Us" grid (4 cards):
  - [x] Time Liberation
  - [x] Risk Mitigation
  - [x] Cost Optimization ($)
  - [x] Knowledge Transfer
- [x] Write "Our Commitment to Your Success" section
- [x] Create 3 value boxes: Innovation, Partnership, Excellence

### 2.4 Business Technology Consultant Section
- [x] Create two-column layout
- [x] Left column: heading, description, 3 checkmark features, CTA button
- [x] Right column: stats panel
  - [x] "30+ Years" stat
  - [x] "$500K+ Saved" stat  
  - [x] "50+ Businesses" stat
  - [x] Expert quote with border

### 2.5 Services Section
- [x] Add "What We Offer" badge and header
- [x] Create 9 service cards in 3-column grid:
  - [x] Fractional CTO (cloud icon) → /fractional-cto-services
  - [x] Public Cloud Solutions (cloud icon) → /cloud-consulting
  - [x] Cybersecurity Consulting (shield-virus icon) → /cybersecurity-consulting
  - [x] Business Automation (robot icon) → /business-automation
  - [x] Point of Sale Solutions (store icon) → /pos-solutions
  - [x] E-Commerce & Web Solutions (cart icon) → /ecommerce-solutions
  - [x] Inventory Management (boxes icon) → /inventory-management
  - [x] Logistics & Supply Chain (truck icon) → /logistics-consulting
  - [x] Startup Strategy (rocket icon) → /startup-consulting
- [x] Each card: icon, title, description, 4 bullet features, "Learn More →" link
- [x] Add hover effects

### 2.6 Testimonials Section
- [x] Add "⭐ Client Success Stories" badge
- [x] Add aggregate rating display (4.8/5, 6 reviews)
- [x] Create 6 testimonial cards:
  - [x] Jessica Martinez - Fractional CTO Services (5/5)
  - [x] Sarah Johnson - Cloud Consulting & Cybersecurity (5/5)
  - [x] Michael Chen - Business Automation (5/5)
  - [x] Emily Rodriguez - E-commerce & POS Solutions (5/5)
  - [x] David Kim - Cloud Consulting & Logistics (4/5) 
  - [x] Amanda Foster - Business Automation (not rated)
- [x] Each card: star rating, quote, author name, title, service type

### 2.7 Contact Section
- [x] Add "💬 Let's Talk" badge and header
- [x] Left column - Contact Information:
  - [x] Phone: (856) 618-1114
  - [x] Email: info@trector.com
  - [x] Business Hours: Mon-Fri 9-6 EST
- [x] Right column - Contact Form:
  - [x] Full Name field
  - [x] Email Address field
  - [x] Company Name field
  - [x] Service Interest dropdown
  - [x] Message textarea
  - [x] Submit button (opens mailto: link)
- [x] Add tip text about 24-hour response

---

## Phase 3: Service Pages

### 3.1 Fractional CTO Services
- [x] Hero with rocket icon
- [x] "What is a Fractional CTO?" section
- [x] Core Services grid (4 cards)
- [x] Engagement models table
- [x] Pricing info
- [x] CTA buttons

### 3.2 Cloud Consulting
- [x] Hero section
- [x] Cloud providers section (AWS, Azure, GCP)
- [x] Services offered
- [x] Case studies/results
- [x] CTA

### 3.3 Cybersecurity Consulting
- [x] Hero section
- [x] Security services list
- [x] Compliance (SOC 2, HIPAA, PCI-DSS)
- [x] Security assessment process
- [x] CTA

### 3.4 Business Automation
- [x] Hero section
- [x] Automation types
- [x] ROI examples
- [x] Implementation process
- [x] CTA

### 3.5 POS Solutions
- [x] Hero section
- [x] POS features
- [x] Payment integrations
- [x] Analytics capabilities
- [x] CTA

### 3.6 E-commerce Solutions
- [x] Hero section
- [x] Platform expertise (Shopify, WooCommerce, Magento)
- [x] Custom development
- [x] SEO & marketing
- [x] CTA

### 3.7 Inventory Management
- [x] Hero section
- [x] Tracking features
- [x] Integration capabilities
- [x] Forecasting
- [x] CTA

### 3.8 Logistics Consulting
- [x] Hero section
- [x] Supply chain optimization
- [x] Route planning
- [x] 3PL integration
- [x] CTA

### 3.9 Startup Consulting
- [x] Hero section
- [x] Business planning
- [x] Market validation
- [x] Funding strategy
- [x] CTA

---

## Phase 4: Blog Migration

### Sitemap Audit (Feb 24, 2026)
- [x] Fetched and parsed www.trector.com/sitemap.xml
- [x] Cross-referenced with NextJS source code (blogData.ts — 33 posts)
- [x] Cross-referenced with live site navigation and footer links
- [x] Identified missing `/technology-assessment` page — deployed
- [x] Confirmed 26 published blog posts (as of Feb 24, 2026)
- [x] Identified 7 future/scheduled posts (Feb 26 – Apr 9, 2026)
- [x] Noted non-sitemap pages: /privacy-policy, /terms-of-service, /contact, /services

### 4.1 Blog Index Page
- [x] Create `/blog` index page
- [x] "Technology Insights" header with article count
- [x] Featured article section (most recent)
- [x] Regular articles in 2-column card grid
- [x] Category color badges (8 categories: Cloud, Strategy, Leadership, Security, Automation, E-Commerce, Data, Integration)
- [x] Read time and date display
- [x] CTA section with assessment link

### 4.2 Blog Infrastructure
- [x] Created `migrate_blogs.py` script with full 33-post registry
- [x] Automated fetch from www.trector.com with content extraction
- [x] Added Tailwind Play CDN to head_html for blog content styling
- [x] Configured custom theme colors (primary: #667eea, secondary: #764ba2)
- [x] Handles both blog formats (older allContent.tsx + newer individual pages)
- [x] Blog CSS (index page styles) added to trector-styles.css
- [x] Deploy as Frappe Web Pages with exact URL routes (`blog/<slug>`)
- [x] Future posts support via `--include-future` flag (deployed as drafts)

### 4.3 Blog Posts — Published (26 posts)
- [x] Public Cloud Strategy (2025-08-28)
- [x] Small Business Data Strategy (2025-09-04)
- [x] API Integration Strategy (2025-09-11)
- [x] E-commerce Modernization (2025-09-18)
- [x] Business Automation High ROI (2025-09-25)
- [x] Cybersecurity Foundations (2025-10-02)
- [x] Fractional CTO Benefits (2025-10-09)
- [x] Business Technology Strategy (2025-10-16)
- [x] Cloud Migration Checklist (2025-10-23)
- [x] Saved Client 50K Cloud Costs (2025-10-30)
- [x] Cybersecurity Basics for CEOs (2025-11-06)
- [x] Small Business AI Adoption 2025 (2025-11-13)
- [x] Digital Transformation Without Disruption (2025-11-20)
- [x] SaaS Stack Optimization (2025-11-27)
- [x] Scalable Infrastructure Growth (2025-12-04)
- [x] Data Analytics ROI Small Business (2025-12-11)
- [x] System Integration Best Practices SMB 2025 (2025-12-18)
- [x] Technology Roadmap Planning 2026 (2025-12-25)
- [x] Zero Trust Security Implementation 2026 (2026-01-01)
- [x] Business Intelligence Dashboard 2025 (2026-01-08)
- [x] Legacy System Modernization 2026 (2026-01-15)
- [x] Business Process Automation Guide 2026 (2026-01-22)
- [x] Headless Commerce Architecture 2026 (2026-01-29)
- [x] Workflow Automation Platforms 2026 (2026-02-05)
- [x] Building Innovation Framework 2026 (2026-02-12)
- [x] Data Privacy Compliance 2025 (2026-02-19)

### 4.4 Blog Posts — Scheduled/Future (7 posts)
- [x] Modern Technology Leadership 2026 (2026-02-26) — published
- [x] SOC 2 Compliance Guide 2026 (2026-03-05) — published
- [x] E-commerce Personalization 2026 (2026-03-12) — staged as draft, K3S CronJob handles publish
- [x] RPA Implementation Guide 2026 (2026-03-19) — staged as draft, K3S CronJob handles publish
- [x] Multi-Cloud Strategy 2026 (2026-03-26) — staged as draft, K3S CronJob handles publish
- [x] Building Tech Teams 2026 (2026-04-02) — staged as draft, K3S CronJob handles publish
- [x] Cloud Cost Governance Framework 2026 (2026-04-09) — staged as draft, K3S CronJob handles publish

---

## Phase 5: Navigation & Footer

### 5.1 Header/Navigation
- [x] Create sticky header with logo
- [x] Navigation links: Home, About, Services, Blog, Contact
- [x] Active link styling with gradient background
- [x] Mobile hamburger menu
- [x] Client Portal button (links to ERPNext)

### 5.2 Footer
- [x] Dark background (gray-900)
- [x] 4-column layout:
  - [x] Logo + description
  - [x] Services links (9 items)
  - [x] Company links (7 items)
  - [x] Contact info
- [x] Copyright bar with Privacy/Terms links
- [x] "Serving businesses since 1993" tagline

### 5.3 Missing Pages (added during Phase 5)
- [x] Privacy Policy page created and deployed
- [x] Terms of Service page created and deployed
- [x] Legal page CSS styles (.trec-legal-content)

### 5.4 Implementation Notes
- Navbar: Frappe built-in navbar with 6 items (5 left + Client Portal right) via Website Settings
- Footer: Site-wide injection via `<template>` + JS in head_html (Frappe's default footer hidden)
- Mobile: Bootstrap hamburger menu with custom purple icon + transitions
- Active link: JS-based route matching on DOMContentLoaded
- CSS: Navbar overrides (sticky, gradient active), hamburger styling, legal page typography

---

## Phase 6: QA & Polish

> **Note (March 6, 2026):** Site has been live at www.trector.com since Feb 27. Formal QA skipped — verified working in production. No blocking issues found.

- [x] Site live and functional at www.trector.com
- [x] All links verified working
- [x] Contact form functional
- [x] SEO meta tags configured
- [x] Mobile responsive verified

---

## Migration Scripts Reference

All updates done via Frappe API:

```bash
# Base URL
BASE_URL="https://client.trector.com"

# Authentication (use API key/secret from .env — never commit tokens)
AUTH_HEADER="Authorization: token <api-key>:<api-secret>"

# Update page content
curl -X PUT -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d '{"content_type":"HTML","main_section_html":"<html>"}' \
  "$BASE_URL/api/resource/Web Page/page-name"
```

---

## Completion Checklist

- [x] Phase 1 complete: Foundation ready
- [x] Phase 2 complete: Homepage matches original
- [x] Phase 3 complete: All 9 service pages migrated
- [x] Phase 4 complete: Blog index and 28 posts live, 5 future staged with CronJob
- [x] Phase 5 complete: Navigation and footer working
- [x] Phase 6 complete: Site live since Feb 27, verified in production
- [x] **MIGRATION COMPLETE** (Feb 27, 2026)
