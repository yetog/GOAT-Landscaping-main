# Green Empire Landscaping — Agent Handoff + Project History

**Repo:** https://github.com/yetog/Green-Empire
**Branch:** `master`
**Live URL:** https://zaylegend.com/green-empire/
**Client deadline:** March 28, 2026
**Local preview:** `python3 -m http.server 8080` → http://localhost:8080

---

## Deployment Architecture

The site is served as a **static subdirectory** on a personal VPS via nginx.

- **Server:** nginx on `zaylegend.com`
- **Served path:** `/green-empire/` subdirectory (not a subdomain)
- **Site root on server:** somewhere under nginx's webroot — confirm with `nginx -T | grep root` or check `/etc/nginx/sites-enabled/`
- **Deploy process:** pull latest from `yetog/Green-Empire` master → place files in nginx-served directory → no build step required (all HTML is pre-generated)

### Deployment Agent Instructions

When deploying updates:

1. Pull latest from GitHub:
   ```bash
   cd /path/to/green-empire   # confirm actual server path
   git pull origin master
   ```

2. Regenerate HTML (if `generate.py` or `site.config.json` changed):
   ```bash
   python3 generate.py
   ```
   All HTML is pre-generated. Static files only — no npm, no build tool.

3. No nginx restart needed for static file changes. If nginx config changes, run:
   ```bash
   nginx -t && systemctl reload nginx
   ```

4. Verify: https://zaylegend.com/green-empire/

### nginx Config Notes

The site lives at a subpath (`/green-empire/`), not the server root. All internal links in generated HTML use **relative paths** (e.g., `href="../../css/main.css"`) so no base-href or rewrite rules are needed. If you see 404s on assets, confirm the nginx `root` or `alias` directive points to the directory containing `index.html`, `css/`, `js/`, `images/`.

---

## Project Context

**Owner:** Zay — web & audio engineer, NYC/Philly/Barbados area, doing freelance client web work.

**What this is:** Site 1 of 3 Long Island service business websites.
1. **Green Empire Landscaping** — ✅ Built (this repo)
2. **Handyman site** — waiting on client logo + brand details
3. **Plumbing site** — waiting on client logo + brand details

**Reference:** Design modeled on the Neighborly franchise template (groundsguys.com). The goal is to beat those nationwide pages on Google by building locally-specific, LocalBusiness-schema-rich pages for Long Island cities.

**SEO play:** Each of the 20 `/service-areas/[city]/` pages targets `"landscaping [city] NY"`. Google proximity ranking favors locally-specific pages over franchise location directories.

---

## Current State (as of March 25, 2026) ← YOU ARE HERE

**Commits:** `master` branch on `yetog/Green-Empire`

### What's live and working:
- ✅ 7 services (complete overhaul from original 10 — see below)
- ✅ 20 service area city pages (Nassau + Suffolk County)
- ✅ Updated tagline: "Long Island's Premier Landscaping & Outdoor Renovation"
- ✅ "Certified & Insured" everywhere (was "Licensed & Insured")
- ✅ Real hours: Mon–Sat 7am–6pm (removed all "Open 24/7" references)
- ✅ 7 new FAQs matching current services
- ✅ Gallery section with 6 placeholder slots (ready for real photos)
- ✅ SMS opt-in checkbox on all forms
- ✅ "How Green Empire Can Help You" section on homepage
- ✅ Blog resources cards (3 stubs — pages not yet built)
- ✅ Service cards support photos (falls back to icon if no image provided)
- ✅ JSON-LD schema: LocalBusiness, BreadcrumbList, FAQPage, Service on all relevant pages
- ✅ UTF-8 encoding fix for Windows compatibility in generator

### Current services (7):
| Slug | Name |
|------|------|
| `back-yard-landscaping` | Back Yard Landscaping |
| `front-yard-landscaping` | Front Yard Landscaping |
| `paver-installation` | Paver Installation |
| `driveway-installation` | Driveway Installation |
| `patio-installation` | Patio Installation |
| `outdoor-living-spaces` | Outdoor Living Spaces |
| `landscape-design-installation` | Landscape Design & Installation |

### Page count: 38 total
| Path | Count |
|------|-------|
| `index.html` + root pages | ~5 |
| `services/index.html` + 7 detail pages | 8 |
| `service-areas/index.html` + 20 city pages | 21 |
| `about/`, `faq/`, `reviews/` | 3 |
| Legal pages | 3 |

---

## Version History (abridged)

### V1 — First draft (reference target)
- White nav, dark text links, clean local-business feel
- Small dark green top strip above nav
- Hero: single-column, content only — no form
- Booking form in dedicated section below stats (1fr 1.3fr grid)
- Service cards: 200px tall green gradient header block
- Zay's verdict: **best layout and visual feel — this is the reference target**

### V2 — Extracted Neighborly CSS (abandoned)
- Used 750KB groundsguys.com CSS, color-swapped variables
- **Failed:** Neighborly CSS requires React runtime to render. Layout collapsed without it.
- **Rule:** Never use `css/neighborly.css` or `footer.css` — in `.gitignore` for a reason.

### V3 — Generator rewrite + class mismatch (buggy intermediate)
- Built `generate.py` but CSS class names didn't match generator output
- Fixed by running a coverage script comparing every HTML class against CSS definitions

### V4 — "Unprofessional" polish pass (overcorrected)
- Full green nav, small icon bubbles on service cards, very dark CTA/stats
- Zay's verdict: "All the pages look unprofessional"
- Problems: green nav felt heavy, icon bubbles made cards look weak, near-black gradients killed energy

### V5 — Current
- White nav restored, original hero layout, 180px gradient header on service cards
- Booking section as dedicated block below stats
- All Ariel client feedback implemented (services overhaul, positioning, hours, FAQs)

---

## Architecture

### How it works
`generate.py` reads `site.config.json` → outputs all HTML files. **Never hand-edit the HTML.** Edit the config or the generator, then run `python3 generate.py`.

### Tech Stack
- **Generator:** `generate.py` (~1100 lines Python) — reads `site.config.json`
- **CSS:** `css/main.css` — ~1600 lines, custom, zero framework dependency
- **JS:** `js/main.js` — mobile menu, FAQ accordion, async Formspree submit
- **Forms:** Formspree — client must replace `YOURCODE` in `site.config.json > brand.formspreeId`
- **Schema:** LocalBusiness, BreadcrumbList, FAQPage, Service JSON-LD on all relevant pages
- **Hosting:** nginx static file serving at `/green-empire/` subpath on `zaylegend.com`

### Brand
- **Name:** Green Empire Landscaping
- **Phone:** (516) 701-3571 | Raw: `5167013571` *(will be replaced with CallRail number)*
- **Address:** 64 Hilton Ave, Hempstead, NY 11550
- **Email:** info@greenempirelandscaping.com
- **Hours:** Mon–Sat 7am–6pm
- **Primary:** `#1e4d2b` (dark forest green) → CSS var `--green`
- **Secondary:** `#6aad32` (lime green) → CSS var `--green-light`
- **Facebook:** https://www.facebook.com/GreenEmpireLawn/
- **Instagram:** https://www.instagram.com/greenempireconstruction/

---

## CSS Architecture

`css/main.css` — all styles in one file, no imports, no dependencies.

```css
:root {
  --green:        #1e4d2b;   /* main brand green */
  --green-dark:   #153820;   /* hover / dark variant */
  --green-light:  #6aad32;   /* lime accent — buttons, badges */
  --green-hover:  #5a9e2f;
  --gray-dark:    #374151;   /* body text */
  --gray-mid:     #6b7280;   /* secondary text */
  --gray-light:   #f9fafb;   /* section backgrounds */
}
```

### Key layout classes (must match generator output exactly)
| Class | What it is |
|-------|-----------|
| `.hero` | Full-height homepage hero, single-column content |
| `.hero-content` | Max-width text block inside hero |
| `.hero-badge` | Solid lime green pill badge |
| `.booking-section` | Homepage booking section (light bg, below stats) |
| `.booking-wrap` | 1fr 1.3fr grid — info left, form right |
| `.booking-card` / `.booking-form` | The form card component |
| `.stats-bar` + `.stats-grid` + `.stat` | Stats strip below hero |
| `.service-grid` | 3-col service card grid |
| `.service-card` + `.service-card-icon` + `.service-card-img` | Service card |
| `.gallery-grid` + `.gallery-item` + `.gallery-placeholder-slot` | Gallery section |
| `.blog-grid` + `.blog-card` | Blog resource cards |
| `.how-we-help` + `.how-we-help-content` | "How We Can Help" homepage section |
| `.split-section` + `.split-img` + `.split-content` | 50/50 Why Us section |
| `.check-list` | Bulleted list with SVG checkmark circles |
| `.review-grid` + `.review-card` | 3-col review cards |
| `.city-grid` + `.city-pill` | 5-col city links |
| `.content-sidebar-layout` | Service/city detail pages (content + sticky sidebar) |
| `.page-hero` | Inner page hero (gradient bg, not full-height) |
| `.section-header` | Centered section heading block |
| `.eyebrow` | Small uppercase label above headings |
| `.cta-banner` | Full-width CTA strip |
| `.features-grid` + `.feature-card` | 4-col feature cards (about page) |

---

## Critical Rules (learned the hard way)

1. **Never use the 750KB Neighborly CSS.** `css/neighborly.css` is `.gitignore`d for a reason.

2. **CSS class names must exactly match generator output.** Run this to check coverage:
   ```bash
   python3 -c "
   import glob, re
   html_classes = set(c for f in glob.glob('**/*.html', recursive=True) for c in re.findall(r'class=\"([^\"]+)\"', open(f).read()) for c in c.split())
   css_text = open('css/main.css').read()
   missing = [c for c in html_classes if f'.{c}' not in css_text]
   print('Missing:', missing[:20] if missing else 'None')
   "
   ```

3. **Never hand-edit HTML files.** They're all generated. Edit `site.config.json` or `generate.py`, then run `python3 generate.py`.

4. **Footer year uses `id="year"` in `js/main.js`.** Generator outputs `id="year"` — keep in sync.

5. **FAQ uses `.faq-question` / `.faq-answer`.** Generator, CSS, and JS all use these — don't shorten.

6. **Generator requires `encoding="utf-8"` on both file open calls** (config read + file write). Windows will silently break emoji in JSON otherwise.

---

## How to Regenerate

```bash
cd /path/to/green-empire
python3 generate.py
```

Regenerates all 38 pages. Takes ~1 second. Safe to run repeatedly.

**Add a service:** Add to `site.config.json > services`, regenerate.
**Add a city:** Add to `site.config.json > serviceAreas`, regenerate.
**Change phone/address/name:** Edit `site.config.json > brand`, regenerate.

---

## What Still Needs to Be Done

### Blocking / client must provide:
- [ ] **Formspree ID** — replace `YOURCODE` in `site.config.json > brand.formspreeId`, then regenerate + deploy
- [ ] **CallRail phone number** — replace `(516) 701-3571` in `site.config.json > brand.phone` + `brand.phoneRaw`, regenerate + deploy
- [ ] **Real photos** — client's contact is sending project photos; drop into `images/gallery/` and update `site.config.json > gallery[].src` fields, regenerate + deploy
- [ ] **Form destination decision** — email via Formspree or CRM (Jobber/HubSpot)?

### Build work remaining:
- [ ] **Blog stub pages** — links to `/blog/landscaping-zones/`, `/blog/outdoor-landscaping-ideas/`, `/blog/spring-lawn-tuneup/` exist on homepage but pages aren't built yet
- [ ] **Hero team photo** — slot ready at `/images/team-hero.jpg` if client wants crew photo in hero
- [ ] **Top nav review** — phone number + "Free Estimate" CTA appears 3× on page; consider consolidating
- [ ] **Logo improvement** — client asked about improving it; direction TBD
- [ ] **Thank-you page redirect** — add meta refresh back to homepage after form submission
- [ ] **Image optimization** — `hero-bg.jpg` is ~2.5 MB; compress before launch

### Post-launch:
- [ ] **Google Search Console** — submit sitemap after launch
- [ ] **GTM** — client handles this themselves
- [ ] **Google Business Profile** — already set up; verify hours/address match site

---

## File Structure

```
green-empire/
├── generate.py              ← Run this to rebuild all pages
├── site.config.json         ← ALL content lives here (single source of truth)
├── AGENTS.md                ← This file
├── index.html               ← Generated homepage
├── request-service.html     ← Generated full estimate form
├── thank-you.html           ← Generated
├── css/
│   └── main.css             ← All styles (~1600 lines, single file)
├── js/
│   └── main.js              ← Mobile menu, FAQ accordion, form handler
├── images/
│   ├── logo.png             ← Color logo
│   ├── logo-dark.png        ← B&W logo (alternate)
│   └── hero-bg.jpg          ← Hero background (~2.5 MB, needs compression)
├── about/index.html
├── faq/index.html
├── reviews/index.html
├── services/
│   ├── index.html
│   └── [7 slugs]/index.html
└── service-areas/
    ├── index.html
    └── [20 slugs]/index.html
```
