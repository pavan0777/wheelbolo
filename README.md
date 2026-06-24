# 🎡 Wheel Bolo — Spin the Wheel

A free, production-ready **Spin the Wheel** random name picker and decision wheel,
optimised for SEO + Google AdSense. 100% static — plain HTML,
CSS and vanilla JavaScript, **no framework and no build step**.

## Features

- 🎯 Canvas wheel with smooth deceleration physics + confetti burst from the winning slice
- 🎲 **Random pick** and **Elimination** modes (winner removed after each spin)
- 📲 **Share result** as a 1080×1080 PNG (native share sheet on mobile / download fallback) — built for WhatsApp
- 🔗 **URL state** — your list is encoded in the link (`?names=A,B,C&mode=elim`), so wheels are shareable with no backend
- 🌗 **Light / dark** theme toggle (follows OS preference, `?theme=dark`)
- 🌐 **English / हिंदी** UI toggle, plus ready-made templates for common occasions
- ♿ Keyboard accessible, `aria-live` winner announcements, `prefers-reduced-motion` aware
- ⚡ Self-hosted fonts, zero third-party JS at rest (AdSense aside) — fast Core Web Vitals

## Pages

| URL | Purpose |
|-----|---------|
| `/` | Homepage — generic wheel + `WebApplication` JSON-LD |
| `/classroom-name-picker/` | Random student picker (Hindi + English names) |
| `/diwali-lucky-draw-wheel/` | Diwali lucky draw |
| `/ipl-team-picker-wheel/` | IPL team picker (all 10 teams) |
| `/dinner-decider-wheel/` | "What's for dinner?" Indian food wheel |
| `/secret-santa-picker/` | Gift-exchange draw |
| `/about/`, `/contact/`, `/privacy-policy/` | Trust pages (AdSense) |
| `/sitemap.xml`, `/robots.txt`, `/ads.txt` | Technical/SEO files |

## Project structure

```
/                       index.html + one folder per page (clean URLs)
assets/css/style.css    design tokens, both themes, all components
assets/js/wheel-engine.js  canvas render, spin physics, share, URL state, theme
assets/js/i18n.js       EN/HI dictionary + toggle
assets/fonts/           self-hosted Baloo 2 + Mukta woff2 (latin + devanagari)
assets/img/             favicon, icons, og-default.png
_gen.py                 dev-only generator for the template/trust pages + sitemap
```

> `_gen.py` is a **development convenience** that produces the static page files
> from shared chrome so they stay consistent. The committed `.html` files are the
> deliverable — Cloudflare does not run it. Re-run `python _gen.py` only if you
> change the shared header/footer or page content, then commit the regenerated HTML.

## Run locally

Any static server works. For example:

```bash
npx serve .
# or
python -m http.server 8000
```

Then open <http://localhost:3000> (serve) or <http://localhost:8000> (python).

## Deploy to Cloudflare Pages

1. Push this repo to GitHub.
2. In the Cloudflare dashboard: **Workers & Pages → Create → Pages → Connect to Git**, pick the repo.
3. Build settings:
   - **Framework preset:** None
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/`
4. Deploy. Clean URLs (e.g. `/diwali-lucky-draw-wheel/`) work automatically, and
   `_headers` applies caching + security headers.

`wrangler.toml` is included for reference but is **not required** for a static
Pages deployment.

## Before you go live (checklist)

- [ ] Point `wheelbolo.com` at the Pages project (custom domain).
- [ ] Replace `ca-pub-XXXXXXXXXXXXXXXX` (in every `*.html`) and `pub-XXXXXXXXXXXXXXXX`
      (in `ads.txt`) with your real Google AdSense publisher ID, then resubmit for review.
- [ ] Submit `sitemap.xml` in Google Search Console.

## License

Code: yours to use. Fonts (Baloo 2, Mukta) are under the SIL Open Font License —
see `assets/fonts/LICENSE.txt`.
