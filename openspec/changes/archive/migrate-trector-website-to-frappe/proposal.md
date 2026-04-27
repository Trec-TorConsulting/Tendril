# Proposal: Migrate Trector Website to Frappe (1:1 Match)

**Change ID:** `migrate-trector-website-to-frappe`  
**Author:** GitHub Copilot  
**Date:** February 19, 2026  
**Updated:** February 27, 2026  
**Status:** Completed  
**Completed:** February 27, 2026

## Summary

Completed 1:1 migration of www.trector.com from Next.js (previously Vercel-hosted) to Frappe CMS running on K3S cluster. The site is now live and self-hosted — Vercel is no longer used.

## Motivation

The business migrated from a Next.js + Vercel hosted website to a self-hosted Frappe CMS for better integration with existing ERPNext instance. Vercel hosting has been fully decommissioned. The website now runs entirely on the local K3S cluster.

## Current State Analysis

### Previous Stack (Decommissioned): Next.js/Vercel

**Former Technology Stack (no longer in use):**
- Next.js 15.x with App Router
- React 19 with dynamic imports
- Tailwind CSS v4
- React Icons (Font Awesome icons)
- Custom CSS animations

**Design System:**
| Element | Value |
|---------|-------|
| Primary Color | `#667eea` (blue-purple) |
| Secondary Color | `#764ba2` (purple) |
| Gradient Middle | `#6e64c6` |
| Font | Inter (Google Fonts) |
| Border Radius | `0.75rem` (lg), `1rem` (xl), `1.5rem` (2xl) |
| Shadows | Tailwind default shadows |

**Homepage Sections (in order):**
1. **Hero Section** - Animated gradient background, floating stat badges, rocket icon
2. **Why Consultants Section** - 6 benefit cards with colored left borders
3. **About Section** - Our Story, Philosophy (3 items), Why Choose Us (4 cards), Commitment (3 values)
4. **Business Technology Consultant Section** - Stats panel with quote
5. **Services Section** - 9-service grid with icons and features
6. **Testimonials Section** - 6 testimonial cards with ratings
7. **Contact Section** - Contact info + form
8. **Footer** - 4-column layout with links and contact

**Animations:**
- `animated-gradient` - Background color shift (20s cycle)
- `gradient-shimmer` - Light sweep effect
- `bounce-slow` - Floating badges bounce
- `pulse-glow` - Glowing dots
- `float` - Central icon float

**Service Pages (9 total):**
- Fractional CTO Services
- Cloud Consulting  
- Cybersecurity Consulting
- Business Automation
- POS Solutions
- E-commerce Solutions
- Inventory Management
- Logistics Consulting
- Startup Consulting

**Blog:**
- 18 published posts with full content
- Blog index with search/filter (React-based)
- Categories: Cloud, Security, Automation, etc.

### Target: client.trector.com (Frappe CMS)

**Current State:**
- Homepage at `/home` (Frappe reserves `/` for login)
- 15 service pages with placeholder HTML
- 18 blog posts created as Web Pages
- Basic styling, missing all animations and icons
- No custom CSS framework

**Frappe Limitations:**
- No React - all interactive features need vanilla JS or static HTML
- No Tailwind by default - need custom CSS
- Web Page doctype with HTML content
- Homepage cannot be at `/` (Frappe framework limitation)

## Proposed Solution

### Phase 1: Foundation (CSS Framework & Assets)

1. **Create custom CSS file** mirroring Tailwind classes used in original
2. **Set up Font Awesome CDN** for icons (mapping from React Icons)
3. **Upload logo and images** to Frappe File Manager
4. **Configure Inter font** via Google Fonts CDN

### Phase 2: Homepage Migration

1. **Hero Section** - Exact gradient, animations, floating badges
2. **Why Consultants Section** - 6 benefit cards with icons
3. **About Section** - Full content with philosophy and values
4. **Business Tech Consultant Section** - Stats panel
5. **Services Grid** - 9 service cards with links
6. **Testimonials** - 6 cards with star ratings
7. **Contact Section** - Info + mailto form

### Phase 3: Service Pages (9 pages)

Full content migration for each service page:
- Hero section with service icon
- What/Why sections
- Features list with checkmarks
- CTA buttons
- Related blog links

### Phase 4: Blog Migration

1. **Blog Index** - Static card-based listing (no search)
2. **Blog Posts** - Full article content with styling
3. **Category styling** - Color-coded category badges

### Phase 5: Navigation & Footer

1. **Header/Navigation** - Fixed header with gradient active states
2. **Footer** - 4-column layout with all links
3. **Mobile responsive** - Hamburger menu

### Phase 6: Polish & QA

1. **Cross-browser testing**
2. **Mobile responsiveness**
3. **Performance optimization**
4. **Compare side-by-side with original**

## Icon Mapping (React Icons → Font Awesome)

| React Icon | Font Awesome Class |
|------------|-------------------|
| FaRocket | `fa-solid fa-rocket` |
| FaCloud | `fa-solid fa-cloud` |
| FaShieldVirus | `fa-solid fa-shield-virus` |
| FaRobot | `fa-solid fa-robot` |
| FaStore | `fa-solid fa-store` |
| FaShoppingCart | `fa-solid fa-cart-shopping` |
| FaBoxes | `fa-solid fa-boxes-stacked` |
| FaTruck | `fa-solid fa-truck` |
| FaChartLine | `fa-solid fa-chart-line` |
| FaEye | `fa-solid fa-eye` |
| FaGraduationCap | `fa-solid fa-graduation-cap` |
| FaShieldAlt | `fa-solid fa-shield-halved` |
| FaClock | `fa-solid fa-clock` |
| FaLightbulb | `fa-solid fa-lightbulb` |
| FaUsers | `fa-solid fa-users` |
| FaCogs | `fa-solid fa-gears` |
| FaHandshake | `fa-solid fa-handshake` |
| FaTrophy | `fa-solid fa-trophy` |
| FaCheckCircle | `fa-solid fa-circle-check` |
| FaPhone | `fa-solid fa-phone` |
| FaEnvelope | `fa-solid fa-envelope` |

## Success Criteria

1. **Visual parity**: Side-by-side comparison shows <5% difference
2. **All content migrated**: 100% of text, images, links present
3. **Animations working**: Hero gradient, shimmer, floating badges
4. **Mobile responsive**: Works on all screen sizes
5. **Performance**: Page loads in <3 seconds
6. **SEO preserved**: Meta descriptions, titles, structured data

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Frappe CSS conflicts | Use scoped class names with `trec-` prefix |
| Animation performance | Use GPU-accelerated transforms, reduce on mobile |
| Homepage URL (`/home` vs `/`) | Accept `/home` or configure Traefik redirect |
| Complex interactivity loss | Accept static alternatives for search/filter |

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Foundation | 2 hours | None |
| Phase 2: Homepage | 4 hours | Phase 1 |
| Phase 3: Service Pages | 6 hours | Phase 1 |
| Phase 4: Blog | 3 hours | Phase 1 |
| Phase 5: Navigation | 2 hours | Phases 2-4 |
| Phase 6: Polish | 2 hours | All phases |
| **Total** | **~19 hours** | |

## Approval

- [ ] Design approved
- [ ] Implementation approach approved
- [ ] Timeline accepted

---

*Once approved, proceed to tasks.md for detailed implementation checklist.*
