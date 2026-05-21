"""Knowledge Base seeding — populates categories and articles on startup."""
# ruff: noqa: E501, RUF001

from __future__ import annotations

import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.support.models import KBArticle, KBCategory

logger = logging.getLogger("tendril.support.kb_seed")


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


SEED_CATEGORIES = [
    {
        "name": "Getting Started",
        "slug": "getting-started",
        "description": "Learn the basics of Tendril and set up your first grow.",
        "icon": "Rocket",
        "sort_order": 0,
        "is_published": True,
    },
    {
        "name": "Grow Management",
        "slug": "grow-management",
        "description": "Managing grow cycles, environments, and plant health.",
        "icon": "Sprout",
        "sort_order": 1,
        "is_published": True,
    },
    {
        "name": "Sensors & Hardware",
        "slug": "sensors-hardware",
        "description": "Setting up ESP32 sensors, calibration, and connectivity.",
        "icon": "Cpu",
        "sort_order": 2,
        "is_published": True,
    },
    {
        "name": "Account & Billing",
        "slug": "account-billing",
        "description": "Managing your account, team members, and subscription.",
        "icon": "CreditCard",
        "sort_order": 3,
        "is_published": True,
    },
    {
        "name": "Troubleshooting",
        "slug": "troubleshooting",
        "description": "Common issues and how to resolve them.",
        "icon": "Wrench",
        "sort_order": 4,
        "is_published": True,
    },
]

SEED_ARTICLES = [
    # ─── Getting Started ──────────────────────────────────────
    {
        "category_slug": "getting-started",
        "title": "What is Tendril?",
        "slug": "what-is-tendril",
        "sort_order": 0,
        "tags": ["overview", "introduction"],
        "body_markdown": """# What is Tendril?

Tendril is an all-in-one grow management platform designed for indoor, outdoor, and hydroponic cultivators. It combines real-time sensor monitoring, automated environment controls, AI-powered plant health analysis, and detailed grow tracking into a single application.

## Key Features

- **Real-time Environment Monitoring** — Connect ESP32-based sensors to track temperature, humidity, VPD, CO₂, soil moisture, and more.
- **Grow Cycle Tracking** — Log every stage from seed to harvest with automated phase transitions.
- **AI Health Analysis** — Upload photos for instant plant health scoring and issue detection powered by Google Gemini.
- **Automation Rules** — Set up triggers to control fans, lights, and pumps based on sensor readings.
- **Nutrient Scheduling** — Track feedings, manage nutrient lines, and follow brand-specific feed charts.
- **Team Collaboration** — Invite team members with role-based access to manage grows together.
- **Mobile-First PWA** — Access your grow data from any device with our Progressive Web App.

## Who is Tendril For?

Tendril is built for home growers, commercial cultivators, and everyone in between. Whether you're running a single tent or managing a multi-room facility, Tendril scales to your needs.
""",
    },
    {
        "category_slug": "getting-started",
        "title": "Creating Your Account",
        "slug": "creating-your-account",
        "sort_order": 1,
        "tags": ["account", "signup"],
        "body_markdown": """# Creating Your Account

## How to Sign Up

1. Visit [tendril.maddscientist.com](https://tendril.maddscientist.com)
2. Click **Sign Up** on the login page
3. Enter your email address, display name, and create a password
4. Verify your email address via the confirmation link
5. You're in! Start by creating your first grow.

## Account Requirements

- A valid email address (used for notifications and password recovery)
- Password must be at least 8 characters with a mix of letters, numbers, and symbols

## What Happens Next?

After signup, you'll land on your dashboard. We recommend:
1. Setting up your profile in **Settings → Account**
2. Creating your first grow cycle
3. Connecting sensors (if you have hardware)
4. Exploring the Reference Database for strain information
""",
    },
    {
        "category_slug": "getting-started",
        "title": "Quick Start: Your First Grow",
        "slug": "quick-start-first-grow",
        "sort_order": 2,
        "tags": ["grow", "quickstart", "beginner"],
        "body_markdown": """# Quick Start: Your First Grow

Get up and running with Tendril in under 5 minutes.

## Step 1: Create a Grow Cycle

1. Navigate to **Dashboard → Grows**
2. Click **New Grow**
3. Choose your grow type (soil, hydro, coco, etc.)
4. Name your grow and select a strain from the reference database
5. Set your start date and expected harvest window

## Step 2: Add Your Environment

- If you have sensors, they'll auto-appear once connected via MQTT
- Without sensors, you can manually log readings

## Step 3: Track Daily Progress

- Add daily journal entries with photos
- Log nutrient feedings and water pH
- Update plant phase (seedling → veg → flower → harvest)

## Step 4: Harvest & Review

When your grow completes, Tendril compiles a full grow report with averages, timelines, and yield data for future reference.
""",
    },
    {
        "category_slug": "getting-started",
        "title": "Where to Find Key Features",
        "slug": "where-to-find-features",
        "sort_order": 3,
        "tags": ["navigation", "ui", "guide"],
        "body_markdown": """# Where to Find Key Features

## Dashboard Navigation

| Section | Location | Description |
|---------|----------|-------------|
| Grows | Sidebar → Grows | Active and past grow cycles |
| Sensors | Sidebar → Sensors | Live readings from connected hardware |
| Analytics | Sidebar → Analytics | Charts and trends for environment data |
| Strains | Sidebar → Library → Strains | Your personal strain library |
| Reference | Sidebar → Library → Reference | Global strain and nutrient database |
| Automation | Sidebar → Automation | Environment control rules |
| Settings | Sidebar → Settings | Account, team, and security |
| Support | Sidebar → Support | Tickets, knowledge base, and forum |

## Quick Actions

- **New Grow** — Dashboard home or Grows page
- **Add Sensor** — Sensors page → Add Device
- **Upload Photo** — Inside any grow cycle → Health tab
- **Submit Ticket** — Support → Submit a Ticket

## Mobile Access

Tendril is a PWA. Add it to your home screen on iOS/Android for an app-like experience with offline support.
""",
    },
    {
        "category_slug": "getting-started",
        "title": "When to Use Each Grow Type",
        "slug": "when-to-use-grow-types",
        "sort_order": 4,
        "tags": ["grow-types", "beginner", "comparison"],
        "body_markdown": """# When to Use Each Grow Type

Tendril supports multiple grow methodologies. Here's when to choose each:

## Soil (Traditional)

**Best for:** Beginners, outdoor grows, organic cultivation
- Forgiving of pH fluctuations
- Natural microbial life supports plant health
- Lower startup cost

## Coco Coir

**Best for:** Intermediate growers wanting faster growth than soil
- Treated like hydro (pH and EC management required)
- Faster root development than soil
- Excellent drainage and aeration

## Deep Water Culture (DWC/RDWC)

**Best for:** Experienced growers seeking maximum growth speed
- Roots submerged in oxygenated nutrient solution
- Fastest vegetative growth of any method
- Requires careful monitoring of dissolved oxygen and EC

## NFT (Nutrient Film Technique)

**Best for:** Commercial operations with many plants
- Thin film of nutrients flows over roots
- Highly efficient water usage
- Requires reliable pumps and backup systems

## Ebb & Flow

**Best for:** Balanced approach between soil and full hydro
- Periodic flooding delivers nutrients to root zone
- Good for larger plants with established root systems
- Simple to automate with timers

## Living Soil / No-Till

**Best for:** Organic purists, sustainability-focused growers
- Build a living ecosystem in your soil
- Minimal inputs after initial setup
- Produces complex terpene profiles
""",
    },
    # ─── Grow Management ──────────────────────────────────────
    {
        "category_slug": "grow-management",
        "title": "Understanding Grow Phases",
        "slug": "understanding-grow-phases",
        "sort_order": 0,
        "tags": ["phases", "lifecycle", "tracking"],
        "body_markdown": """# Understanding Grow Phases

Tendril tracks your plant through its entire lifecycle with customized phases per grow type.

## Standard Phases

1. **Germination** — Seed cracking and taproot emergence (2-7 days)
2. **Seedling** — First leaves emerge, establishing root system (1-2 weeks)
3. **Vegetative** — Rapid growth, building structure (2-8 weeks)
4. **Transition** — Switching to flower light cycle (1-2 weeks)
5. **Flowering** — Bud development and maturation (6-12 weeks)
6. **Flush** — Final 1-2 weeks, plain water only
7. **Harvest** — Chop, dry, and cure
8. **Curing** — 2-8 weeks in jars for flavor development

## Phase Transitions

Tendril can automatically suggest phase transitions based on:
- Days since last phase change
- Average environmental readings
- Photo analysis (AI-detected maturity indicators)

You can always override and manually advance phases.

## Phase-Specific Guidance

Each phase shows tailored recommendations for:
- Target temperature and humidity (VPD)
- Light schedule (DLI)
- Nutrient strength (EC/PPM)
- Watering frequency
""",
    },
    {
        "category_slug": "grow-management",
        "title": "How to Read VPD Charts",
        "slug": "how-to-read-vpd-charts",
        "sort_order": 1,
        "tags": ["vpd", "environment", "charts"],
        "body_markdown": """# How to Read VPD Charts

## What is VPD?

Vapor Pressure Deficit (VPD) measures the difference between how much moisture the air *can* hold and how much it *currently* holds. It directly affects transpiration rate — how fast plants move water from roots to leaves.

## Why VPD Matters

- **Too low (<0.4 kPa):** Air is saturated, stomata close, risk of mold
- **Too high (>1.6 kPa):** Plants lose water faster than roots can uptake, stress and wilting
- **Sweet spot:** Depends on growth phase

## Target VPD by Phase

| Phase | VPD Range (kPa) | Temp Range | RH Range |
|-------|-----------------|------------|----------|
| Seedling/Clone | 0.4 – 0.8 | 72-78°F | 65-75% |
| Vegetative | 0.8 – 1.2 | 75-82°F | 55-65% |
| Early Flower | 1.0 – 1.4 | 75-80°F | 50-60% |
| Late Flower | 1.2 – 1.6 | 72-78°F | 40-50% |

## Reading VPD in Tendril

Tendril automatically calculates VPD from your temperature and humidity sensors. The Analytics page shows:
- Current VPD reading with zone indicator (green/yellow/red)
- Historical VPD trendline
- Alerts when VPD leaves your target range
""",
    },
    {
        "category_slug": "grow-management",
        "title": "Nutrient Tracking & Feed Charts",
        "slug": "nutrient-tracking-feed-charts",
        "sort_order": 2,
        "tags": ["nutrients", "feeding", "ec", "ppm"],
        "body_markdown": """# Nutrient Tracking & Feed Charts

## Logging Feedings

1. Navigate to your active grow cycle
2. Open the **Nutrients** tab
3. Click **Log Feeding**
4. Enter: nutrient products used, amounts (mL/gal), water volume, pH in, pH out, EC/PPM

## Using Feed Charts

Tendril includes built-in feed charts for popular nutrient lines:
- General Hydroponics Flora Series
- Advanced Nutrients pH Perfect
- Jack's 3-2-1
- Fox Farm Trio
- Canna Coco
- Athena Pro Line

Access them via **Reference → Feed Charts** and select your brand and medium.

## Best Practices

- **Always pH after mixing** — Target 5.8-6.2 for hydro, 6.2-6.8 for soil
- **Start at half strength** — Increase based on plant response
- **Track runoff EC** — Rising EC means buildup; flush if needed
- **Log every feeding** — Tendril uses this data to correlate growth with nutrition
""",
    },
    {
        "category_slug": "grow-management",
        "title": "AI Plant Health Analysis",
        "slug": "ai-plant-health-analysis",
        "sort_order": 3,
        "tags": ["ai", "health", "photos", "diagnosis"],
        "body_markdown": """# AI Plant Health Analysis

## How It Works

Tendril uses Google Gemini vision AI to analyze photos of your plants and provide:
- **Health Score** (0-100) — Overall plant condition
- **Issue Detection** — Nutrient deficiencies, pests, environmental stress
- **Recommended Actions** — Specific steps to address detected problems

## Taking Good Photos

For best results:
- Use natural or full-spectrum lighting
- Capture the whole plant AND close-ups of problem areas
- Include top and bottom of leaves
- Avoid flash (causes glare and color distortion)
- Upload multiple angles for comprehensive analysis

## Interpreting Results

| Score | Meaning |
|-------|---------|
| 90-100 | Excellent health, no issues detected |
| 70-89 | Good health, minor issues noted |
| 50-69 | Moderate issues requiring attention |
| 30-49 | Significant problems, action needed immediately |
| 0-29 | Critical condition, emergency intervention required |

## Limitations

- AI analysis is a tool, not a replacement for grower experience
- Works best with clear, well-lit photos
- May not detect root zone issues without visible above-ground symptoms
""",
    },
    {
        "category_slug": "grow-management",
        "title": "Automation Rules & Triggers",
        "slug": "automation-rules-triggers",
        "sort_order": 4,
        "tags": ["automation", "triggers", "iot"],
        "body_markdown": """# Automation Rules & Triggers

## What Are Automation Rules?

Rules let you automate actions based on sensor readings. When a condition is met, Tendril triggers an action — like turning on an exhaust fan when temperature exceeds 82°F.

## Creating a Rule

1. Go to **Automation** in the sidebar
2. Click **New Rule**
3. Define the trigger condition (sensor, threshold, operator)
4. Define the action (device, command)
5. Set optional cooldown period and schedules

## Example Rules

| Trigger | Action | Cooldown |
|---------|--------|----------|
| Temp > 82°F | Turn on exhaust fan | 5 min |
| Humidity > 70% | Turn on dehumidifier | 10 min |
| Soil moisture < 30% | Send notification | 30 min |
| Light off for 12h | Turn on light | None |
| VPD > 1.5 kPa | Activate humidifier | 5 min |

## Rule Types

- **Threshold** — Triggers when a value crosses a boundary
- **Schedule** — Triggers at specific times (light cycles, feeding reminders)
- **Compound** — Multiple conditions must be true (AND/OR logic)

## Safety Limits

All rules have configurable:
- Maximum activation frequency (cooldown)
- Active time windows (only run during certain hours)
- Override capability (manually disable without deleting)
""",
    },
    # ─── Sensors & Hardware ───────────────────────────────────
    {
        "category_slug": "sensors-hardware",
        "title": "Supported ESP32 Sensor Boards",
        "slug": "supported-esp32-sensors",
        "sort_order": 0,
        "tags": ["esp32", "hardware", "sensors"],
        "body_markdown": """# Supported ESP32 Sensor Boards

## Official Tendril Sensor Firmware

Tendril provides open-source firmware for ESP32-based sensor boards:

### Environment Monitor
- **Sensors:** BME280 (temp/humidity/pressure), SCD40 (CO₂), BH1750 (light)
- **Use case:** General tent/room environment monitoring
- **Board:** ESP32-WROOM-32

### Soil Basic
- **Sensors:** Capacitive soil moisture
- **Use case:** Simple soil moisture monitoring
- **Board:** ESP32-C3 Mini

### Soil Pro
- **Sensors:** Soil moisture, soil temperature (DS18B20), EC probe
- **Use case:** Advanced soil monitoring with EC
- **Board:** ESP32-WROOM-32

### Hydro Monitor
- **Sensors:** pH probe, EC/TDS, water temperature, water level
- **Use case:** Reservoir monitoring for hydroponic systems
- **Board:** ESP32-WROOM-32

### Aero Monitor
- **Sensors:** BME280, particulate matter (PM2.5), VOC
- **Use case:** Air quality monitoring for sealed rooms
- **Board:** ESP32-S3

## Connectivity

All sensors connect via WiFi to your MQTT broker, which Tendril reads in real-time. Configuration is done through a web portal on first boot (captive portal).
""",
    },
    {
        "category_slug": "sensors-hardware",
        "title": "How to Connect Your First Sensor",
        "slug": "how-to-connect-first-sensor",
        "sort_order": 1,
        "tags": ["setup", "mqtt", "wifi", "beginner"],
        "body_markdown": """# How to Connect Your First Sensor

## Prerequisites

- An ESP32 sensor board with Tendril firmware flashed
- WiFi network (2.4GHz — ESP32 doesn't support 5GHz)
- Your Tendril account

## Step 1: Power On

Connect your ESP32 board via USB-C or a 5V power supply. The LED will blink indicating setup mode.

## Step 2: Connect to Setup Portal

1. On your phone/laptop, find the WiFi network named `Tendril-XXXX`
2. Connect to it (no password needed)
3. A captive portal will open automatically

## Step 3: Configure WiFi & MQTT

In the setup portal:
1. Select your home WiFi network and enter password
2. Enter MQTT broker details:
   - **Host:** Your Tendril MQTT server address
   - **Port:** 1883 (or 8883 for TLS)
   - **Username/Password:** From your Tendril dashboard → Sensors → Add Device
3. Click Save & Reboot

## Step 4: Verify in Tendril

1. Go to **Dashboard → Sensors**
2. Your new device should appear within 30 seconds
3. Click it to see live readings
4. Assign it to a grow cycle or zone

## Troubleshooting

- **Device not appearing?** Check WiFi password and MQTT credentials
- **Readings are 0?** Sensor may need calibration (see calibration guide)
- **Intermittent connection?** Move device closer to WiFi router
""",
    },
    {
        "category_slug": "sensors-hardware",
        "title": "Sensor Calibration Guide",
        "slug": "sensor-calibration-guide",
        "sort_order": 2,
        "tags": ["calibration", "accuracy", "ph", "ec"],
        "body_markdown": """# Sensor Calibration Guide

## Why Calibrate?

Sensors drift over time. Regular calibration ensures accurate readings that you can trust for making grow decisions.

## Temperature & Humidity (BME280)

These sensors are factory-calibrated and rarely need adjustment. If readings seem off:
- Compare against a known-accurate thermometer
- Apply offset in Tendril: Sensors → Device → Settings → Offset

## Soil Moisture (Capacitive)

1. Take a reading in completely dry air → note the "dry" value
2. Submerge sensor tip in water → note the "wet" value
3. Enter both in Tendril: Sensors → Device → Calibrate
4. Tendril maps the raw range to 0-100%

## pH Probe

Calibrate monthly with buffer solutions:
1. Rinse probe in distilled water
2. Place in pH 7.0 buffer → enter reading in calibration UI
3. Rinse again
4. Place in pH 4.0 buffer → enter reading
5. Two-point calibration is now active

## EC/TDS Probe

1. Rinse in distilled water
2. Place in 1413 µS/cm calibration solution
3. Enter reading in calibration UI
4. For higher ranges, also calibrate at 12880 µS/cm

## Calibration Schedule

| Sensor | Frequency |
|--------|-----------|
| Temperature/Humidity | Every 6 months |
| Soil Moisture | After each grow cycle |
| pH | Monthly |
| EC/TDS | Monthly |
| CO₂ | Yearly (auto-calibrates outdoors) |
""",
    },
    # ─── Account & Billing ────────────────────────────────────
    {
        "category_slug": "account-billing",
        "title": "Managing Team Members",
        "slug": "managing-team-members",
        "sort_order": 0,
        "tags": ["team", "roles", "access"],
        "body_markdown": """# Managing Team Members

## Adding Team Members

1. Go to **Settings → Team**
2. Click **Invite Member**
3. Enter their email and select a role
4. They'll receive an email invitation to join your workspace

## Roles & Permissions

| Role | Capabilities |
|------|-------------|
| **Owner** | Full access, billing, can delete workspace |
| **Admin** | Manage members, all grow operations, settings |
| **Member** | View and edit grows, log data, run AI analysis |
| **Viewer** | Read-only access to all grow data |

## Removing Members

1. Go to **Settings → Team**
2. Find the member in the list
3. Click the remove button (trash icon)
4. Confirm removal

Removed members immediately lose access. Their logged data (journal entries, feedings) remains in the system attributed to them.

## Limits

Team member limits depend on your plan:
- **Free:** 1 member (owner only)
- **Pro:** Up to 5 members
- **Commercial:** Unlimited members
""",
    },
    {
        "category_slug": "account-billing",
        "title": "Subscription Plans & Features",
        "slug": "subscription-plans-features",
        "sort_order": 1,
        "tags": ["billing", "plans", "pricing"],
        "body_markdown": """# Subscription Plans & Features

## Available Plans

### Free Tier
- 1 active grow cycle
- 2 connected sensors
- Basic analytics (7-day history)
- Community forum access
- AI health analysis (3/month)

### Pro ($9/month)
- Unlimited grow cycles
- 10 connected sensors
- Full analytics (unlimited history)
- Automation rules (10 max)
- AI health analysis (30/month)
- Priority support
- 5 team members

### Commercial ($29/month)
- Everything in Pro
- Unlimited sensors
- Unlimited automation rules
- Unlimited AI analysis
- Custom branding
- API access
- Unlimited team members
- Compliance reports
- Dedicated support

## Changing Plans

1. Go to **Settings → Billing**
2. Click **Change Plan**
3. Select your new plan
4. Changes take effect immediately (prorated)

## Cancellation

You can cancel anytime. Your data is retained for 30 days after cancellation, then permanently deleted.
""",
    },
    {
        "category_slug": "account-billing",
        "title": "Security & Two-Factor Authentication",
        "slug": "security-two-factor-auth",
        "sort_order": 2,
        "tags": ["security", "2fa", "password"],
        "body_markdown": """# Security & Two-Factor Authentication

## Password Requirements

- Minimum 8 characters
- Must include uppercase, lowercase, numbers, and symbols
- Cannot be a commonly breached password
- Changed passwords take effect immediately on all devices

## Enabling 2FA (TOTP)

1. Go to **Settings → Security**
2. Click **Enable Two-Factor Authentication**
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, 1Password)
4. Enter the 6-digit code to verify
5. Save your backup codes in a secure location

## Session Management

View and revoke active sessions:
- **Settings → Security → Active Sessions**
- See device type, IP address, and last activity
- Click **Revoke** to immediately end a session

## API Tokens

For integrations and automation:
- Generate tokens in **Settings → Security → API Tokens**
- Tokens have configurable expiry
- Revoke tokens instantly if compromised

## Best Practices

- Use a unique password for Tendril
- Enable 2FA for all team members
- Review active sessions weekly
- Rotate API tokens quarterly
""",
    },
    # ─── Troubleshooting ──────────────────────────────────────
    {
        "category_slug": "troubleshooting",
        "title": "Sensor Not Showing Data",
        "slug": "sensor-not-showing-data",
        "sort_order": 0,
        "tags": ["sensor", "connectivity", "debug"],
        "body_markdown": """# Sensor Not Showing Data

## Quick Checks

1. **Is the device powered on?** Check for LED activity
2. **Is WiFi connected?** The device should not be broadcasting its own SSID (setup mode)
3. **Is MQTT connected?** Check your MQTT broker's client list

## Step-by-Step Diagnosis

### Check Physical Connection
- Verify USB-C or power supply is firmly connected
- Check sensor wire connections (loose jumper wires are common)
- Look for corrosion on probe connectors

### Check WiFi
- Ensure your router is on and broadcasting 2.4GHz
- Device must be within WiFi range (typically 30-50 feet indoors)
- Too many devices on network? Some routers limit connections

### Check MQTT
- Verify MQTT credentials haven't changed
- Check if MQTT broker is running (Tendril dashboard → System Status)
- Test with an MQTT client (like MQTT Explorer) to verify messages are publishing

### Reset Device
If all else fails:
1. Hold the RESET button for 10 seconds
2. Device enters setup mode (broadcasts Tendril-XXXX WiFi)
3. Reconfigure WiFi and MQTT credentials
4. Device should reconnect within 30 seconds

## Still Not Working?

Open a support ticket with:
- Device type and serial number
- When it last worked
- Any changes to your network
""",
    },
    {
        "category_slug": "troubleshooting",
        "title": "Pages Not Loading or Errors",
        "slug": "pages-not-loading-errors",
        "sort_order": 1,
        "tags": ["errors", "loading", "pwa", "cache"],
        "body_markdown": """# Pages Not Loading or Errors

## "This page couldn't load" Error

This usually means the page failed to fetch data from the API.

### Quick Fixes

1. **Check your internet connection** — Try loading another website
2. **Refresh the page** — Pull down to refresh on mobile, or Ctrl+R / Cmd+R on desktop
3. **Clear PWA cache:**
   - Open browser DevTools → Application → Storage → Clear Site Data
   - Or uninstall and reinstall the PWA
4. **Check if the service is up** — Visit the status page or try another browser

### If the Error Persists

- **Try incognito/private mode** — Rules out extension or cache issues
- **Check browser console** (F12 → Console) for specific error messages
- **Log out and log back in** — Your session token may have expired

## Common API Errors

| Error | Meaning | Fix |
|-------|---------|-----|
| 401 Unauthorized | Session expired | Log out and back in |
| 403 Forbidden | Insufficient permissions | Check your role |
| 404 Not Found | Resource doesn't exist | May have been deleted |
| 500 Server Error | Backend issue | Wait and retry; report if persistent |
| Network Error | Can't reach API | Check internet; API may be down |

## Reporting Issues

If the problem persists, submit a support ticket including:
- What page/action caused the error
- Browser and device information
- Screenshot of any error messages
- Time when the error occurred
""",
    },
    {
        "category_slug": "troubleshooting",
        "title": "Incorrect Sensor Readings",
        "slug": "incorrect-sensor-readings",
        "sort_order": 2,
        "tags": ["calibration", "accuracy", "drift"],
        "body_markdown": """# Incorrect Sensor Readings

## Common Causes

### Temperature Reading Too High/Low
- **Sensor in direct light** — Shield from grow lights, which radiate heat
- **Too close to heat source** — Mount away from ballasts, fans, heaters
- **Needs calibration offset** — Apply in Sensors → Device → Settings

### Humidity Always 99%
- **Condensation on sensor** — Mount away from humidifiers, water sources
- **Sensor damaged** — BME280 humidity element degrades if exposed to liquid water
- **Replace sensor** if cleaning doesn't help

### Soil Moisture Stuck at 0% or 100%
- **Needs calibration** — See Calibration Guide
- **Probe degraded** — Capacitive probes last 6-12 months in soil
- **Wrong depth** — Insert to the recommended depth marked on the probe

### pH Reading Drifting
- **Needs monthly calibration** — Buffer solutions required
- **Probe storage** — Keep in KCl solution, never let dry out
- **Probe end of life** — pH probes typically last 12-18 months

## Applying Offsets

For sensors that read consistently off by a fixed amount:
1. Go to **Sensors → [Device] → Settings**
2. Enter the offset value (e.g., -2.0°F if it reads 2° high)
3. Save — readings will be adjusted automatically

## When to Replace

If calibration doesn't fix the issue and readings are wildly inaccurate, the sensor may need physical replacement. Contact support for warranty claims on Tendril hardware.
""",
    },
    {
        "category_slug": "troubleshooting",
        "title": "Automation Rules Not Firing",
        "slug": "automation-rules-not-firing",
        "sort_order": 3,
        "tags": ["automation", "triggers", "debug"],
        "body_markdown": """# Automation Rules Not Firing

## Checklist

### 1. Is the Rule Enabled?
- Go to **Automation** and check the toggle next to your rule
- Rules can be disabled without being deleted

### 2. Is the Condition Being Met?
- Check current sensor readings against your threshold
- Rules only fire when the value *crosses* the threshold, not while it stays above/below

### 3. Is the Cooldown Active?
- After firing, rules won't fire again until the cooldown period expires
- Check the "Last Fired" timestamp on the rule detail page

### 4. Is the Device Online?
- The target device must be connected and responding
- Check Sensors page for device status (green = online)

### 5. Is the Schedule Window Active?
- Rules with time restrictions only fire during their configured hours
- Verify the time zone is correct in Settings

## Testing a Rule

1. Open the rule and click **Test**
2. This fires the action immediately regardless of conditions
3. Useful to verify the device responds correctly

## Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Never fires | Threshold too extreme | Lower/raise threshold |
| Fires too often | Cooldown too short | Increase cooldown |
| Fires but no effect | Device offline | Check device connection |
| Wrong time | Timezone mismatch | Fix in Settings → Account |
""",
    },
    {
        "category_slug": "troubleshooting",
        "title": "How to Contact Support",
        "slug": "how-to-contact-support",
        "sort_order": 4,
        "tags": ["support", "tickets", "help"],
        "body_markdown": """# How to Contact Support

## Support Channels

### Support Tickets (Recommended)
1. Go to **Support → Submit a Ticket**
2. Select a category (Technical, Billing, Bug Report, Feature Request)
3. Describe your issue with as much detail as possible
4. Attach screenshots or logs if applicable
5. We respond within 24 hours (Pro/Commercial: 4 hours)

### Knowledge Base
Search our growing collection of articles before submitting a ticket — your answer may already be here!

### Community Forum
Ask questions and help others in **Support → Community Forum**. Community moderators and staff monitor regularly.

## What to Include in a Ticket

- **What happened** — Clear description of the issue
- **What you expected** — What should have happened instead
- **Steps to reproduce** — How can we trigger the same issue?
- **Device/Browser info** — OS, browser, app version
- **Screenshots** — Visual evidence helps us resolve faster

## Response Times

| Plan | First Response | Resolution Target |
|------|---------------|-------------------|
| Free | 48 hours | Best effort |
| Pro | 24 hours | 72 hours |
| Commercial | 4 hours | 24 hours |

## Emergency Issues

For service outages or security concerns, email security@tendril.maddscientist.com directly.
""",
    },
]


async def sync_kb_seed(session: AsyncSession) -> dict:
    """Seed KB categories and articles. Returns counts of new items added."""
    cat_added = 0
    art_added = 0

    # Upsert categories
    category_map: dict[str, KBCategory] = {}
    for cat_data in SEED_CATEGORIES:
        existing = (
            await session.execute(select(KBCategory).where(KBCategory.slug == cat_data["slug"]))
        ).scalar_one_or_none()

        if existing:
            for k, v in cat_data.items():
                setattr(existing, k, v)
            category_map[cat_data["slug"]] = existing
        else:
            cat = KBCategory(**cat_data)
            session.add(cat)
            category_map[cat_data["slug"]] = cat
            cat_added += 1

    await session.flush()  # Ensure category IDs are generated

    # Upsert articles
    for art_data in SEED_ARTICLES:
        cat_slug = art_data.pop("category_slug")
        category = category_map.get(cat_slug)
        if not category:
            art_data["category_slug"] = cat_slug  # Restore for safety
            continue

        existing = (
            await session.execute(select(KBArticle).where(KBArticle.slug == art_data["slug"]))
        ).scalar_one_or_none()

        if existing:
            for k, v in art_data.items():
                setattr(existing, k, v)
            existing.category_id = category.id
        else:
            article = KBArticle(**art_data, category_id=category.id)
            session.add(article)
            art_added += 1

        art_data["category_slug"] = cat_slug  # Restore for next run

    await session.commit()
    logger.info("KB seed complete: %d categories, %d articles added", cat_added, art_added)
    return {"categories_added": cat_added, "articles_added": art_added}
