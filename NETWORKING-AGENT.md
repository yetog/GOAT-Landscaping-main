# Networking Agent Instructions — GOAT Landscaping

## Context

A new client site (GOAT Landscaping) needs to be deployed on the same server that already hosts other domains. The DNS is already pointed:
- **A record** for `goatlandscapeli.com` → server IP ✅ (already done)
- **CNAME** for `www.goatlandscapeli.com` → `goatlandscapeli.com` ✅ (already done)

The site is a **static HTML site** (no Node, no PHP, no database). It's generated from Python and consists entirely of HTML, CSS, JS, and image files.

**GitHub repo:** https://github.com/yetog/GOAT-Landscaping-main  
**Domain:** goatlandscapeli.com  
**Stack:** Static files served by nginx  

---

## Step 1 — Pull the Site Files onto the Server

```bash
# Create the web root directory
sudo mkdir -p /var/www/goatlandscapeli.com/html

# Clone the repo
sudo git clone https://github.com/yetog/GOAT-Landscaping-main.git /var/www/goatlandscapeli.com/html

# Set ownership so nginx can read files
sudo chown -R www-data:www-data /var/www/goatlandscapeli.com/html
sudo chmod -R 755 /var/www/goatlandscapeli.com
```

---

## Step 2 — Create the nginx Site Config

Create `/etc/nginx/sites-available/goatlandscapeli.com`:

```nginx
# Redirect www → non-www
server {
    listen 80;
    listen [::]:80;
    server_name www.goatlandscapeli.com;
    return 301 $scheme://goatlandscapeli.com$request_uri;
}

server {
    listen 80;
    listen [::]:80;
    server_name goatlandscapeli.com;

    root /var/www/goatlandscapeli.com/html;
    index index.html;

    # Clean URLs — try file, then directory index, then 404
    location / {
        try_files $uri $uri/ $uri/index.html =404;
    }

    # Cache static assets aggressively (1 year)
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Block source/config files from being served
    location ~ \.(py|sh|md|json|conf|gitignore)$ {
        return 404;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
}
```

---

## Step 3 — Enable the Site

```bash
# Symlink into sites-enabled
sudo ln -s /etc/nginx/sites-available/goatlandscapeli.com /etc/nginx/sites-enabled/

# Test nginx config — fix any errors before reloading
sudo nginx -t

# Reload nginx (zero-downtime — does NOT restart other sites)
sudo systemctl reload nginx
```

---

## Step 4 — SSL with Let's Encrypt (Certbot)

```bash
# Install certbot if not already installed
sudo apt install certbot python3-certbot-nginx -y

# Issue certificate and auto-configure nginx for HTTPS
sudo certbot --nginx -d goatlandscapeli.com -d www.goatlandscapeli.com

# Certbot will:
# 1. Verify domain ownership via HTTP challenge (DNS must be pointed first)
# 2. Issue the certificate
# 3. Auto-update the nginx config to add HTTPS blocks and HTTP→HTTPS redirect
# 4. Set up auto-renewal via systemd timer

# Verify auto-renewal works
sudo certbot renew --dry-run
```

---

## Step 5 — Verify the Site is Live

```bash
# Check nginx is serving the domain
curl -I http://goatlandscapeli.com
# Expected: 301 redirect to https://

curl -I https://goatlandscapeli.com
# Expected: 200 OK

# Check the homepage loads
curl -s https://goatlandscapeli.com | grep "<title>"
# Expected: Landscaping in Massapequa Park, NY | GOAT Landscaping
```

---

## Step 6 — Future Deploys (When Site is Updated)

When the GitHub repo is updated, pull changes on the server:

```bash
cd /var/www/goatlandscapeli.com/html
sudo git pull origin main

# No nginx restart needed — static files update immediately
```

To automate this, a GitHub Actions webhook or a simple cron job can be set up separately.

---

## Portfolio Dashboard — Add GOAT Landscaping

When adding this site to the portfolio dashboard, use these details:

```
Client:      GOAT Landscaping
Domain:      https://goatlandscapeli.com
GitHub:      https://github.com/yetog/GOAT-Landscaping-main
Stack:       Python static site generator → nginx
Industry:    Landscaping / Outdoor Living
Location:    Massapequa Park, NY (South Shore Long Island)
Phone:       (516) 217-8909
Email:       goatlandscapingli@gmail.com
Status:      Live (pending DNS propagation + SSL)
Notes:       7 services, 15 service area pages, 3 blog posts.
             Zapier webhook active for lead capture.
             Same stack as Green Empire Landscaping.
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| 502 Bad Gateway | nginx is up but something else is wrong — check `sudo nginx -t` and `sudo journalctl -u nginx` |
| 404 on clean URLs | Confirm `try_files $uri $uri/ $uri/index.html =404;` is in the location block |
| SSL certificate error | DNS may not have propagated yet — wait and retry `certbot --nginx` |
| Images not loading | Check file permissions: `sudo chown -R www-data:www-data /var/www/goatlandscapeli.com/html` |
| Old cached content showing | Hard refresh (`Ctrl+Shift+R`) or clear CDN cache if behind Cloudflare |
| www not redirecting | Confirm the www server block is in sites-enabled and nginx was reloaded |
