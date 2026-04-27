# Design: Trector Website Migration to Frappe

**Change ID:** `migrate-trector-website-to-frappe`  
**Last Updated:** February 19, 2026

---

## Technical Architecture

### Frappe Web Page Structure

Each page in Frappe uses the Web Page doctype with these key fields:
- `title` - Page title (appears in browser tab)
- `route` - URL path (e.g., "home", "fractional-cto-services")
- `published` - Boolean, must be 1 for public access
- `content_type` - "HTML" or "Page Builder"
- `main_section_html` - The actual HTML content
- `meta_description` - SEO description
- `insert_code` - Custom CSS/JS in `<head>`

### CSS Strategy

**Approach:** Create a comprehensive CSS file that mirrors all Tailwind classes used in the original site, prefixed with `trec-` to avoid conflicts.

**Delivery Method:** Include via `insert_code` field on each page, or use Website Settings to add globally.

---

## CSS Framework: `trector-styles.css`

```css
/* ==========================================================================
   TRECTOR STYLES - Custom CSS Framework for Frappe Migration
   Mirrors the Tailwind/React styling from www.trector.com
   ========================================================================== */

/* --------------------------------------------------------------------------
   CSS VARIABLES
   -------------------------------------------------------------------------- */
:root {
  /* Brand Colors */
  --trec-primary: #667eea;
  --trec-secondary: #764ba2;
  --trec-gradient: #6e64c6;
  --trec-accent: #f093fb;
  
  /* Gradient Variations */
  --trec-gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --trec-gradient-animated: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #6e64c6 50%, #667eea 75%, #764ba2 100%);
  
  /* Text Colors */
  --trec-text-primary: #111827;
  --trec-text-secondary: #4b5563;
  --trec-text-muted: #6b7280;
  
  /* Background Colors */
  --trec-bg-white: #ffffff;
  --trec-bg-gray-50: #f9fafb;
  --trec-bg-gray-100: #f3f4f6;
  --trec-bg-gray-900: #111827;
  
  /* Shadows */
  --trec-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --trec-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --trec-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --trec-shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --trec-shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  
  /* Border Radius */
  --trec-radius-sm: 0.25rem;
  --trec-radius-md: 0.5rem;
  --trec-radius-lg: 0.75rem;
  --trec-radius-xl: 1rem;
  --trec-radius-2xl: 1.5rem;
  --trec-radius-full: 9999px;
  
  /* Font */
  --trec-font-sans: 'Inter', system-ui, -apple-system, sans-serif;
}

/* --------------------------------------------------------------------------
   BASE RESET
   -------------------------------------------------------------------------- */
.trec-page * {
  box-sizing: border-box;
}

.trec-page {
  font-family: var(--trec-font-sans);
  color: var(--trec-text-primary);
  line-height: 1.5;
}

/* --------------------------------------------------------------------------
   TYPOGRAPHY
   -------------------------------------------------------------------------- */
.trec-text-xs { font-size: 0.75rem; line-height: 1rem; }
.trec-text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.trec-text-base { font-size: 1rem; line-height: 1.5rem; }
.trec-text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.trec-text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.trec-text-2xl { font-size: 1.5rem; line-height: 2rem; }
.trec-text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
.trec-text-4xl { font-size: 2.25rem; line-height: 2.5rem; }
.trec-text-5xl { font-size: 3rem; line-height: 1; }
.trec-text-6xl { font-size: 3.75rem; line-height: 1; }

.trec-font-normal { font-weight: 400; }
.trec-font-medium { font-weight: 500; }
.trec-font-semibold { font-weight: 600; }
.trec-font-bold { font-weight: 700; }

.trec-text-center { text-align: center; }
.trec-text-left { text-align: left; }
.trec-text-white { color: #ffffff; }
.trec-text-gray-600 { color: var(--trec-text-secondary); }
.trec-text-gray-700 { color: #374151; }
.trec-text-gray-900 { color: var(--trec-text-primary); }
.trec-text-primary { color: var(--trec-primary); }

/* Gradient Text */
.trec-gradient-text {
  background: var(--trec-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* --------------------------------------------------------------------------
   LAYOUT - Container & Grid
   -------------------------------------------------------------------------- */
.trec-container {
  width: 100%;
  max-width: 1280px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 640px) {
  .trec-container { padding-left: 1.5rem; padding-right: 1.5rem; }
}

@media (min-width: 1024px) {
  .trec-container { padding-left: 2rem; padding-right: 2rem; }
}

.trec-grid { display: grid; gap: 2rem; }
.trec-grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.trec-grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.trec-grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.trec-grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

@media (min-width: 768px) {
  .trec-md-grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .trec-md-grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (min-width: 1024px) {
  .trec-lg-grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .trec-lg-grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .trec-lg-grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}

.trec-flex { display: flex; }
.trec-flex-col { flex-direction: column; }
.trec-items-center { align-items: center; }
.trec-justify-center { justify-content: center; }
.trec-justify-between { justify-content: space-between; }
.trec-gap-2 { gap: 0.5rem; }
.trec-gap-4 { gap: 1rem; }
.trec-gap-6 { gap: 1.5rem; }
.trec-gap-8 { gap: 2rem; }
.trec-gap-12 { gap: 3rem; }

/* --------------------------------------------------------------------------
   SPACING
   -------------------------------------------------------------------------- */
.trec-p-4 { padding: 1rem; }
.trec-p-6 { padding: 1.5rem; }
.trec-p-8 { padding: 2rem; }
.trec-px-4 { padding-left: 1rem; padding-right: 1rem; }
.trec-px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
.trec-px-8 { padding-left: 2rem; padding-right: 2rem; }
.trec-py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
.trec-py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.trec-py-20 { padding-top: 5rem; padding-bottom: 5rem; }
.trec-py-24 { padding-top: 6rem; padding-bottom: 6rem; }

.trec-mb-2 { margin-bottom: 0.5rem; }
.trec-mb-4 { margin-bottom: 1rem; }
.trec-mb-6 { margin-bottom: 1.5rem; }
.trec-mb-8 { margin-bottom: 2rem; }
.trec-mb-12 { margin-bottom: 3rem; }
.trec-mb-16 { margin-bottom: 4rem; }

.trec-mx-auto { margin-left: auto; margin-right: auto; }
.trec-max-w-4xl { max-width: 56rem; }
.trec-max-w-5xl { max-width: 64rem; }
.trec-max-w-6xl { max-width: 72rem; }

/* --------------------------------------------------------------------------
   BACKGROUNDS
   -------------------------------------------------------------------------- */
.trec-bg-white { background-color: var(--trec-bg-white); }
.trec-bg-gray-50 { background-color: var(--trec-bg-gray-50); }
.trec-bg-gray-900 { background-color: var(--trec-bg-gray-900); }

/* Hero Gradient Background */
.trec-hero-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #6e64c6 50%, #667eea 75%, #764ba2 100%);
  background-size: 400% 400%;
  animation: trec-gradientShift 20s ease infinite;
}

/* Animated Gradient Keyframes */
@keyframes trec-gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Gradient Shimmer Effect */
.trec-gradient-shimmer {
  position: relative;
  overflow: hidden;
}

.trec-gradient-shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.08) 50%, transparent 100%);
  animation: trec-shimmer 8s infinite;
  pointer-events: none;
  z-index: 2;
}

@keyframes trec-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* Dots Pattern */
.trec-dots-pattern {
  background-image: radial-gradient(circle, rgba(102, 126, 234, 0.15) 1px, transparent 1px);
  background-size: 20px 20px;
}

/* --------------------------------------------------------------------------
   CARDS & SURFACES
   -------------------------------------------------------------------------- */
.trec-card {
  background: var(--trec-bg-white);
  border-radius: var(--trec-radius-xl);
  padding: 2rem;
  box-shadow: var(--trec-shadow-lg);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.trec-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--trec-shadow-2xl);
}

.trec-card-border-left-primary {
  border-left: 4px solid var(--trec-primary);
}

.trec-card-border-left-secondary {
  border-left: 4px solid var(--trec-secondary);
}

.trec-card-border-left-green {
  border-left: 4px solid #22c55e;
}

.trec-card-border-left-blue {
  border-left: 4px solid #3b82f6;
}

.trec-card-border-left-orange {
  border-left: 4px solid #f97316;
}

/* --------------------------------------------------------------------------
   BUTTONS
   -------------------------------------------------------------------------- */
.trec-btn {
  display: inline-block;
  padding: 1rem 2rem;
  border-radius: var(--trec-radius-lg);
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.trec-btn-white {
  background: white;
  color: var(--trec-primary);
  box-shadow: var(--trec-shadow-lg);
}

.trec-btn-white:hover {
  background: #f3f4f6;
  transform: scale(1.05);
  box-shadow: var(--trec-shadow-2xl);
}

.trec-btn-gradient {
  background: var(--trec-gradient-primary);
  color: white;
  box-shadow: var(--trec-shadow-lg);
}

.trec-btn-gradient:hover {
  transform: scale(1.05);
  box-shadow: var(--trec-shadow-2xl);
}

.trec-btn-outline {
  background: transparent;
  border: 2px solid white;
  color: white;
}

.trec-btn-outline:hover {
  background: white;
  color: var(--trec-primary);
}

/* --------------------------------------------------------------------------
   BADGES & PILLS
   -------------------------------------------------------------------------- */
.trec-badge {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: var(--trec-radius-full);
  font-size: 0.875rem;
  font-weight: 600;
}

.trec-badge-gradient {
  background: var(--trec-gradient-primary);
  color: white;
}

.trec-badge-white-glass {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(8px);
}

/* --------------------------------------------------------------------------
   ICONS
   -------------------------------------------------------------------------- */
.trec-icon-box {
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--trec-radius-2xl);
  font-size: 2rem;
  transition: transform 0.3s ease;
}

.trec-icon-box-primary {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(102, 126, 234, 0.1));
  color: var(--trec-primary);
}

.trec-icon-box-secondary {
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.4), rgba(118, 75, 162, 0.2));
  color: var(--trec-secondary);
}

.trec-icon-box-green {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  color: #22c55e;
}

.trec-icon-box-blue {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
  color: #3b82f6;
}

.trec-icon-box-orange {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.2), rgba(249, 115, 22, 0.1));
  color: #f97316;
}

/* --------------------------------------------------------------------------
   FLOATING ANIMATIONS
   -------------------------------------------------------------------------- */
@keyframes trec-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

@keyframes trec-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes trec-pulseGlow {
  0%, 100% { box-shadow: 0 0 15px rgba(102, 126, 234, 0.2); }
  50% { box-shadow: 0 0 30px rgba(118, 75, 162, 0.4); }
}

.trec-float { animation: trec-float 6s ease-in-out infinite; }
.trec-bounce-slow { animation: trec-bounce 4s ease-in-out infinite; }
.trec-bounce-slow-delay-1 { animation: trec-bounce 4s ease-in-out infinite; animation-delay: 1s; }
.trec-bounce-slow-delay-2 { animation: trec-bounce 4s ease-in-out infinite; animation-delay: 2s; }
.trec-pulse-glow { animation: trec-pulseGlow 3s ease-in-out infinite; }

/* Floating Badge */
.trec-floating-badge {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--trec-radius-xl);
  padding: 0.75rem 1rem;
  backdrop-filter: blur(8px);
  box-shadow: var(--trec-shadow-2xl);
}

/* Central Hero Icon Circle */
.trec-hero-icon-circle {
  width: 16rem;
  height: 16rem;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.3);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.05));
  backdrop-filter: blur(16px);
  box-shadow: var(--trec-shadow-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (min-width: 1024px) {
  .trec-hero-icon-circle {
    width: 20rem;
    height: 20rem;
  }
}

/* Pulsing Dots */
.trec-pulsing-dot {
  border-radius: 50%;
  box-shadow: var(--trec-shadow-lg);
}

.trec-pulsing-dot-yellow {
  width: 2rem;
  height: 2rem;
  background: #facc15;
}

.trec-pulsing-dot-green {
  width: 1.5rem;
  height: 1.5rem;
  background: #22c55e;
}

.trec-pulsing-dot-blue {
  width: 1rem;
  height: 1rem;
  background: #3b82f6;
}

/* --------------------------------------------------------------------------
   SECTION HEADERS
   -------------------------------------------------------------------------- */
.trec-section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.trec-section-header h2 {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--trec-text-primary);
  margin-bottom: 1rem;
}

@media (min-width: 1024px) {
  .trec-section-header h2 {
    font-size: 3rem;
  }
}

.trec-section-header p {
  font-size: 1.25rem;
  color: var(--trec-text-secondary);
}

/* --------------------------------------------------------------------------
   TESTIMONIALS
   -------------------------------------------------------------------------- */
.trec-testimonial-card {
  background: white;
  border-radius: var(--trec-radius-xl);
  padding: 2rem;
  box-shadow: var(--trec-shadow-lg);
  border-top: 3px solid var(--trec-primary);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.trec-testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--trec-shadow-xl);
}

.trec-stars {
  color: #facc15;
  font-size: 1.25rem;
  letter-spacing: 2px;
}

/* --------------------------------------------------------------------------
   FORMS
   -------------------------------------------------------------------------- */
.trec-form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: var(--trec-radius-lg);
  font-size: 1rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.trec-form-input:focus {
  outline: none;
  border-color: var(--trec-primary);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.trec-form-label {
  display: block;
  font-weight: 600;
  color: var(--trec-text-primary);
  margin-bottom: 0.5rem;
}

/* --------------------------------------------------------------------------
   FOOTER
   -------------------------------------------------------------------------- */
.trec-footer {
  background: var(--trec-bg-gray-900);
  color: #9ca3af;
  padding: 3rem 0;
}

.trec-footer h4 {
  color: white;
  font-weight: 600;
  margin-bottom: 1rem;
}

.trec-footer a {
  color: #9ca3af;
  text-decoration: none;
  transition: color 0.3s ease;
}

.trec-footer a:hover {
  color: var(--trec-primary);
}

/* --------------------------------------------------------------------------
   RESPONSIVE UTILITIES
   -------------------------------------------------------------------------- */
.trec-hidden { display: none; }
.trec-block { display: block; }

@media (min-width: 768px) {
  .trec-md-hidden { display: none; }
  .trec-md-block { display: block; }
  .trec-md-flex { display: flex; }
}

@media (min-width: 1024px) {
  .trec-lg-hidden { display: none; }
  .trec-lg-block { display: block; }
  .trec-lg-flex { display: flex; }
  .trec-lg-text-5xl { font-size: 3rem; }
  .trec-lg-text-6xl { font-size: 3.75rem; }
  .trec-lg-py-32 { padding-top: 8rem; padding-bottom: 8rem; }
}

/* --------------------------------------------------------------------------
   POSITIONING
   -------------------------------------------------------------------------- */
.trec-relative { position: relative; }
.trec-absolute { position: absolute; }
.trec-z-10 { z-index: 10; }
.trec-z-20 { z-index: 20; }
.trec-inset-0 { top: 0; right: 0; bottom: 0; left: 0; }
.trec-overflow-hidden { overflow: hidden; }

/* --------------------------------------------------------------------------
   REDUCED MOTION PREFERENCE
   -------------------------------------------------------------------------- */
@media (prefers-reduced-motion: reduce) {
  .trec-hero-gradient,
  .trec-gradient-shimmer::after,
  .trec-float,
  .trec-bounce-slow,
  .trec-bounce-slow-delay-1,
  .trec-bounce-slow-delay-2,
  .trec-pulse-glow {
    animation: none !important;
  }
}
```

---

## HTML Template Structure

### Homepage HTML Structure

```html
<!-- Font imports (add to Frappe Website Settings or page insert_code) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<div class="trec-page">
  <!-- HERO SECTION -->
  <section class="trec-hero-gradient trec-gradient-shimmer trec-relative trec-overflow-hidden trec-py-24 trec-lg-py-32 trec-text-white">
    <!-- Background Elements -->
    <div class="trec-dots-pattern trec-absolute trec-inset-0" style="opacity: 0.2;"></div>
    <div class="trec-absolute" style="top: 5rem; right: 2.5rem; width: 18rem; height: 18rem; border-radius: 50%; background: rgba(255,255,255,0.1); filter: blur(64px);"></div>
    <div class="trec-absolute" style="bottom: 5rem; left: 2.5rem; width: 24rem; height: 24rem; border-radius: 50%; background: rgba(118, 75, 162, 0.2); filter: blur(64px);"></div>
    
    <div class="trec-container trec-relative trec-z-10">
      <div class="trec-grid trec-lg-grid-cols-2 trec-items-center trec-gap-12">
        <!-- Left Column: Content -->
        <div>
          <div class="trec-badge-white-glass trec-mb-6">
            ⭐ Trusted by 500+ Businesses
          </div>
          <h1 class="trec-text-4xl trec-lg-text-6xl trec-font-bold trec-mb-6">
            Business Technology Consultant & 
            <span style="position: relative;">
              <span style="position: relative; z-index: 10;">Solutions</span>
              <span style="position: absolute; bottom: 0.5rem; left: 0; height: 0.75rem; width: 100%; background: rgba(250, 204, 21, 0.3);"></span>
            </span>
          </h1>
          <p class="trec-text-xl trec-mb-8" style="opacity: 0.9;">
            Expert business technology consultant helping small businesses...
          </p>
          <div class="trec-flex trec-gap-4" style="flex-wrap: wrap;">
            <a href="#services" class="trec-btn trec-btn-white">Our Services →</a>
            <a href="/technology-assessment" class="trec-btn trec-btn-outline">Let's Chat</a>
          </div>
        </div>
        
        <!-- Right Column: Visual -->
        <div class="trec-relative" style="min-height: 400px; display: flex; align-items: center; justify-content: center;">
          <!-- Floating badges and icon here -->
        </div>
      </div>
    </div>
  </section>
  
  <!-- Additional sections follow same pattern -->
</div>
```

---

## API Integration

### Updating Web Pages

```python
import requests

BASE_URL = "https://client.trector.com"
API_KEY = "6f489b8903b6fad"
API_SECRET = "3df65342ef2b596"
HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}

def update_page(route: str, html_content: str, meta_description: str = ""):
    """Update a Web Page with new HTML content."""
    url = f"{BASE_URL}/api/resource/Web Page/{route}"
    data = {
        "content_type": "HTML",
        "main_section_html": html_content,
        "meta_description": meta_description
    }
    response = requests.put(url, headers=HEADERS, json=data)
    return response.json()
```

---

## File Structure

```
frappe-migration/
├── README.md                    # Documentation
├── HOMEPAGE.md                  # Homepage notes
├── ISSUES-FOUND.md              # Known issues
├── css/
│   └── trector-styles.css       # Custom CSS framework
├── html/
│   ├── home.html                # Homepage HTML
│   ├── services/
│   │   ├── fractional-cto.html
│   │   ├── cloud-consulting.html
│   │   └── ...
│   └── blog/
│       ├── index.html
│       └── posts/
│           └── ...
└── scripts/
    ├── migrate_homepage.py
    ├── migrate_services.py
    └── migrate_blog.py
```

---

## Testing Checklist

### Visual Comparison Points

| Element | Original | Check |
|---------|----------|-------|
| Hero gradient animation | Shifts colors over 20s | ☐ |
| Hero badges bounce | 4s cycle with delays | ☐ |
| Rocket icon floats | 6s cycle | ☐ |
| Card hover lifts | translateY(-4px) | ☐ |
| Gradient text works | Purple-to-blue | ☐ |
| Icons display | All Font Awesome icons show | ☐ |
| Mobile responsive | Stacks properly on mobile | ☐ |

---

## Rollback Plan

If migration fails:
1. Frappe Web Pages can be reverted via API
2. Keep backup of all page content before updates
3. Original www.trector.com remains live during migration
4. Can restore placeholder content if needed
