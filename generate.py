#!/usr/bin/env python3
"""
GOAT Landscaping — Static Site Generator
Run: python3 generate.py
Generates all pages from site.config.json + templates
"""

import json, os, re, shutil

# ── Load config ───────────────────────────────────────────
with open("site.config.json", encoding="utf-8") as f:
    cfg = json.load(f)

B = cfg["brand"]
SERVICES = cfg["services"]
AREAS = cfg["serviceAreas"]
REVIEWS = cfg["reviews"]
FAQS = cfg["faqs"]
GALLERY = cfg.get("gallery", [])

PHONE = B["phone"]
PHONE_RAW = B["phoneRaw"]
NAME = B["name"]
ADDRESS = f"{B['address']}, {B['city']}, {B['state']} {B['zip']}"
PRIMARY = B["primaryColor"]
SECONDARY = B["secondaryColor"]
WEBHOOK = B["zapierWebhook"]
FONT    = B.get("font", "Inter")

# ── Lucide icon helpers ───────────────────────────────────
def _svg(paths, size=16):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
            f' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
            f' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
            f' aria-hidden="true">{paths}</svg>')

ICON = {
    'phone':    _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>"),
    'pin':      _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>"),
    'clock':    _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>"),
    'star':     _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>"),
    'shield':   _svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>"),
    'home':     _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>"),
    'dollar':   _svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>"),
    'check':    _svg("<polyline points='20 6 9 17 4 12'/>"),
    'check-circle': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>"),
    'clipboard':_svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>"),
    'camera':   _svg("<path d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z'/><circle cx='12' cy='13' r='3'/>"),
    'timer':    _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>"),
    'ruler':    _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>"),
    'phone_lg': _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>", 24),
    'pin_lg':   _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>", 24),
    'clock_lg': _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>", 24),
    'timer_lg': _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>", 24),
    'star_lg':  _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>", 20),
    'dollar_lg':_svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>", 24),
    'ruler_lg': _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>", 24),
    'home_lg':  _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>", 24),
    'shield_lg':_svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>", 24),
    'clipboard_lg': _svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>", 24),
    'check_lg': _svg("<polyline points='20 6 9 17 4 12'/>", 20),
    'check-circle_lg': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>", 24),
}
# ─────────────────────────────────────────────────────────


pages_created = []
pages_failed = []

# ── Helpers ───────────────────────────────────────────────

def make_theme_css():
    primary_dark   = B.get("primaryDark", B["primaryColor"])
    secondary_dark = B.get("secondaryDark", B["secondaryColor"])
    content = f"""/* Auto-generated by generate.py — do not edit manually */
:root {{
  --green:        {B["primaryColor"]};
  --green-dark:   {primary_dark};
  --green-light:  {B["secondaryColor"]};
  --green-hover:  {secondary_dark};
}}
"""
    write("css/theme.css", content)

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def write(path, content):
    d = os.path.dirname(path)
    if d:
        mkdir(d)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    pages_created.append(path.replace(os.getcwd() + "/", ""))

def nav(active=""):
    service_links = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    mobile_service_links = "\n".join(
        f'<a href="/services/{s["slug"]}/">{s["name"]}</a>'
        for s in SERVICES
    )
    return f"""
<header class="site-header">
  <nav class="main-nav" aria-label="Main navigation">
    <div class="container nav-inner">
      <a href="/" class="nav-logo">
        <img src="/images/logo.png" alt="{NAME} logo" height="96" />
      </a>
      <ul class="nav-links">
        <li class="has-dropdown">
          <a href="/services/" class="{'active' if active=='services' else ''}">Services ▾</a>
          <ul class="dropdown">
            <li><span class="dropdown-label">Our Services</span></li>
            {service_links}
            <li><a href="/services/" class="dropdown-all">View All Services →</a></li>
          </ul>
        </li>
        <li><a href="/about/" class="{'active' if active=='about' else ''}">About Us</a></li>
        <li><a href="/service-areas/" class="{'active' if active=='areas' else ''}">Service Areas</a></li>
        <li><a href="/reviews/" class="{'active' if active=='reviews' else ''}">Reviews</a></li>
        <li><a href="/faq/" class="{'active' if active=='faq' else ''}">FAQ</a></li>
      </ul>
      <div class="nav-cta">
        <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
        <a href="/request-service.html" class="btn btn-primary btn-sm">Get Started</a>
      </div>
      <button class="hamburger" id="hamburger" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</header>
<div class="mobile-menu" id="mobile-menu">
  <div class="mobile-menu-header">
    <img src="/images/logo.png" alt="{NAME}" height="40" />
    <button id="mobile-close" aria-label="Close">✕</button>
  </div>
  <a href="/request-service.html" class="btn btn-primary mobile-cta">Get Free Estimate</a>
  <a href="tel:{PHONE_RAW}" class="btn btn-outline mobile-cta">{PHONE}</a>
  <div class="mobile-nav-section">Services</div>
  {mobile_service_links}
  <div class="mobile-nav-section">Company</div>
  <a href="/about/">About Us</a>
  <a href="/service-areas/">Service Areas</a>
  <a href="/reviews/">Reviews</a>
  <a href="/faq/">FAQ</a>
</div>"""

def footer():
    service_links = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    nassau = [a for a in AREAS if a["county"] == "Nassau"][:6]
    suffolk = [a for a in AREAS if a["county"] == "Suffolk"][:6]
    nassau_links = "\n".join(f'<li><a href="/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in nassau)
    suffolk_links = "\n".join(f'<li><a href="/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in suffolk)
    return f"""
<footer class="site-footer">
  <div class="footer-main">
    <div class="container footer-grid">
      <div class="footer-brand">
        <a href="/"><img src="/images/logo.png" alt="{NAME}" height="72" class="footer-logo" /></a>
        <p>{B.get('footerTagline', f"{NAME} — locally based in {B['city']}, NY.")}</p>
        <a href="tel:{PHONE_RAW}" class="footer-phone">{PHONE}</a>
        <p class="footer-address">{ADDRESS}</p>
        <div class="footer-social">
          <a href="{B['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
          </a>
          <a href="{B['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg>
          </a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Our Services</h4>
        <ul>{service_links}</ul>
      </div>
      <div class="footer-col">
        <h4>Nassau County</h4>
        <ul>{nassau_links}<li><a href="/service-areas/">All Areas →</a></li></ul>
      </div>
      <div class="footer-col">
        <h4>Suffolk County</h4>
        <ul>{suffolk_links}<li><a href="/service-areas/">All Areas →</a></li></ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <span>&copy; <span id="yr"></span> {NAME}. All rights reserved.</span>
      <div class="footer-legal">
        <a href="/privacy-policy.html">Privacy Policy</a>
        <a href="/terms.html">Terms of Use</a>
        <a href="/accessibility.html">Accessibility</a>
      </div>
    </div>
  </div>
</footer>
<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>
<script src="/js/main.js"></script>"""

def head(title, desc, canonical, schema=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="https://{B['domain']}{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://{B['domain']}{canonical}" />
  <meta property="og:image" content="/images/hero-bg.jpg" />
  {schema}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family={FONT.replace(' ', '+')}:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/main.css" />
  <link rel="stylesheet" href="/css/theme.css" />
</head>
<body>"""

def booking_form(compact=False):
    service_opts = "\n".join(
        f'<option value="{s["slug"]}">{s["name"]}</option>'
        for s in SERVICES
    )
    if compact:
        return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Get Your Custom Quote</h3>
    <p>Response within 1 business hour</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Your full name" /></div>
    <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required placeholder="{PHONE}" /></div>
    <div class="form-group"><label>Service</label>
      <select name="service"><option value="">Select a service...</option>{service_opts}</select>
    </div>
    <div class="form-group"><label>Details</label><textarea name="message" rows="3" placeholder="Tell us about your project..."></textarea></div>
    <input type="text" name="_gotcha" style="display:none" />
    <input type="hidden" name="_next" value="/thank-you.html" />
    <button type="submit" class="btn btn-primary btn-block">Send Request →</button>
  </form>
</div>"""
    return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Request a Free Estimate</h3>
    <p>We respond within 1 business hour</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Your full name" /></div>
    <div class="form-row">
      <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required placeholder="{PHONE}" /></div>
      <div class="form-group"><label>ZIP Code *</label><input type="text" name="zip" required placeholder="{B['zip']}" maxlength="5" /></div>
    </div>
    <div class="form-group"><label>Email</label><input type="email" name="email" placeholder="you@email.com" /></div>
    <div class="form-group"><label>Service Needed *</label>
      <select name="service" required><option value="">Select a service...</option>{service_opts}<option value="other">Other / Not Sure</option></select>
    </div>
    <div class="form-group"><label>Project Details</label><textarea name="message" rows="4" placeholder="Describe your project, property size, timeline..."></textarea></div>
    <input type="text" name="_gotcha" style="display:none" />
    <input type="hidden" name="_subject" value="New Estimate Request — {NAME}" />
    <input type="hidden" name="_next" value="/thank-you.html" />
    <button type="submit" class="btn btn-primary btn-block">Send My Request →</button>
    <p class="form-disclaimer">We respect your privacy. No spam, ever.</p>
  </form>
</div>"""

def review_cards(city=None):
    cards = []
    for r in REVIEWS:
        loc = city + ", NY" if city else r["location"]
        stars = ICON["star"] * r["rating"]
        parts = r["name"].split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
        cards.append(f"""
    <div class="review-card">
      <div class="review-stars">{stars}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-footer">
        <div class="review-avatar">{initials}</div>
        <div>
          <div class="review-author">{r['name']}</div>
          <div class="review-location">{loc}</div>
        </div>
      </div>
    </div>""")
    return "\n".join(cards)

def service_area_links():
    return "\n".join(
        f'<a href="/service-areas/{a["slug"]}/" class="city-pill">{a["name"]}</a>'
        for a in AREAS
    )

def breadcrumbs(crumbs):
    items = []
    schema_items = []
    for i, (label, url) in enumerate(crumbs):
        if url:
            items.append(f'<li><a href="{url}">{label}</a></li>')
        else:
            items.append(f'<li>{label}</li>')
        if url:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}","item":"https://{B["domain"]}{url}"}}')
        else:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}"}}')
    schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{",".join(schema_items)}]}}
  </script>"""
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="container"><ol class="breadcrumb-list">{"".join(items)}</ol></div></nav>', schema

LOCAL_BIZ_SCHEMA = f"""<script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"{B.get('schemaType','LocalBusiness')}",
    "name":"{NAME}",
    "url":"https://{B['domain']}/",
    "telephone":"{PHONE}",
    "address":{{"@type":"PostalAddress","streetAddress":"{B['address']}","addressLocality":"{B['city']}","addressRegion":"{B['state']}","postalCode":"{B['zip']}","addressCountry":"US"}},
    "priceRange":"$$",
    "openingHours":"Mo-Sa 08:00-18:00",
    "geo":{{"@type":"GeoCoordinates","latitude":40.7065,"longitude":-73.6212}},
    "areaServed":{json.dumps([{"@type":"City","name":a["name"]} for a in AREAS])},
    "sameAs":["{B['facebook']}","{B['instagram']}"]
  }}
  </script>"""

# ─────────────────────────────────────────────────────────
# HELPER: Service card header (photo or emoji icon)
# ─────────────────────────────────────────────────────────

def service_card_header(s):
    if s.get("image"):
        return f'<img class="service-card-img" src="{s["image"]}" alt="{s["name"]}" loading="lazy" />'
    return f'<div class="service-card-placeholder" aria-hidden="true"></div>'


# ─────────────────────────────────────────────────────────
# HELPER: Gallery section (Our Work)
# ─────────────────────────────────────────────────────────

def gallery_section():
    if not GALLERY:
        return ""
    items = []
    for item in GALLERY:
        if item.get("src"):
            items.append(f"""      <figure class="gallery-item">
        <img src="{item['src']}" alt="{item['alt']}" loading="lazy" />
        <figcaption>{item['label']}</figcaption>
      </figure>""")
        else:
            items.append(f"""      <div class="gallery-item gallery-placeholder-slot">
        <span class="gallery-slot-icon">{item.get('icon','')}</span>
        <span class="gallery-slot-label">{item['label']}</span>
      </div>""")
    items_html = "\n".join(items)
    return f"""
<!-- OUR WORK -->
<section class="section" id="our-work">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Work</span>
      <h2>South Shore Work We're Proud Of</h2>
      <p>Custom landscapes, pavers, patios, and outdoor living spaces — built right here on Long Island's South Shore. Every project is one-of-a-kind.</p>
    </div>
    <div class="gallery-grid">
{items_html}
    </div>
    <div class="text-center mt-4">
      <a href="/request-service.html" class="btn btn-primary">Start Your Project</a>
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# PAGE: Homepage
# ─────────────────────────────────────────────────────────

def make_homepage():
    service_cards_list = []
    for s in SERVICES:
        service_cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3>{s['name']}</h3>
        <p>{s['description']}</p>
        <a href="/services/{s['slug']}/" class="card-link">Learn More →</a>
      </div>
    </div>""")
    service_cards = "\n".join(service_cards_list)

    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS[:5])

    slides = B.get('heroSlides', ['/images/hero-bg.jpg'])
    slide_divs = "\n    ".join(
        f'<div class="hero-slide{" active" if i == 0 else ""}" style="background-image:url(\'{s}\')"></div>'
        for i, s in enumerate(slides)
    )
    dot_buttons = "\n    ".join(
        f'<button class="hero-dot{" active" if i == 0 else ""}" data-slide="{i}" aria-label="Go to slide {i+1}"></button>'
        for i in range(len(slides))
    )

    content = f"""{head(
        f"{B['industry']} in {B['city']}, NY | {NAME} | {PHONE}",
        f"{NAME} provides professional {B['industryLower']} in {B['city']}, NY. Call {PHONE} for a free estimate!",
        "/",
        LOCAL_BIZ_SCHEMA
    )}
{nav()}

<!-- HERO -->
<section class="hero" id="hero-carousel">
  <div class="hero-slides">
    {slide_divs}
  </div>
  <div class="hero-overlay"></div>
  <div class="container">
    <div class="hero-content">
      <span class="hero-brand-name">{NAME}</span>
      <span class="hero-badge">{B['city']}, NY · South Shore Long Island</span>
      <h1>{B['tagline']}</h1>
      <p>{B.get('heroSubtext', f'Professional {B.get("industryLower","contracting")} services for Long Island homeowners. Call {PHONE} for a free estimate.')}</p>
      <div class="hero-actions">
        <a href="/request-service.html" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
      </div>
      <div class="hero-trust">
        <span>5-Star Rated</span>
        <span>Licensed &amp; Insured</span>
        <span>{B['city']} Based</span>
      </div>
    </div>
  </div>
  <div class="hero-slide-dots">
    {dot_buttons}
  </div>
</section>
<script>
(function() {{
  var slides = document.querySelectorAll('#hero-carousel .hero-slide');
  var dots   = document.querySelectorAll('#hero-carousel .hero-dot');
  var cur = 0, timer;
  function goTo(n) {{
    slides[cur].classList.remove('active');
    dots[cur].classList.remove('active');
    cur = (n + slides.length) % slides.length;
    slides[cur].classList.add('active');
    dots[cur].classList.add('active');
  }}
  function next() {{ goTo(cur + 1); }}
  function start() {{ timer = setInterval(next, 5500); }}
  function stop()  {{ clearInterval(timer); }}
  dots.forEach(function(dot, i) {{
    dot.addEventListener('click', function() {{ stop(); goTo(i); start(); }});
  }});
  var hero = document.getElementById('hero-carousel');
  hero.addEventListener('mouseenter', stop);
  hero.addEventListener('mouseleave', start);
  start();
}})();
</script>

<!-- STATS -->
<div class="stats-bar">
  <div class="container stats-grid">
    <div class="stat"><span class="stat-n">South Shore</span><span class="stat-l">Specialists Since Day One</span></div>
    <div class="stat"><span class="stat-n">100%</span><span class="stat-l">Custom Builds — No Templates</span></div>
    <div class="stat"><span class="stat-n">15+</span><span class="stat-l">Towns Served</span></div>
    <div class="stat"><span class="stat-n">5-Star</span><span class="stat-l">Rated by Homeowners</span></div>
  </div>
</div>

<!-- BOOKING -->
<section class="booking-section">
  <div class="container booking-wrap">
    <div class="booking-info">
      <span class="eyebrow">Start Your Project</span>
      <h2>Get Your Free Estimate</h2>
      <p>Response within 1 hour — we answer when other companies don't call back. Locally owned, South Shore based, and built on doing things right.</p>
      <ul>
        <li><span class="icon">{ICON["phone"]}</span><div><strong>Call or text {PHONE}</strong> — Mon–Sat 8am–6pm, we pick up.</div></li>
        <li><span class="icon">{ICON["home"]}</span><div><strong>Free on-site walkthrough</strong> — we come to your property before any quote is written.</div></li>
        <li><span class="icon">{ICON["clipboard"]}</span><div><strong>Written quote upfront</strong> — you know the price before we touch anything. No surprises, ever.</div></li>
        <li><span class="icon">{ICON["check-circle"]}</span><div><strong>We don't leave until it's right</strong> — every job is finished to the standard you expect.</div></li>
      </ul>
    </div>
    <div class="booking-form-col">
      {booking_form(compact=True)}
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section class="section section-light" id="how-it-works">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">How {NAME} Works</span>
      <h2>Simple Process. Serious Results.</h2>
      <p>From your first call to the final walkthrough — a straightforward process with no surprises and no shortcuts.</p>
    </div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">1</div>
        <h3 class="step-title">Tell Us What You Want</h3>
        <p class="step-desc">Call, text, or fill out the form. We respond within 1 hour to confirm your free on-site consultation — no pressure, no obligation.</p>
      </div>
      <div class="step-card">
        <div class="step-number">2</div>
        <h3 class="step-title">We Walk the Property</h3>
        <p class="step-desc">A {NAME} crew member visits your property, listens to your vision, and gives you a written quote before anything is scheduled or started.</p>
      </div>
      <div class="step-card">
        <div class="step-number">3</div>
        <h3 class="step-title">We Build It Right</h3>
        <p class="step-desc">Once you approve the plan, our crew handles materials, installation, and cleanup — and we don't leave until the job meets your standard.</p>
      </div>
    </div>
    <div class="text-center mt-4">
      <a href="/request-service.html" class="btn btn-primary">Schedule Your Consultation</a>
    </div>
  </div>
</section>

<!-- SERVICES -->
<section class="section" id="services">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What We Do</span>
      <h2>{B.get('servicesHeadline', f'{B.get("industry","Professional")} Services for Long Island')}</h2>
      <p>{B.get('servicesSubtext', f'Professional {B.get("industryLower","services")} for Long Island homeowners and businesses.')}</p>
    </div>
    <div class="service-grid">
      {service_cards}
    </div>
  </div>
</section>

<!-- WHY US -->
<section class="split-section">
  <div class="split-img">
    <img src="/images/Gemini_Generated_Image_xrda4xxrda4xxrda.png" alt="GOAT Landscaping — Massapequa Park, NY" />
  </div>
  <div class="split-content">
    <span class="eyebrow">Why {NAME}</span>
    <h2>South Shore's Best. No Exceptions.</h2>
    <p>Based in Massapequa Park — not a franchise, not a national chain. Every project is personally managed from the first consultation to the final walkthrough.</p>
    <ul class="check-list">
      <li>Licensed &amp; insured in New York State</li>
      <li>Transparent pricing — written quote before any work begins</li>
      <li>100% custom — no templates, no cookie-cutter designs</li>
      <li>Crew that doesn't leave until the job is done right</li>
    </ul>
    <a href="/about/" class="btn btn-primary">About GOAT</a>
  </div>
</section>
{gallery_section()}

<!-- REVIEWS -->
<section class="section section-light" id="reviews">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Reviews</span>
      <h2>What South Shore Homeowners Are Saying</h2>
    </div>
    <div class="review-grid">
      {review_cards()}
    </div>
    <div class="text-center mt-4">
      <a href="/reviews/" class="btn btn-outline">Read More Reviews</a>
    </div>
  </div>
</section>

<!-- SERVICE AREAS -->
<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Service Areas</span>
      <h2>Serving the South Shore of Long Island</h2>
      <p>We cover Nassau and Suffolk Counties on the South Shore. Don't see your town? Call us — we likely serve you.</p>
    </div>
    <div class="city-grid">
      {service_area_links()}
    </div>
  </div>
</section>

<!-- FAQ PREVIEW -->
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">FAQ</span>
      <h2>Frequently Asked Questions</h2>
    </div>
    <div class="faq-list">
      {faq_items}
    </div>
    <div class="text-center mt-4">
      <a href="/faq/" class="btn btn-outline">See All FAQs</a>
    </div>
  </div>
</section>

<!-- BLOG RESOURCES -->
<!-- TODO: create /blog/ pages and update these links when ready -->
<section class="section blog-resources">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Learn More</span>
      <h2>Helpful Resources</h2>
      <p>Expert tips and guides for your Long Island property</p>
    </div>
    <div class="blog-grid">
      <article class="blog-card">
        <h3>How to Choose the Right Paver Material for Your Long Island Property</h3>
        <p>Concrete, natural stone, or porcelain? We break down the pros, cons, and real-world performance of the most popular paver materials for South Shore driveways, patios, and walkways.</p>
        <a href="/blog/paver-guide/" class="read-more">Read More →</a>
      </article>
      <article class="blog-card">
        <h3>5 Signs Your Front Yard Needs a Professional Redesign</h3>
        <p>Is your curb appeal working for your home or against it? Here are five clear signs it's time to stop patching and start planning a front yard that actually impresses.</p>
        <a href="/blog/front-yard-redesign/" class="read-more">Read More →</a>
      </article>
      <article class="blog-card">
        <h3>What to Expect During a Professional Landscape Installation</h3>
        <p>Not sure what the process looks like from start to finish? Here's an honest, step-by-step walkthrough of what happens when you hire a landscaping crew for a real South Shore project.</p>
        <a href="/blog/what-to-expect/" class="read-more">Read More →</a>
      </article>
    </div>
    <div class="text-center mt-4">
      <a href="/blog/" class="btn btn-outline">View All Articles</a>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Build Something Outstanding?</h2>
    <p>One call is all it takes. Free on-site estimate, transparent pricing, and a crew that shows up on time and delivers.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get a Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service detail pages
# ─────────────────────────────────────────────────────────

def make_service_page(s):
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", "/services/"), (s["name"], None)])
    bullets = "\n".join(f"<li>{b}</li>" for b in s["bullets"])
    other_services = "\n".join(
        f'<a href="/services/{o["slug"]}/" class="related-link">{o["name"]}</a>'
        for o in SERVICES if o["slug"] != s["slug"]
    )
    content = f"""{head(
        f"{s['name']} in {B['city']}, NY | {NAME} | {PHONE}",
        f"Professional {s['name'].lower()} in {B['city']}, NY and all of Long Island. {NAME} — certified, insured, and locally based. Call {PHONE} for a free estimate.",
        f"/services/{s['slug']}/",
        bc_schema
    )}
{nav(active="services")}
{bc}

<section class="page-hero">
  <div class="container">
    <h1>{s['name']} in {B['city']}, NY</h1>
    <p>{s['heroText']}</p>
    <div class="hero-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Professional {s['name']} on Long Island</h2>
      <p>{s['description']} {NAME} is based in {B['city']}, NY — delivering custom {B['industryLower']} and outdoor renovation for South Shore homeowners who expect craftsmanship and transparent pricing.</p>
      <h3>What's Included</h3>
      <ul class="check-list">{bullets}</ul>
      <h3>Why Choose {NAME}?</h3>
      <p>We're locally owned and based in {B['city']}, NY — not a franchise, not a national chain. Every project is handled by our own crew, and we don't leave until the job meets your standard.</p>
      <div class="cta-inline">
        <a href="/request-service.html" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline">Call {PHONE}</a>
      </div>
      <h3>Service Areas</h3>
      <p>We provide {s['name'].lower()} throughout Long Island including:</p>
      <div class="city-grid city-grid-sm">
        {service_area_links()}
      </div>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What Customers Say</h2>
    <div class="review-grid">{review_cards()}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="text-center mb-4">Other Services We Offer</h2>
    <div class="related-grid">{other_services}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need {s['name']} in {B['city']}, NY?</h2>
    <p>Call or fill out the form above — we respond within 1 business hour with a free estimate.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"services/{s['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Services hub
# ─────────────────────────────────────────────────────────

def make_services_hub():
    cards_list = []
    for s in SERVICES:
        cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3><a href="/services/{s['slug']}/">{s['name']}</a></h3>
        <p>{s['description']}</p>
        <a href="/services/{s['slug']}/" class="card-link">Learn More →</a>
      </div>
    </div>""")
    cards = "\n".join(cards_list)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", None)])
    content = f"""{head(
        f"{B['industry']} | {NAME} | {PHONE}",
        f"{NAME} offers professional {B['industryLower']} in {B['city']}, NY. Call {PHONE} for a free estimate.",
        "/services/",
        bc_schema
    )}
{nav(active="services")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Our Landscaping Services</h1>
    <p>Custom landscaping and outdoor renovation for South Shore homeowners. Every project is designed from scratch — no templates, no shortcuts, built to last.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="service-grid">{cards}</div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Not Sure What You Need?</h2>
    <p>Call us and describe your property — we'll recommend the right services and give you a free estimate.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("services/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: City / Service Area pages
# ─────────────────────────────────────────────────────────

def make_city_page(area):
    city = area["name"]
    slug = area["slug"]
    county = area["county"]
    nearby = ", ".join(f"<strong>{n}</strong>" for n in area["nearbyAreas"])
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", "/service-areas/"), (city, None)])

    city_schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"LandscapingBusiness",
    "name":"{NAME} — {city}","url":"https://{B['domain']}/service-areas/{slug}/",
    "telephone":"{PHONE}","priceRange":"$$",
    "@type":"{B.get('schemaType','LocalBusiness')}",
    "address":{{"@type":"PostalAddress","addressLocality":"{city}","addressRegion":"{B['state']}","addressCountry":"US"}},
    "areaServed":{{"@type":"City","name":"{city}"}}
  }}
  </script>"""

    service_list = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]} in {city}</a></li>'
        for s in SERVICES
    )

    content = f"""{head(
        f"{B['industry']} in {city}, NY | {NAME} | {PHONE}",
        f"Professional {B['industryLower']} in {city}, NY. {NAME} serves {city} and {county} County. Call {PHONE} for a free estimate.",
        f"/service-areas/{slug}/",
        bc_schema + city_schema
    )}
{nav(active="areas")}
{bc}

<section class="page-hero">
  <div class="container">
    <h1>Landscaping Services in {city}, NY</h1>
    <p>{NAME} serves {city} and surrounding {county} County communities. Call {PHONE} for a free estimate today.</p>
    <div class="hero-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Your Local Landscaping Experts in {city}</h2>
      <p>When {city} homeowners want custom landscaping done right, they call {NAME}. We're based in {B['city']} on the South Shore — not a national franchise, not a call center. Our crew knows the properties, the soil, and the climate in {county} County and delivers real craftsmanship on every project.</p>
      <p>From landscape design and installation to pavers, patios, driveways, and full outdoor living environments, we handle everything for homeowners throughout {city} and surrounding {county} County.</p>

      <h3>Services We Offer in {city}, NY</h3>
      <ul class="check-list">{service_list}</ul>

      <h3>Areas Near {city} We Also Serve</h3>
      <p>In addition to {city}, we serve {nearby} and more throughout {county} County.
      <a href="/service-areas/">View all service areas →</a></p>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What {city} Residents Say</h2>
    <div class="review-grid">{review_cards(city)}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need Landscaping in {city}, NY?</h2>
    <p>We're nearby and ready. Call or submit the form — response within 1 business hour.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"service-areas/{slug}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service Areas hub
# ─────────────────────────────────────────────────────────

def make_areas_hub():
    nassau = [a for a in AREAS if a["county"] == "Nassau"]
    suffolk = [a for a in AREAS if a["county"] == "Suffolk"]
    def area_cards(areas):
        return "\n".join(f"""
        <a href="/service-areas/{a['slug']}/" class="area-card">
          <h3>{a['name']}</h3>
          <span>{a['county']} County</span>
        </a>""" for a in areas)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", None)])
    content = f"""{head(
        f"Landscaping Service Areas — Long Island, NY | {NAME}",
        f"{NAME} serves Nassau and Suffolk Counties on Long Island. Click your city to see local landscaping services and get a free estimate.",
        "/service-areas/",
        bc_schema
    )}
{nav(active="areas")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>South Shore Landscaping Service Areas</h1>
    <p>{NAME} covers the South Shore of Nassau and Suffolk Counties. Select your town for local information and a free estimate.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <h2>Nassau County</h2>
    <div class="area-grid">{area_cards(nassau)}</div>
    <h2 class="mt-4">Suffolk County</h2>
    <div class="area-grid">{area_cards(suffolk)}</div>
    <p class="mt-4" style="color:var(--text-mid)">Don't see your city? <a href="tel:{PHONE_RAW}">Call us at {PHONE}</a> — we likely serve your area.</p>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Serving All of Long Island</h2>
    <p>Call or request online for service in your area.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("service-areas/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: About
# ─────────────────────────────────────────────────────────

def make_about():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("About Us", None)])
    content = f"""{head(
        f"About Us | {NAME} — {B['city']}, NY",
        f"Learn about {NAME}, Long Island's landscaping &amp; outdoor renovation company based in {B['city']}, NY. Locally owned, certified, and insured.",
        "/about/",
        bc_schema
    )}
{nav(active="about")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>About {NAME}</h1>
    <p>South Shore Long Island's custom landscaping and outdoor living company — based in {B['city']}, NY.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="split-section">
      <div class="split-img"><img src="/images/hero-bg.jpg" alt="{NAME} — locally owned and operated in Massapequa Park, NY" /></div>
      <div class="split-content">
        <span class="eyebrow">Who We Are</span>
        <h2>Built to Be the Best</h2>
        <p>{NAME} is a South Shore landscaping company built around one standard: the best. Based at {B['address']} in {B['city']}, NY, we design and install custom landscapes, patios, pavers, and outdoor living spaces for homeowners who expect craftsmanship.</p>
        <p>Not a franchise — a locally owned team. Every project gets personal attention, transparent pricing, and a crew that doesn't leave until the job is done right.</p>
        <ul class="check-list">
          <li>Fully licensed and insured in New York State</li>
          <li>Locally owned — based in {B['city']}, NY</li>
          <li>100% custom designs — no templates or shortcuts</li>
          <li>Free on-site consultation before any quote</li>
          <li>We don't leave until the job meets your standard</li>
        </ul>
      </div>
    </div>
  </div>
</section>
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Promise</span>
      <h2>What Makes GOAT Different</h2>
    </div>
    <div class="features-grid">
      <div class="feature-card">{ICON["pin_lg"]}<h3>South Shore Specialists</h3><p>We know the South Shore's soil, climate, and neighborhoods. Every design decision is made with Long Island in mind.</p></div>
      <div class="feature-card">{ICON["dollar_lg"]}<h3>Transparent Pricing</h3><p>You'll know the full cost before we start. Written quotes, no hidden fees, no surprises at the end.</p></div>
      <div class="feature-card">{ICON["star_lg"]}<h3>Done Right or We Fix It</h3><p>We don't consider a job finished until you're satisfied. Every project is backed by our commitment to quality.</p></div>
      <div class="feature-card">{ICON["ruler_lg"]}<h3>100% Custom</h3><p>No templates, no shortcuts. Every project is designed specifically for your property, your goals, and your budget.</p></div>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Work with Us?</h2>
    <p>Call or request a free estimate today.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("about/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: FAQ
# ─────────────────────────────────────────────────────────

def make_faq():
    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS)

    faq_schema_items = json.dumps([{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in FAQS])
    faq_schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{faq_schema_items}}}</script>'

    bc, bc_schema = breadcrumbs([("Home", "/"), ("FAQ", None)])
    content = f"""{head(
        f"FAQ — Landscaping Questions Answered | {NAME}",
        f"Common questions about {NAME}'s landscaping services in {B['city']}, NY. Get answers about pricing, scheduling, service areas, and more.",
        "/faq/",
        bc_schema + faq_schema
    )}
{nav(active="faq")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Frequently Asked Questions</h1>
    <p>Everything you need to know about {NAME}'s services on Long Island.</p>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width:800px">
    <div class="faq-list">{faq_items}</div>
    <div class="cta-inline mt-4">
      <p>Still have questions? <a href="tel:{PHONE_RAW}">Call or text us at {PHONE}</a> — we respond within 1 business hour.</p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Get Started?</h2>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("faq/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Reviews
# ─────────────────────────────────────────────────────────

def make_reviews():
    all_reviews = "\n".join(f"""
    <div class="review-card">
      <div class="review-stars">{ICON["star"] * r['rating']}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-author">{r['name']}</div>
      <div class="review-location">{r['location']}</div>
    </div>""" for r in REVIEWS)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Reviews", None)])
    content = f"""{head(
        f"Customer Reviews | {NAME} — Long Island, NY",
        f"Read reviews from satisfied customers of {NAME} in {B['city']}, NY and Long Island. See why we're rated 5 stars.",
        "/reviews/",
        bc_schema
    )}
{nav(active="reviews")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Customer Reviews</h1>
    <p>See what Long Island homeowners and businesses say about {NAME}.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="review-grid">{all_reviews}</div>
    <div class="cta-inline mt-4 text-center">
      <p>Want to leave a review? <a href="https://g.page/r/GOOGLE_REVIEW_LINK/review" target="_blank" rel="noopener">Leave us a Google review →</a></p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Join Our Happy Customers</h2>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("reviews/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Request Service
# ─────────────────────────────────────────────────────────

def make_request_service():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Request Service", None)])
    content = f"""{head(
        f"Request a Free Estimate | {NAME} | {PHONE}",
        f"Request a free landscaping estimate from {NAME} in {B['city']}, NY. We serve all of Long Island and respond within 1 business hour.",
        "/request-service.html",
        bc_schema
    )}
{nav()}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Request a Free Estimate</h1>
    <p>Fill out the form and we'll get back to you within 1 business hour. No pressure, no obligation.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="content-sidebar-layout">
      <div class="content-main">
        <h2>Let's Talk About Your Project</h2>
        <p>Whether it's a quick lawn mowing quote or a full landscape renovation, we're here to help. Tell us about your project and we'll provide a free, transparent estimate.</p>
        <div class="features-grid" style="margin-top:2rem">
          <div class="feature-card">{ICON["phone_lg"]}<h3>Call or Text</h3><p><a href="tel:{PHONE_RAW}">{PHONE}</a><br/>Mon–Sat, 7am–6pm</p></div>
          <div class="feature-card">{ICON["pin_lg"]}<h3>Our Location</h3><p>{ADDRESS}</p></div>
          <div class="feature-card">{ICON["timer_lg"]}<h3>Response Time</h3><p>Within 1 business hour</p></div>
        </div>
        <div style="margin-top:2rem;border-radius:8px;overflow:hidden">
          <iframe src="{B['googleMapsEmbed']}" width="100%" height="300" style="border:0;display:block" allowfullscreen loading="lazy" title="{NAME} Location Map"></iframe>
        </div>
      </div>
      <aside class="content-sidebar">
        {booking_form()}
      </aside>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("request-service.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Thank You
# ─────────────────────────────────────────────────────────

def make_thank_you():
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Request Received | {NAME}</title>
  <meta name="robots" content="noindex" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family={FONT.replace(' ', '+')}:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/main.css" />
  <link rel="stylesheet" href="/css/theme.css" />
</head>
<body>
<header class="site-header">
  <nav class="main-nav"><div class="container nav-inner">
    <a href="/" class="nav-logo"><img src="/images/logo.png" alt="{NAME}" height="48" /></a>
    <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
  </div></nav>
</header>

<section class="ty-hero">
  <div class="container ty-hero-inner">
    <div class="ty-check">
      <svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" width="64" height="64">
        <circle cx="26" cy="26" r="26" fill="var(--green-light)"/>
        <path d="M15 27l8 8 14-16" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1>Your Request Was Received</h1>
    <p>Thanks for contacting {NAME}. A member of our team will reach out to you within <strong>1 business hour</strong>.</p>
    <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-lg">Call Us Now — {PHONE}</a>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What Happens Next</span>
      <h2>Here's What to Expect</h2>
    </div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">1</div>
        <h3 class="step-title">We'll Be in Touch</h3>
        <p class="step-desc">Expect a call or text from our team within 1 business hour. We'll confirm your request and answer any questions you have right away.</p>
      </div>
      <div class="step-card">
        <div class="step-number">2</div>
        <h3 class="step-title">Free On-Site Consultation</h3>
        <p class="step-desc">We'll visit your property, walk the space with you, and listen to your vision. No pressure — just an honest conversation about what's possible.</p>
      </div>
      <div class="step-card">
        <div class="step-number">3</div>
        <h3 class="step-title">Your Custom Quote</h3>
        <p class="step-desc">You'll receive a detailed, transparent quote before any work begins. No surprises, no hidden fees — just clear pricing for exactly what you asked for.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container" style="text-align:center;max-width:560px;margin:0 auto">
    <h2>While You Wait</h2>
    <p style="color:var(--gray-mid);margin-bottom:2rem">Browse our services to get inspired, or read what Long Island homeowners are saying about us.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a href="/services/" class="btn btn-outline">Browse Services</a>
      <a href="/reviews/" class="btn btn-outline">Read Reviews</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("thank-you.html", content)


# ─────────────────────────────────────────────────────────
# PAGES: Blog articles
# ─────────────────────────────────────────────────────────

def make_blog_pages():
    posts = [
        {
            "slug": "paver-guide",
            "title": "How to Choose the Right Paver Material for Your Long Island Property",
            "desc": "Concrete, natural stone, or porcelain? A breakdown of paver materials for South Shore driveways, patios, and walkways from GOAT Landscaping in Massapequa Park, NY.",
            "body": f"""
<p>If you're planning a paver driveway, patio, or walkway, the material you choose affects everything — cost, durability, appearance, and how it holds up through Long Island winters. Here's an honest breakdown of the most popular options.</p>
<h2>Concrete Pavers</h2>
<p>Concrete pavers are the most popular choice for driveways and patios on the South Shore. They're cost-effective, available in a huge range of colors and shapes, and engineered to handle freeze-thaw cycles without cracking. With proper base prep and sealing, a concrete paver installation can last 25+ years.</p>
<ul>
  <li><strong>Best for:</strong> driveways, large patios, budget-conscious projects</li>
  <li><strong>Typical cost:</strong> moderate — good value per square foot</li>
  <li><strong>Durability:</strong> excellent with professional installation and proper base</li>
</ul>
<h2>Natural Stone (Bluestone, Travertine, Fieldstone)</h2>
<p>Natural stone delivers a premium, one-of-a-kind look that concrete can't replicate. Bluestone is a Long Island classic — timeless, durable, and available in both thermal and natural cleft finishes. Travertine runs more expensive but gives a high-end Mediterranean look that photographs beautifully.</p>
<ul>
  <li><strong>Best for:</strong> patios, walkways, upscale front entry areas</li>
  <li><strong>Typical cost:</strong> higher — premium material and additional prep required</li>
  <li><strong>Durability:</strong> excellent, but some stones require sealing to prevent staining</li>
</ul>
<h2>Porcelain Pavers</h2>
<p>Porcelain is the newest category gaining traction in the South Shore market. It's non-porous, highly stain-resistant, and comes in large-format tiles that create a sleek, modern look. The tradeoff is cost — both material and installation run higher than concrete.</p>
<ul>
  <li><strong>Best for:</strong> pool decks, modern patio designs, low-maintenance priorities</li>
  <li><strong>Typical cost:</strong> highest of the three</li>
  <li><strong>Durability:</strong> excellent — won't stain, fade, or absorb moisture</li>
</ul>
<h2>What We Recommend</h2>
<p>At {NAME}, we talk through material options during your free on-site consultation — based on your project, your property, and your budget. There's no one-size-fits-all answer, and we'll tell you honestly what holds up best for your specific situation. <a href="/request-service.html">Request your free consultation today.</a></p>"""
        },
        {
            "slug": "front-yard-redesign",
            "title": "5 Signs Your Front Yard Needs a Professional Redesign",
            "desc": "Is your curb appeal working for or against your home? Here are five signs it's time to stop patching and start planning a proper front yard redesign on the South Shore.",
            "body": f"""
<p>A lot of South Shore homeowners have been doing the same thing to their front yard for years — trim a little here, add a plant there, re-mulch every spring. But at a certain point, those small fixes stop working. Here are five signs it's time for a real redesign.</p>
<h2>1. Your Plantings Look Overgrown or Crowded</h2>
<p>Plants grow. What looked balanced when it was installed five years ago might now be blocking windows, crowding walkways, or completely overwhelming the space. Overgrown plantings don't just look bad — they can also damage foundations and create drainage issues. When pruning is no longer keeping up, it's time to rethink the layout.</p>
<h2>2. Your Lawn Has Bare or Patchy Areas That Won't Come Back</h2>
<p>Recurring bare spots are a symptom, not a problem. They usually indicate compacted soil, drainage issues, excessive shade, or grading problems that need professional attention. Re-seeding the same patch year after year is money spent without results.</p>
<h2>3. Your Walkway Looks Dated or Out of Place</h2>
<p>The walkway is the visual bridge between your driveway and your front door. If it's cracked concrete, plain blacktop, or just doesn't match the rest of the property, it drags down the entire curb appeal — even if everything else looks decent.</p>
<h2>4. There's No Defined Structure</h2>
<p>Great front yards have a clear visual structure — defined bed edges, a focal point, some contrast between hardscape and soft plantings. If your front yard looks flat and undefined, the fix isn't more plants. It's a design that creates hierarchy and visual interest.</p>
<h2>5. You've Stopped Feeling Good About How the House Looks</h2>
<p>This is the most important one. If you're embarrassed to park in front of your own house or avoid looking at it from the street, that feeling is worth addressing. A well-designed front yard doesn't just improve property value — it changes how you feel about coming home.</p>
<h2>What a Professional Redesign Actually Looks Like</h2>
<p>At {NAME}, a front yard redesign starts with a free on-site consultation where we walk the space, discuss what's not working, and plan around your home's architecture. You get a written quote before anything is touched. <a href="/request-service.html">Book your free consultation here.</a></p>"""
        },
        {
            "slug": "what-to-expect",
            "title": "What to Expect During a Professional Landscape Installation",
            "desc": "Not sure what a professional landscaping project actually looks like from start to finish? Here's an honest walkthrough from GOAT Landscaping in Massapequa Park, NY.",
            "body": f"""
<p>If you've never hired a landscaping company before — or if you've had a bad experience in the past — knowing what the process should look like helps you make a better decision. Here's a straight walkthrough of how a professional installation runs from start to finish.</p>
<h2>Step 1: The Free On-Site Consultation</h2>
<p>Every project at {NAME} starts with a free consultation at your property. We walk the space with you, listen to what you want, assess what's there now, and ask questions to understand how you use the space. No pressure, no pitch — just a conversation about what's possible.</p>
<p>This step is non-negotiable for us. We don't quote projects we haven't seen, and we don't start work we haven't planned.</p>
<h2>Step 2: The Written Quote</h2>
<p>After the consultation, you receive a detailed written quote that breaks down materials, labor, and scope. You'll know exactly what you're paying for before any work is scheduled. If you have questions about the quote, we answer them — no runaround.</p>
<h2>Step 3: Scheduling and Materials</h2>
<p>Once you approve the quote, we get you on the schedule and source all materials. For most projects, we give you a specific start date and a realistic timeline. If anything changes (weather, material delays), we communicate proactively.</p>
<h2>Step 4: The Installation</h2>
<p>Our crew arrives on time, sets up properly, and works through the job systematically. For hardscape projects (pavers, patios, driveways), this typically involves base excavation, compacted gravel base, sand setting bed, and finally the paver installation and finishing. Landscape projects include grading, soil amendment, plant installation, edging, and mulching.</p>
<p>We don't rush. We work until each phase is done right before moving to the next one.</p>
<h2>Step 5: Final Walkthrough and Cleanup</h2>
<p>When installation is complete, we walk the property with you. If anything needs to be adjusted or addressed, we do it before we leave. We don't consider the job done until you're satisfied — and we clean up completely before driving away.</p>
<h2>Ready to Get Started?</h2>
<p>That's the whole process — no mystery, no surprises. If you're ready to talk about your project, <a href="/request-service.html">request a free on-site consultation here.</a></p>"""
        }
    ]
    for post in posts:
        bc, bc_schema = breadcrumbs([("Home", "/"), ("Resources", None), (post["title"][:40] + "…", None)])
        content = f"""{head(
            f"{post['title']} | {NAME}",
            post["desc"],
            f"/blog/{post['slug']}/",
            bc_schema
        )}
{nav()}{bc}
<section class="page-hero">
  <div class="container">
    <h1>{post['title']}</h1>
  </div>
</section>
<section class="section">
  <div class="container blog-post-layout">
    <article class="blog-post-body">
      {post['body']}
      <div class="blog-post-cta">
        <h3>Ready to Transform Your Outdoor Space?</h3>
        <p>{NAME} serves all of Long Island — Nassau &amp; Suffolk Counties. Free estimates, no obligation.</p>
        <a href="/request-service.html" class="btn btn-primary">Get a Free Estimate</a>
      </div>
    </article>
    <aside class="blog-post-sidebar">
      <div class="booking-card">
        <div class="booking-card-header">
          <h3>Free Estimate</h3>
          <p>Response within 1 business hour</p>
        </div>
        <div style="padding:20px">
          <p style="font-size:.9rem;color:var(--gray-dark);margin-bottom:16px">Ready to get started? Call or text us and we'll schedule a free on-site consultation.</p>
          <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-block">Call {PHONE}</a>
          <a href="/request-service.html" class="btn btn-outline btn-block" style="margin-top:10px">Request Online</a>
        </div>
      </div>
      <div class="sidebar-services">
        <h4>Our Services</h4>
        <ul>{"".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)}</ul>
      </div>
    </aside>
  </div>
</section>
{footer()}
</body></html>"""
        write(f"blog/{post['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Privacy Policy & Terms (boilerplate)
# ─────────────────────────────────────────────────────────

def make_legal():
    for slug, title, body in [
        ("privacy-policy", "Privacy Policy", f"<p>{NAME} respects your privacy. We collect contact information submitted through our forms solely to respond to your service inquiry. We do not sell or share your information with third parties. For questions, call {PHONE}.</p>"),
        ("terms", "Terms of Use", f"<p>By using this website, you agree to these terms of use. All content on this site is owned by {NAME}. Unauthorized reproduction is prohibited. For questions, contact us at {PHONE}.</p>"),
        ("accessibility", "Accessibility", f"<p>{NAME} is committed to ensuring this website is accessible to people with disabilities. If you experience any difficulty, please call us at {PHONE} and we will assist you.</p>"),
    ]:
        bc, bc_schema = breadcrumbs([("Home", "/"), (title, None)])
        content = f"""{head(f"{title} | {NAME}", f"{title} for {NAME}, {B['city']}, NY.", f"/{slug}.html", bc_schema)}
{nav()}{bc}
<section class="page-hero"><div class="container"><h1>{title}</h1></div></section>
<section class="section"><div class="container" style="max-width:800px">{body}</div></section>
{footer()}</body></html>"""
        write(f"{slug}.html", content)


# ─────────────────────────────────────────────────────────
# RUN ALL GENERATORS
# ─────────────────────────────────────────────────────────

print(f"Generating {NAME} site...\n")  # noqa

make_theme_css()
make_homepage()
make_services_hub()
for s in SERVICES:
    make_service_page(s)
make_areas_hub()
for a in AREAS:
    make_city_page(a)
make_about()
make_faq()
make_reviews()
make_request_service()
make_thank_you()
make_blog_pages()
make_legal()

print(f"[OK] {len(pages_created)} pages generated:\n")
for p in sorted(pages_created):
    print(f"   {p}")

if pages_failed:
    print(f"\n[FAIL] {len(pages_failed)} failed:")
    for p in pages_failed:
        print(f"   {p}")

print(f"\nTotal: {len(pages_created)} pages")
