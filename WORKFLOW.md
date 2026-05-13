# Green Empire — Build Workflow & Agent Playbook

How this site was built. Use this as a repeatable playbook for new service business websites.

---

## Overview

**Pattern:** Config-driven static site generator
**Stack:** Python 3, vanilla CSS, vanilla JS, Formspree, static hosting (nginx or Netlify)
**Time to launch:** 1–2 sessions for a new client (config + CSS tuning + images)
**Pages generated:** 38–45 depending on service/city count

The core idea: `site.config.json` is the only file a non-developer needs to touch. The generator (`generate.py`) produces all HTML. Never hand-edit generated HTML.

---

## Phase 1 — Client Intake

Gather before starting. Everything feeds into `site.config.json`.

### Required:
- [ ] Business name
- [ ] Phone number (formatted + raw digits)
- [ ] Email address
- [ ] Physical address (street, city, state, zip)
- [ ] Business hours
- [ ] Domain name
- [ ] Facebook URL
- [ ] Instagram URL
- [ ] List of services (slug, name, description, hero text, 5 bullets each)
- [ ] List of service areas (city name, county, 4 nearby areas each)
- [ ] 3–5 customer reviews (name, location, text, star rating)
- [ ] 5–7 FAQs

### Nice to have:
- [ ] Logo (PNG, high resolution, transparent background preferred)
- [ ] Project photos (JPG/PNG, landscape orientation, 1200px+ wide)
- [ ] Google Maps embed URL
- [ ] Formspree ID (from formspree.io — free tier works)
- [ ] Brand colors (hex codes)

### Brand color defaults (if client doesn't have):
- Service businesses: dark primary + bright accent (e.g., `#1e4d2b` + `#6aad32`)
- CSS variables: `--green`, `--green-dark`, `--green-light`, `--green-hover`

---

## Phase 2 — Config Setup

Edit `site.config.json` only. Structure:

```json
{
  "brand": {
    "name": "...",
    "tagline": "...",
    "phone": "(555) 555-5555",
    "phoneRaw": "5555555555",
    "email": "...",
    "address": "...",
    "city": "...",
    "state": "NY",
    "zip": "...",
    "hours": "Mon–Sat 7am–6pm",
    "domain": "www.example.com",
    "formspreeId": "YOURCODE",
    "facebook": "https://...",
    "instagram": "https://...",
    "googleMapsEmbed": "https://...",
    "primaryColor": "#1e4d2b",
    "primaryDark": "#153820",
    "secondaryColor": "#6aad32",
    "secondaryDark": "#5a9e2f",
    "industry": "Landscaping",
    "industryLower": "landscaping"
  },
  "services": [...],
  "serviceAreas": [...],
  "reviews": [...],
  "faqs": [...],
  "gallery": [...]
}
```

**Service object structure:**
```json
{
  "slug": "patio-installation",
  "name": "Patio Installation",
  "shortName": "Patios",
  "icon": "☀️",
  "image": "/images/patio.jpg",
  "description": "One sentence for service card.",
  "heroText": "2-3 sentences for service page hero.",
  "bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4", "bullet 5"]
}
```

**Service area object structure:**
```json
{
  "slug": "hempstead",
  "name": "Hempstead",
  "county": "Nassau",
  "nearbyAreas": ["Garden City", "West Hempstead", "Uniondale", "Levittown"]
}
```

---

## Phase 3 — Generate & Review

```bash
python3 generate.py
python3 -m http.server 8080
# open http://localhost:8080
```

First-pass review checklist:
- [ ] Logo loads at correct size
- [ ] Hero image loads (not blank)
- [ ] All 7 service cards show
- [ ] City grid has all cities
- [ ] Form shows (even if not wired)
- [ ] Mobile menu opens/closes
- [ ] FAQ accordion works

CSS class coverage check (run if anything looks broken):
```bash
python3 -c "
import glob, re
html = set(c for f in glob.glob('**/*.html', recursive=True) for c in re.findall(r'class=\"([^\"]+)\"', open(f).read()) for c in c.split())
css = open('css/main.css').read()
missing = [c for c in html if f'.{c}' not in css]
print('Missing CSS:', missing[:20] if missing else 'None')
"
```

---

## Phase 4 — UI Customization

### CSS variables to update per client (top of `css/main.css`):
```css
:root {
  --green:        [primary color];
  --green-dark:   [darker shade];
  --green-light:  [accent/button color];
  --green-hover:  [hover state];
}
```

### Key sections in order of visual impact:
1. **Hero** — background image, h1 tagline, subheadline copy
2. **Stats bar** — verify numbers are accurate for the client
3. **Service cards** — ensure images are assigned (no gradient placeholders)
4. **Why Us section** — use team photo if available, otherwise a project photo
5. **Gallery** — fill all slots before demo
6. **Reviews** — real reviews are much stronger than placeholders

### Common fixes:
- Logo too small → increase `.nav-logo img { height: }` in CSS + `height=""` in nav function
- Section feels repetitive → audit for repeated phrases ("1 business hour", "Certified & Insured", trust signals that appear 3+ times)
- Service cards look weak → ensure `image` field is set in config for every service

---

## Phase 5 — Images

### Folder structure:
```
images/
├── logo.png              ← brand logo (transparent background)
├── logo-dark.png         ← alternate (optional)
├── hero-bg.jpg           ← hero background (1920px+ wide, compressed)
├── Hero.png              ← team/owner photo (for About page)
└── services/             ← optional subfolder for service images
    ├── patio.jpg
    └── ...
```

### Image assignment in `site.config.json`:
- Service card photo → `services[n].image: "/images/filename.jpg"`
- Gallery slot → `gallery[n].src: "/images/filename.jpg"`
- Hero bg → hardcoded in `generate.py` hero section
- About/Why Us → hardcoded in `generate.py` split-section

### When client has no photos:
1. Use AI-generated images (Gemini, Midjourney, etc.) — describe the service specifically
2. Prompts that work: `"professional [service name] project, suburban home, daytime, high quality photography"`
3. Assign the most relevant photo to each service — it's fine to reuse across 2–3 services
4. Gallery placeholders are styled dark green — acceptable for demo, swap before launch

### Image compression (before launch):
```bash
# Install: pip install Pillow
python3 -c "
from PIL import Image
import os
for f in ['images/hero-bg.jpg']:
    img = Image.open(f)
    img.save(f, quality=75, optimize=True)
    print(f, os.path.getsize(f) // 1024, 'KB')
"
```

---

## Phase 6 — Pre-Launch Checklist

### Content:
- [ ] All service descriptions are specific to the client (not generic)
- [ ] Phone number is correct everywhere (config is the source of truth)
- [ ] Address is correct
- [ ] Hours are correct (remove "24/7" if not applicable)
- [ ] "Licensed" vs "Certified" — match what the client actually has
- [ ] Franchise copy removed ("Each location independently owned" etc.)
- [ ] No placeholder text (YOURCODE, GOOGLE_REVIEW_LINK, etc.)
- [ ] Blog links go to real pages (or remove them)

### Technical:
- [ ] Formspree ID set and form tested (submit a real lead)
- [ ] Thank-you page redirect works
- [ ] Mobile menu opens/closes
- [ ] All nav links work (no 404s)
- [ ] Images load (no broken img tags)
- [ ] Google Maps embed loads (if using)
- [ ] Footer year updates (JS)

### SEO:
- [ ] LocalBusiness schema has correct address, phone, hours
- [ ] Canonical URLs match the production domain
- [ ] `openingHours` in schema matches displayed hours
- [ ] Each page has a unique `<title>` and `<meta description>`
- [ ] Sitemap submitted to Google Search Console after launch

### Deployment:
```bash
# On the server
cd /path/to/site
git pull origin master
python3 generate.py   # only if generate.py or site.config.json changed
# No server restart needed for static file changes
```

---

## Agent Prompt Template

Use this to brief a Claude agent on a new site build:

```
You are building a static service business website using the Green Empire pattern.

Repo reference: https://github.com/yetog/Green-Empire
Read AGENTS.md and WORKFLOW.md first.

The pattern:
- site.config.json = single source of truth for all content
- generate.py = reads config, outputs all HTML (never hand-edit HTML)
- css/main.css = all styles, no framework
- Run: python3 generate.py to rebuild

Client details:
- Business name: [NAME]
- Industry: [INDUSTRY]
- Phone: [PHONE]
- Address: [ADDRESS]
- Services: [LIST]
- Cities: [LIST]
- Brand colors: [PRIMARY] / [ACCENT]

Tasks:
1. Update site.config.json with all client details
2. Update CSS variables for client brand colors
3. Update generate.py if industry-specific copy changes are needed
4. Run generate.py and verify output
5. Report any issues or missing information

Rules:
- Never hand-edit generated HTML files
- CSS class names must match generator output exactly
- Always use encoding="utf-8" on file open calls (Windows compat)
- Run the CSS coverage check if anything looks broken
```

---

## What Takes the Most Time (and how to speed it up)

| Task | Time | Speed-up |
|---|---|---|
| Client intake / config population | 30–60 min | Use an intake form that maps directly to config fields |
| First CSS tuning pass | 30–45 min | Start from the Green Empire base CSS, change only variables |
| Finding/placing images | 20–40 min | Batch-generate AI images with specific prompts, rename clearly |
| Copy review + redundancy cleanup | 15–20 min | Audit for repeated phrases after generation |
| Form + deploy testing | 10–15 min | Keep a test Formspree endpoint ready |

**Total:** A clean build from intake to demo-ready is 2–4 hours.

---

## Session Log — Green Empire Build (March 2026)

### Session 1
- Pulled repo, did codebase analysis
- Identified UI gaps vs. Grounds Guys reference
- Added gallery section, SMS opt-in checkbox, service card photo support
- Built "How Green Empire Can Help" section
- Hero redesign (split layout) — built, shown, **reverted** at user request
- Pushed to GitHub

### Session 2
- Implemented all Ariel client feedback:
  - 10 services → 7 (outdoor renovation focus)
  - Tagline updated to "Landscaping & Outdoor Renovation"
  - "Licensed" → "Certified" everywhere
  - Removed all "Open 24/7" / "24/7" references
  - Updated FAQs (7 new questions)
  - Removed commercial/snow/mowing from all copy
- Deleted 10 old service directories, generated 7 new ones
- Pushed + wrote email reply to Ariel

### Session 3
- Added nginx deployment context to AGENTS.md
- Confirmed site live at https://zaylegend.com/green-empire/
- Added "How It Works" 3-step section to homepage
- Rebuilt thank-you page (full "What Happens Next" journey)
- Gallery placeholders redesigned (dark green, "Coming Soon" label)
- Removed emojis from service cards (clean gradient placeholder)
- Removed emojis from related-links and city service lists
- Logo increased to 72px
- Removed redundant "How We Help" prose section
- Fixed footer franchise disclaimer
- Nav dropdown: "Residential & Commercial" → "Our Services"
- Added review avatar initials (MT, SK, RA)
- Built 3 real blog pages with content (no more 404s)
- Mapped 8 Gemini AI photos across service cards, gallery, Why Us, About, hero
- All 6 gallery slots filled
- Redundant homepage copy trimmed (1-business-hour x4 → x1, trust signals consolidated)
- Hero background → stunning front yard photo
- Why Us → team of 4 in Green Empire shirts
- About page → Hero.png (owner/team member in branded shirt)
- Written MEETING-BRIEF.md and WORKFLOW.md

### Session 4 — Design Sync + Hero Carousel (May 2026)
- Removed top-bar phone banner from nav (was green bar above navigation)
- Added hero slideshow carousel (4 slides, fade transition, dot nav, pause on hover) driven by `heroSlides` array in `site.config.json`
- Replaced all emojis site-wide with inline Lucide SVGs (`_svg()` helper, no external CDN)
- Added hero brand name eyebrow (`<span class="hero-brand-name">`) above badge
- Logo height increased to 76px (was 60px, too small in 96px nav bar)
- Confirmed GEL and GEB are separate repos with separate codebases — changes are never synced between them without explicit instruction
- Live at `greenempireland.com` via GitHub + nginx

### Session 5 — Photo Swap, Form Fix & Zapier Cleanup (May 2026)
- Replaced all 4 AI-generated hero slides with 3 real landscaping photos (supplied via projects.zip)
- Added real project photos to Outdoor Living Spaces and Landscape Design & Installation service pages
- Updated homepage service cards and gallery to use real photos for those two services
- Restored original AI image in "Why Us / Meet Our Team" split section (was accidentally overwritten during bulk image swap — lesson: target replacements by section, not just filename)
- Removed "Text me updates about my estimate" SMS opt-in checkbox from all 29 pages and generate.py template
- Diagnosed Zapier errors: "Not enough credits" is a Quo SMS step failing — unrelated to form data capture; advised user to remove/disable the Quo step since SMS checkbox is gone
- Identified form field mismatch: homepage/service forms send `name`, but `request-service.html` sent `first_name` + `last_name` — Zapier was mapping `{{name}}` so full estimate page submissions showed blank name
- Standardized `request-service.html` and generate.py to use single `name` field across all forms
- Fixed encoding corruption introduced by bulk PowerShell file edit (PowerShell 5.1 `Get-Content` reads ANSI by default, corrupting UTF-8 multi-byte chars) — restored from git, redid edits using `[System.IO.File]::ReadAllText/WriteAllText` with explicit UTF-8 encoding
- **Upcoming:** GOAT Landscaping — new website, same stack, details TBD
