# -*- coding: utf-8 -*-
"""Generates Wheel Bolo template + trust pages and technical files.
Output files are committed static HTML — there is NO runtime build step.
Run: python _gen.py  (re-run if shared chrome changes)."""
import os, json, html, datetime, hashlib, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://wheelbolo.com"
ADS_CLIENT = "ca-pub-XXXXXXXXXXXXXXXX"  # <-- replace after AdSense approval

# Content fingerprint for CSS/JS URLs (?v=<hash>). /assets/* is cached for a
# year as `immutable` (see _headers), so the URL itself MUST change whenever
# the file content changes — otherwise Cloudflare's edge and visitors' browsers
# keep serving the old file for up to a year after a deploy.
def _asset_ver():
    h = hashlib.md5()
    for p in ("assets/css/style.css", "assets/js/i18n.js", "assets/js/wheel-engine.js"):
        with open(os.path.join(ROOT, p), "rb") as f:
            h.update(f.read())
    return h.hexdigest()[:10]
ASSET_VER = _asset_ver()

# ---------------------------------------------------------------- shared chrome
def head(title, desc, canonical, *, og_type="website", og_image="/assets/img/og-default.png",
         extra_head="", jsonld=None):
    blocks = []
    blocks.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y0473KQPW5"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-Y0473KQPW5');
  </script>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}" />
  <link rel="canonical" href="{canonical}" />

  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Wheel Bolo" />
  <meta property="og:title" content="{html.escape(title)}" />
  <meta property="og:description" content="{html.escape(desc)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{SITE}{og_image}" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(title)}" />
  <meta name="twitter:description" content="{html.escape(desc)}" />
  <meta name="twitter:image" content="{SITE}{og_image}" />

  <meta name="theme-color" content="#FF8A1E" />
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/assets/img/icon-180.png" />

  <link rel="preload" href="/assets/fonts/baloo2-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/mukta-400-latin.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/assets/css/style.css?v={ASSET_VER}" />

  <!-- Google AdSense — replace {ADS_CLIENT} with your publisher ID after approval -->
  <link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin />
  <link rel="preconnect" href="https://googleads.g.doubleclick.net" crossorigin />
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS_CLIENT}" crossorigin="anonymous"></script>''')
    if jsonld:
        items = jsonld if isinstance(jsonld, list) else [jsonld]
        for obj in items:
            blocks.append('  <script type="application/ld+json">\n' +
                          json.dumps(obj, ensure_ascii=False, indent=2) + '\n  </script>')
    if extra_head:
        blocks.append(extra_head)
    blocks.append("</head>\n<body>")
    blocks.append('  <a class="skip-link" href="#main">Skip to content</a>')
    return "\n".join(blocks)

HEADER = '''
  <header class="site-header">
    <div class="container">
      <a class="brand" href="/"><span aria-hidden="true">🎡</span> Wheel <span class="brand-dot">Bolo</span></a>
      <nav class="main-nav" aria-label="Primary">
        <a href="/#templates" data-i18n="nav.templates">Templates</a>
        <a href="/about/" data-i18n="nav.about">About</a>
        <a href="/contact/" data-i18n="nav.contact">Contact</a>
      </nav>
      <div class="header-tools">
        <button class="icon-btn lang-toggle" type="button" data-lang-toggle aria-label="भाषा / Language">EN / हिं</button>
        <button class="icon-btn" type="button" data-theme-toggle aria-label="Switch theme">🌙</button>
      </div>
    </div>
  </header>
'''

FOOTER = f'''
  <footer class="site-footer">
    <div class="container">
      <div class="footer-brand">
        <a class="brand" href="/"><span aria-hidden="true">🎡</span> Wheel <span class="brand-dot">Bolo</span></a>
        <p>A free spin-the-wheel random picker. Fair, fast, private — and fun.</p>
      </div>
      <div>
        <h2>Wheels</h2>
        <ul class="footer-links">
          <li><a href="/classroom-name-picker/">Classroom Name Picker</a></li>
          <li><a href="/diwali-lucky-draw-wheel/">Diwali Lucky Draw</a></li>
          <li><a href="/ipl-team-picker-wheel/">IPL Team Picker</a></li>
          <li><a href="/dinner-decider-wheel/">Dinner Decider</a></li>
          <li><a href="/secret-santa-picker/">Secret Santa Picker</a></li>
        </ul>
      </div>
      <div>
        <h2>Wheel Bolo</h2>
        <ul class="footer-links">
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="/privacy-policy/">Privacy Policy</a></li>
        </ul>
      </div>
    </div>
    <div class="container footer-bottom">
      © <span data-year>2026</span> Wheel Bolo · Made with 🎡 for the world
    </div>
  </footer>

  <script src="/assets/js/i18n.js?v={ASSET_VER}"></script>
  <script src="/assets/js/wheel-engine.js?v={ASSET_VER}"></script>
</body>
</html>
'''

def app_section(eyebrow, h1, lead):
    return f'''
    <section class="hero">
        <div class="wb-page-wrapper">
          <aside class="wb-ad-sidebar" aria-label="Advertisement">
            <div class="wb-ad-slot-inner">Advertisement</div>
          </aside>

          <div class="wb-tool-center">
            <div class="wb-wheel-title" id="wbWheelTitle" contenteditable="true" spellcheck="false" data-placeholder="Click to name your wheel..." aria-label="Editable wheel title"></div>
            <div class="wheel-stage">
              <canvas id="wheel-canvas" class="wheel-canvas" role="img" aria-label="Spinning wheel of options"></canvas>
              <span class="wheel-pointer" aria-hidden="true">
                <svg viewBox="0 0 46 54" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 27 L43 4 L33 27 L43 50 Z" fill="#E5247B" stroke="#FFFFFF" stroke-width="2.5" stroke-linejoin="round"/>
                </svg>
              </span>
              <button class="wheel-hub-btn" type="button" data-spin aria-label="Spin the wheel">
                <span data-i18n="app.hubSpin">SPIN</span>
              </button>
              <button class="wb-sound-btn wb-sound-icon" id="wbSoundBtn" type="button" aria-label="Toggle sound">🔊</button>
            </div>
            <p id="winner-banner" class="winner-banner" role="status" aria-live="polite"></p>
            <div class="wb-action-bar">
              <button class="btn btn-primary btn-lg" type="button" data-spin>
                <span aria-hidden="true">🎯</span> <span data-spin-label data-i18n="app.spin">Spin the Wheel</span>
              </button>
              <button class="btn btn-secondary" type="button" data-share>
                <span aria-hidden="true">📲</span> <span data-i18n="app.share">Share result</span>
              </button>
              <button class="btn btn-secondary" type="button" data-copy-link>
                <span aria-hidden="true">🔗</span> <span data-i18n="app.copyLink">Copy link</span>
              </button>
            </div>
          </div>

          <aside class="wb-right-panel" aria-label="Wheel options">
            <div class="wb-tabs" role="tablist">
              <button class="wb-tab-btn active" type="button" role="tab" data-tab="entries" aria-selected="true"><span aria-hidden="true">📝</span> Entries <span class="wb-entry-count-badge" id="entryCountBadge">0</span></button>
              <button class="wb-tab-btn" type="button" role="tab" data-tab="results" aria-selected="false"><span aria-hidden="true">🏆</span> Results</button>
              <button class="wb-tab-btn" type="button" role="tab" data-tab="customize" aria-selected="false"><span aria-hidden="true">🎨</span> Customize</button>
            </div>
            <div class="wb-tab-pane active" id="tab-pane-entries" role="tabpanel">
              <div id="wbEditorSlotDesktop">
                <div class="panel wb-editor" id="wbEditorPanel">
                  <label class="field-label" for="entries-input" data-i18n="app.entriesLabel">Enter names or options (one per line)</label>
                  <textarea id="entries-input" class="entries-input" spellcheck="false"
                    aria-describedby="entries-meta"
                    data-i18n-attr="placeholder:app.entriesPlaceholder"
                    placeholder="One per line"></textarea>
                  <p id="entries-meta" class="entries-meta"></p>
                  <div class="controls-row">
                    <span class="field-label" id="mode-label" style="margin:0" data-i18n="app.mode">Mode</span>
                    <div class="segmented" role="radiogroup" aria-labelledby="mode-label">
                      <input type="radio" name="mode" id="mode-random" value="random" checked />
                      <label for="mode-random" data-i18n="app.modeRandom">Random pick</label>
                      <input type="radio" name="mode" id="mode-elim" value="elim" />
                      <label for="mode-elim" data-i18n="app.modeElim">Elimination</label>
                    </div>
                  </div>
                  <p id="mode-hint" class="entries-meta"></p>
                  <div class="action-row">
                    <button class="btn btn-secondary" type="button" data-shuffle data-i18n="app.shuffle">Shuffle</button>
                    <button class="btn btn-secondary" type="button" data-reset data-i18n="app.reset">Reset</button>
                  </div>
                </div>
              </div>
              <div class="wb-restore-banner" id="wbRestoreBanner">
                <strong>Restore your entries?</strong><br />
                You have <span id="wbRestoreCount">0</span> saved from last time.
                <div class="wb-restore-actions">
                  <button type="button" class="wb-restore-yes" id="wbRestoreYes">Restore</button>
                  <button type="button" class="wb-restore-no" id="wbRestoreNo">Dismiss</button>
                </div>
              </div>
              <ul class="wb-entries-list" id="wbEntriesList" aria-label="Current entries"></ul>
              <p class="wb-panel-hint">Tap × to remove a name.</p>
            </div>
            <div class="wb-tab-pane" id="tab-pane-results" role="tabpanel">
              <ul class="wb-results-list" id="wbResultsList" aria-live="polite" aria-label="Spin results"></ul>
              <p class="wb-results-empty" id="wbResultsEmpty">No spins yet. Hit Spin!</p>
              <div class="wb-legacy-history" hidden>
                <p id="history-empty" class="history-empty" data-i18n="history.empty">No spins yet.</p>
                <ol id="history-list" class="history-list"></ol>
              </div>
            </div>
            <div class="wb-tab-pane" id="tab-pane-customize" role="tabpanel">
              <div class="wb-customize-section">
                <span class="wb-customize-label">Wheel colours</span>
                <div class="wb-palette-grid" id="wbPaletteGrid"></div>
              </div>
              <div class="wb-customize-section">
                <span class="wb-customize-label">Background</span>
                <div class="wb-bg-grid" id="wbBgGrid"></div>
              </div>
              <div class="wb-customize-section">
                <span class="wb-customize-label">Spin duration</span>
                <div class="wb-sound-row">
                  <span aria-hidden="true">⏱️</span>
                  <input type="range" class="wb-dur-slider" min="1" max="8" step="0.5" value="4" aria-label="Spin duration in seconds" />
                  <span class="wb-dur-value">4s</span>
                </div>
              </div>
              <div class="wb-customize-section">
                <span class="wb-customize-label">Sound</span>
                <div class="wb-sound-row">
                  <button class="wb-sound-icon" id="wbSoundIcon" type="button" aria-label="Toggle sound">🔊</button>
                  <input type="range" class="wb-sound-slider" id="wbSoundVolume" min="0" max="1" step="0.05" value="0.15" aria-label="Sound volume" />
                </div>
              </div>
            </div>
          </aside>
        </div>

        <div class="container">
        <div class="wb-mobile-tabs">
          <div class="wb-mobile-tab-bar">
            <button class="wb-mobile-tab-btn active" type="button" data-mtab="entries"><span aria-hidden="true">📝</span> Entries <span class="wb-entry-count-badge" id="mobileEntryBadge">0</span></button>
            <button class="wb-mobile-tab-btn" type="button" data-mtab="results"><span aria-hidden="true">🏆</span> Results</button>
            <button class="wb-mobile-tab-btn" type="button" data-mtab="customize"><span aria-hidden="true">🎨</span> Customize</button>
          </div>
          <div class="wb-mobile-tab-pane active" id="mobile-pane-entries">
            <div id="wbEditorSlotMobile"></div>
            <ul class="wb-entries-list" id="wbEntriesListMobile" aria-label="Current entries"></ul>
            <p class="wb-panel-hint">Tap × to remove a name.</p>
          </div>
          <div class="wb-mobile-tab-pane" id="mobile-pane-results">
            <ul class="wb-results-list" id="wbResultsListMobile" aria-live="polite"></ul>
            <p class="wb-results-empty" id="wbResultsEmptyMobile">No spins yet. Hit Spin!</p>
          </div>
          <div class="wb-mobile-tab-pane" id="mobile-pane-customize">
            <div class="wb-customize-section">
              <span class="wb-customize-label">Wheel colours</span>
              <div class="wb-palette-grid" id="wbPaletteGridMobile"></div>
            </div>
            <div class="wb-customize-section">
              <span class="wb-customize-label">Background</span>
              <div class="wb-bg-grid" id="wbBgGridMobile"></div>
            </div>
            <div class="wb-customize-section">
              <span class="wb-customize-label">Spin duration</span>
              <div class="wb-sound-row">
                <span aria-hidden="true">⏱️</span>
                <input type="range" class="wb-dur-slider" min="1" max="8" step="0.5" value="4" aria-label="Spin duration in seconds" />
                <span class="wb-dur-value">4s</span>
              </div>
            </div>
            <div class="wb-customize-section">
              <span class="wb-customize-label">Sound</span>
              <div class="wb-sound-row">
                <button class="wb-sound-icon" id="wbSoundIconMobile" type="button" aria-label="Toggle sound">🔊</button>
                <input type="range" class="wb-sound-slider" id="wbSoundVolumeMobile" min="0" max="1" step="0.05" value="0.15" aria-label="Sound volume" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <canvas id="confetti-canvas" class="confetti-canvas" aria-hidden="true"></canvas>
    </section>

    <section class="section hero-copy">
      <div class="container">
        <span class="hero-eyebrow">{eyebrow}</span>
        <h1>{html.escape(h1)}</h1>
        <p class="hero-lead">{html.escape(lead)}</p>
      </div>
    </section>
'''

AD_SLOT = f'''
    <div class="container">
      <div class="ad-slot">
        <ins class="adsbygoogle" style="display:block" data-ad-client="{ADS_CLIENT}" data-ad-slot="0000000000" data-ad-format="auto" data-full-width-responsive="true"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
      </div>
    </div>
'''

def breadcrumbs(name):
    return f'''
    <div class="container">
      <nav class="breadcrumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> <span aria-hidden="true">›</span>
        <span aria-current="page">{html.escape(name)}</span>
      </nav>
    </div>
'''

def breadcrumb_jsonld(name, url):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": url},
        ],
    }

def webapp_jsonld(name, url, desc, category="UtilitiesApplication",
                  currency="INR", langs=None, features=None):
    if langs is None:
        langs = ["en", "hi"]
    if features is None:
        features = [
            "Random winner selection",
            "Elimination mode for no-repeat picks",
            "Hindi and English interface",
            "Shareable result card",
            "Works on mobile without install",
        ]
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": name,
        "url": url,
        "description": desc,
        "applicationCategory": category,
        "operatingSystem": "All",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": currency},
        "inLanguage": langs,
        "featureList": features,
    }

def faq_jsonld(qa):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in qa
        ],
    }

def faq_html(qa):
    items = "\n".join(f'''        <details class="faq-item">
          <summary>{html.escape(q)}</summary>
          <div class="faq-answer"><p>{html.escape(a)}</p></div>
        </details>''' for q, a in qa)
    return f'''
        <h2>Frequently asked questions</h2>
{items}
'''

def related(cards):
    items = "\n".join(f'''          <a class="template-card" href="{href}">
            <span class="tc-emoji" aria-hidden="true">{emoji}</span>
            <span class="tc-title">{title}</span>
            <p class="tc-desc">{desc}</p>
          </a>''' for emoji, title, desc, href in cards)
    return f'''
    <section class="section section-tinted">
      <div class="container">
        <div class="section-head"><h2 data-i18n="related.title">You might also like</h2></div>
        <div class="related-grid">
{items}
        </div>
      </div>
    </section>
'''

# Product-wide FAQ appended to every wheel page (covers the shared feature set).
PRODUCT_FAQ = [
    ("Is there a dark mode?",
     "Yes. Tap the sun/moon button in the top bar to switch between light and dark themes. Wheel Bolo also follows your device's system preference automatically on your first visit."),
    ("What languages does Wheel Bolo support?",
     "The interface is available in 17 languages including Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Marathi, Punjabi and Urdu. Tap the language button to switch, and type entry names in any script, including Devanagari."),
    ("Does the wheel play a sound?",
     "Yes. The wheel makes a soft ticking sound as it spins and a short chime when a winner is picked. Use the sound button or the volume slider in the Customize tab to adjust or mute it. Sound stays off if your device requests reduced motion."),
    ("Can I change the wheel's colours and background?",
     "Yes. Open the Customize tab to choose a colour palette (Pastel, Ocean, Sunset, Forest and more) and a background theme. Your choice is remembered on your device for next time."),
    ("Can I share the result?",
     "Yes. After the wheel stops, tap Share result to create a 1080x1080 winner image. On phones it opens the share sheet (WhatsApp, Instagram and more); on desktop it downloads. Free, with no sign-up."),
]

# ------------------------------------------------------------------- page data
CARDS = {
  "classroom": ("🎓", "Classroom Name Picker", "Pick a student fairly for answers, turns and group work.", "/classroom-name-picker/"),
  "diwali":    ("🪔", "Diwali Lucky Draw", "Run a fair lucky draw at your Diwali party or office.", "/diwali-lucky-draw-wheel/"),
  "ipl":       ("🏏", "IPL Team Picker", "Spin to assign an IPL team for fantasy or gully cricket.", "/ipl-team-picker-wheel/"),
  "dinner":    ("🍛", "What's for Dinner?", "End the daily debate — spin the wheel of dinner ideas.", "/dinner-decider-wheel/"),
  "santa":     ("🎁", "Secret Santa Picker", "Draw names for a gift exchange without rigging.", "/secret-santa-picker/"),
  "birthday":  ("🎂", "Birthday Wheel Generator", "Spin to pick party games, a lucky guest or who goes first.", "/birthday-wheel-generator/"),
  "yesno":     ("🤔", "Yes or No Wheel", "Can't decide? Let the wheel say yes or no.", "/yes-no-wheel/"),
  "truthdare": ("😈", "Truth or Dare Wheel", "Spin for truths and dares — instant party fun.", "/truth-or-dare-wheel/"),
  "team":      ("👥", "Team Picker Wheel", "Split players into fair teams with a spin.", "/team-picker-wheel/"),
  "prize":     ("🎟️", "Prize Wheel", "Spin a prize wheel for rewards and offers.", "/prize-wheel/"),
  "giveaway":  ("🎉", "Giveaway Wheel", "Pick a random giveaway winner — fair and live.", "/giveaway-wheel/"),
  "reward":    ("⭐", "Classroom Reward Wheel", "Reward students with fun classroom perks.", "/classroom-reward-wheel/"),
  "antakshari":("🎵", "Antakshari Team Picker", "Spin to split players into fair Antakshari teams.", "/antakshari-team-picker/"),
  "kitty":     ("🪅", "Kitty Party Wheel", "Pick games, hosts and lucky-draw winners for kitty parties.", "/kitty-party-wheel/"),
  "office":    ("🏢", "Office Lucky Draw", "Run a fair office lucky draw, tambola or prize pick.", "/office-lucky-draw-wheel/"),
  "holi":      ("🌈", "Holi Team Picker", "Spin to make colour teams for Holi games.", "/holi-team-picker/"),
  "gully":     ("🏟️", "Gully Cricket Picker", "Split players into fair gully cricket teams with a spin.", "/gully-cricket-team-picker/"),
  "study":     ("📚", "Study Topic Picker", "Spin to decide which subject or chapter to study next.", "/study-topic-picker/"),
  "iplplayer": ("🏏", "IPL Player Picker", "Spin for a random IPL player for fantasy or friendly debates.", "/ipl-player-picker-wheel/"),
  "iplauction":("🔨", "IPL Auction Wheel", "Spin to pick the next category in a mock IPL auction.", "/ipl-auction-wheel/"),
  "cricket":   ("🌍", "Cricket Team Picker", "Spin for a random international cricket team.", "/cricket-team-picker/"),
  "football":  ("⚽", "Football Team Picker", "Spin for a random football club — PL, La Liga and more.", "/football-team-picker/"),
}

TEMPLATES = [
  {
    "slug": "classroom-name-picker",
    "name": "Classroom Name Picker",
    "title": "Classroom Name Picker — Free Random Student Selector for Indian Teachers | Wheel Bolo",
    "desc": "Free classroom name picker for Indian teachers. Spin the wheel to randomly select a student for questions, turns or group work — works in Hindi and English. No sign-up needed.",
    "app_desc": "Free random student selector for Indian teachers. Spin the wheel to pick a student fairly in Hindi or English.",
    "app_category": "EducationApplication",
    "features": ["Random student selection", "Elimination mode for no-repeat picks",
                 "Hindi and English support", "WhatsApp result sharing",
                 "Works on mobile without install"],
    "eyebrow": "🎓 For Indian teachers",
    "h1": "Classroom Name Picker for Indian Teachers",
    "lead": "Call on students fairly. Add your class list, spin the wheel, and let chance decide who answers next — in Hindi or English.",
    "mode": "random",
    "entries": ["Aarav","Priya","Rohan","Ananya","Vikas","Sneha","Arjun","Divya","Karthik","Meera"],
    "article": '''
        <h2>How to use the classroom name picker</h2>
        <p>The classroom name picker takes three simple steps, and it works just as well in Hindi as it does in English — type names in Devanagari (देवनागरी) or the Roman alphabet and the wheel handles both.</p>
        <ol>
          <li><strong>Add your student names.</strong> Type one name per line, or paste your class list straight from a register. The wheel comes pre-loaded with ten sample names so you can try it in seconds.</li>
          <li><strong>Choose a mode.</strong> Pick <em>Random</em> to call on any student each spin, or <em>Elimination</em> so every student is picked once before anyone repeats — ideal for turn-taking.</li>
          <li><strong>Spin and announce the winner.</strong> Tap the wheel, wait for the confetti, and read out the name it lands on. Then hand the next question to chance, not to the same raised hands.</li>
        </ol>

        <h2>When to use a random student selector</h2>
        <p>A random name wheel is useful far beyond just asking questions. Here are six everyday moments in an Indian classroom where it keeps things fair and quick. It works for CBSE, ICSE, State Board classrooms alike — the tool does not care which syllabus you follow.</p>
        <ul>
          <li><strong>Morning assembly and prayer duty rotation.</strong> Instead of the same confident students leading prayer or the pledge every week, spin to rotate assembly duties. Over a term, everyone gets a fair turn at the mic without you having to keep a chart.</li>
          <li><strong>Picking students to answer in-class questions.</strong> Cold-calling with a wheel removes any hint of teacher bias — the class can see the pick is random. It keeps every child alert, because anyone could be next, not just the front bench.</li>
          <li><strong>Forming project groups fairly.</strong> Use Elimination mode to draw students one by one into balanced groups. Nobody is picked last, and there are no complaints that friends were kept together or split up on purpose.</li>
          <li><strong>Selecting students for school competitions and elocutions.</strong> When more children volunteer than there are slots for the inter-house elocution or quiz, a spin makes the shortlist transparent and drama-free for both students and parents.</li>
          <li><strong>Assigning blackboard duty and class monitor duty.</strong> Rotate who cleans the board, collects notebooks, or acts as monitor for the day. The wheel spreads these small responsibilities evenly across the whole class.</li>
          <li><strong>Choosing volunteers for science experiments or drama.</strong> For a demonstration in the lab or a role in the class play, spin to pick who comes up next — every child gets a fair shot at the hands-on, exciting parts.</li>
        </ul>

        <h2>Why fair random selection matters in Indian classrooms</h2>
        <p>Research in educational psychology consistently shows that <strong>random questioning improves engagement</strong>: when students know anyone can be called, more of them stay mentally prepared with an answer. It also reduces unconscious teacher bias. In many Indian classrooms, teachers tend to call on the same confident front-row students repeatedly, while children at the back or those who are shy slowly disengage. A visible, random wheel breaks that pattern — every name has an equal chance, participation spreads across the whole room, and no student feels singled out or ignored. Fair selection is not just about being nice; it measurably lifts attention and learning for the class as a whole.</p>
''',
    "faq": [
      ("Is this classroom name picker free to use?",
       "Yes, Wheel Bolo's classroom name picker is completely free. No sign-up, no download, and no hidden charges. Open it on your phone or laptop and start using it immediately."),
      ("Can I use this in Hindi?",
       "Yes. Wheel Bolo supports both Hindi and English. You can type student names in Hindi (Devanagari script) and the wheel will display and pick them correctly."),
      ("What is Elimination mode?",
       "In Elimination mode, each student picked is removed from the wheel after their turn. This ensures every student gets a chance before anyone is picked twice — ideal for oral exams, presentations, or class activities."),
      ("How many student names can I add?",
       "You can add as many names as you need. The wheel automatically adjusts the size of each segment. It works well for small groups of 5 and large classes of 60+."),
      ("Is this tool different from ClassTools?",
       "Wheel Bolo is a free alternative to ClassTools' random name picker. It is designed specifically for Indian classrooms with Hindi language support, WhatsApp sharing, and templates for Indian school activities. No account or registration is required."),
      ("Does it work on mobile phones?",
       "Yes. Wheel Bolo is built mobile-first. It works on any Android or iPhone browser without installing an app. Most Indian teachers use it directly from their phone in the classroom."),
    ],
    "related": ["study","antakshari","dinner"],
  },
  {
    "slug": "diwali-lucky-draw-wheel",
    "name": "Diwali Lucky Draw",
    "title": "Diwali Lucky Draw Wheel — Free Online Lucky Draw for Diwali Party | Wheel Bolo",
    "desc": "Run a fair Diwali lucky draw online. Add participant names, spin the wheel, announce the winner. Free for office parties, housing societies and family Diwali celebrations.",
    "app_category": "GameApplication",
    "eyebrow": "🪔 Happy Diwali",
    "h1": "Diwali Lucky Draw Wheel",
    "lead": "Pick a lucky winner the fun way. Add the names, spin, and let the festival of lights choose.",
    "mode": "elim",
    "entries": ["Priya","Rohan","Aunty ji","Sharma uncle","Neha","Vikram","Meera","Anil",
                "Pooja","Sanjay","Kavya","Deepak"],
    "article": '''
        <h2>How to run a Diwali lucky draw online</h2>
        <p>No Diwali party is complete without a lucky draw — and this wheel replaces the bowl of folded paper chits entirely. Add every guest's name (one per line, or paste your list), keep <em>Elimination</em> mode on so each winner is removed as they are drawn, and spin once per prize from the smallest gift up to the grand prize. Each spin uses your browser's secure random generator, so there is genuinely no way to rig it — and everyone can watch the wheel land on a winner in real time. Tap Share result to send the winner card straight to your family or office WhatsApp group.</p>
        <h2>Perfect for these Diwali celebrations</h2>
        <ul>
          <li><strong>Office Diwali party:</strong> draw names for gift hampers, sweets boxes or the grand prize in front of the whole team.</li>
          <li><strong>Housing society event:</strong> run the annual society lucky draw on a projector so every flat can see it is fair.</li>
          <li><strong>Family gathering:</strong> add cousins, uncles and aunties and let the wheel pick who wins the taash-night pot or the biggest mithai box.</li>
          <li><strong>School Diwali mela:</strong> use it at a stall to pick raffle winners without printing tickets.</li>
          <li><strong>Online gift exchange:</strong> spin over a video call so far-away relatives can join the celebration too.</li>
        </ul>
        <h2>Tips for a fair Diwali lucky draw</h2>
        <p>Show the full list of names on the screen before you spin, so everyone can confirm they are included. Use Elimination mode when you have several prizes so nobody wins twice. Screenshot or share the winner card as a record, and share the wheel link so anyone can reopen the exact same draw and verify it. Light the diyas, gather around the phone, and let Wheel Bolo pick your winners. Shubh Deepavali!</p>
''',
    "faq": [
      ("Is the Diwali lucky draw wheel free?",
       "Yes, it is completely free with no sign-up or download. Add your participant names and spin as many times as your celebration needs."),
      ("How do I give away more than one Diwali prize?",
       "Keep Elimination mode on. Each name the wheel lands on is removed after the spin, so you can draw a different winner for every prize without anyone being picked twice."),
      ("Is the draw genuinely random and fair?",
       "Yes. Every spin uses your browser's secure random generator, so each name has an exactly equal chance. You can show the list on screen before spinning so everyone sees it is fair."),
      ("Can I share the winner on WhatsApp?",
       "Yes. After the wheel stops, tap Share result to send a winner card to your family or office WhatsApp group, or Copy link to share the exact wheel."),
    ],
    "related": ["kitty","office","prize"],
  },
  {
    "slug": "ipl-team-picker-wheel",
    "name": "IPL Team Picker",
    "title": "IPL Team Picker Wheel — Spin to Get a Random IPL 2026 Team | Wheel Bolo",
    "desc": "Spin the wheel to get a random IPL team for fantasy cricket, gully cricket or friendly bets. All 10 IPL 2026 teams loaded. Free, instant, no sign-up.",
    "app_desc": "Randomly pick an IPL team by spinning the wheel. Includes all 10 IPL 2026 teams. Perfect for fantasy cricket, gully cricket team assignment, and friendly bets.",
    "app_category": "GameApplication",
    "team_data": {
      "Chennai Super Kings":         {"color": "#FDB913", "abbr": "CSK",  "textColor": "#1A1A1A"},
      "Mumbai Indians":              {"color": "#004BA0", "abbr": "MI",   "textColor": "#FFFFFF"},
      "Royal Challengers Bengaluru": {"color": "#D11D1D", "abbr": "RCB",  "textColor": "#FFD700"},
      "Kolkata Knight Riders":       {"color": "#3A225D", "abbr": "KKR",  "textColor": "#FFD700"},
      "Sunrisers Hyderabad":         {"color": "#FF6D22", "abbr": "SRH",  "textColor": "#1A1A1A"},
      "Delhi Capitals":              {"color": "#17479E", "abbr": "DC",   "textColor": "#FFFFFF"},
      "Punjab Kings":                {"color": "#AA4545", "abbr": "PBKS", "textColor": "#FFFFFF"},
      "Rajasthan Royals":            {"color": "#254AA5", "abbr": "RR",   "textColor": "#FFB6D9"},
      "Gujarat Titans":              {"color": "#1C1C1C", "abbr": "GT",   "textColor": "#D4B15A"},
      "Lucknow Super Giants":        {"color": "#5AACE3", "abbr": "LSG",  "textColor": "#1A1A1A"},
    },
    "eyebrow": "🏏 Cricket season",
    "h1": "IPL Team Picker Wheel",
    "lead": "Let the wheel hand you an IPL team. All 10 teams loaded and ready — spin and play.",
    "mode": "elim",
    "entries": ["Chennai Super Kings","Mumbai Indians","Royal Challengers Bengaluru",
                "Kolkata Knight Riders","Sunrisers Hyderabad","Delhi Capitals",
                "Punjab Kings","Rajasthan Royals","Gujarat Titans","Lucknow Super Giants"],
    "article": '''
        <h2>How to use the IPL team picker</h2>
        <ol>
          <li><strong>Open the page.</strong> All ten IPL 2026 teams are already loaded on the wheel, so there is nothing to set up.</li>
          <li><strong>Spin.</strong> Tap the wheel and it lands on a random team — that is your team for the match, the draft, or the bet.</li>
          <li><strong>Share on WhatsApp.</strong> Hit Share result to send the team card to your group, or Copy link to share the exact wheel with friends.</li>
        </ol>
        <h2>Uses for the IPL team picker wheel</h2>
        <ul>
          <li><strong>Office IPL pool:</strong> assign each colleague a team to follow for the season and track who tops the table.</li>
          <li><strong>Fantasy league draft:</strong> deal out teams fairly when several friends are drafting.</li>
          <li><strong>Gully cricket team assignment:</strong> decide which franchise each side plays as in your mohalla match.</li>
          <li><strong>Settling debates:</strong> end the "which team do I support today?" argument with a neutral spin.</li>
        </ul>
        <h2>IPL 2026 teams on the wheel</h2>
        <ul>
          <li><strong>Chennai Super Kings</strong> — Chennai, home at the M. A. Chidambaram Stadium; the "Yellow Army".</li>
          <li><strong>Mumbai Indians</strong> — Mumbai, home at the Wankhede Stadium; the "Paltan".</li>
          <li><strong>Royal Challengers Bengaluru</strong> — Bengaluru, home at the M. Chinnaswamy Stadium; "RCB".</li>
          <li><strong>Kolkata Knight Riders</strong> — Kolkata, home at Eden Gardens; "KKR".</li>
          <li><strong>Delhi Capitals</strong> — Delhi, home at the Arun Jaitley Stadium; "DC".</li>
          <li><strong>Punjab Kings</strong> — Mohali/Punjab, home at the PCA Stadium; "PBKS".</li>
          <li><strong>Rajasthan Royals</strong> — Jaipur, home at the Sawai Mansingh Stadium; "RR".</li>
          <li><strong>Sunrisers Hyderabad</strong> — Hyderabad, home at the Rajiv Gandhi Stadium; "SRH".</li>
          <li><strong>Lucknow Super Giants</strong> — Lucknow, home at the Ekana Stadium; "LSG".</li>
          <li><strong>Gujarat Titans</strong> — Ahmedabad, home at the Narendra Modi Stadium; "GT".</li>
        </ul>
''',
    "faq": [
      ("Which IPL teams are on the wheel?",
       "All 10 IPL 2026 teams are included: Mumbai Indians, Chennai Super Kings, Royal Challengers Bengaluru, Kolkata Knight Riders, Delhi Capitals, Punjab Kings, Rajasthan Royals, Sunrisers Hyderabad, Lucknow Super Giants, and Gujarat Titans."),
      ("Can I remove my own team from the wheel?",
       "Yes. Edit the list and delete your team name before spinning. The wheel will redistribute evenly among the remaining teams."),
      ("Is this useful for IPL fantasy league team selection?",
       "Yes. Many fantasy cricket players use the IPL team picker to randomly decide which team to support each match, or to assign rival teams in office leagues and friendly competitions."),
      ("Can I share my result on WhatsApp?",
       "Yes. After the wheel stops, tap the Share Result button to send the winner directly to WhatsApp — including the team name and a fun caption."),
      ("Does the wheel remember which teams were picked?",
       "Switch to Elimination mode to automatically remove each picked team after every spin. This is useful when assigning different IPL teams to multiple people in a group."),
    ],
    "related": ["gully","study","antakshari"],
  },
  {
    "slug": "dinner-decider-wheel",
    "name": "Dinner Decider",
    "title": "Dinner Decider Wheel — Spin to Pick What to Eat Tonight | Wheel Bolo",
    "desc": "Can't decide what to make for dinner? Spin the Indian dinner decider wheel. Includes dal-rice, roti-sabzi, biryani, pasta and more. Add your own options too.",
    "eyebrow": "🍛 What's cooking tonight?",
    "h1": "What's for Dinner? Decision Wheel",
    "lead": "End the daily 'kya banaye?' debate. Spin the wheel of Indian favourites and let dinner decide itself.",
    "mode": "random",
    "entries": ["Dal Chawal","Roti Sabzi","Biryani","Rajma Chawal","Chole Bhature","Khichdi",
                "Pasta","Maggi","Paneer","Order In"],
    "article": '''
        <h2>Never argue about dinner again</h2>
        <p>"Aaj khaane mein kya banaye?" is the question that stumps every household, every single evening. The Dinner Decider takes the decision off your plate. The wheel comes loaded with everyday Indian favourites — from dal chawal and roti sabzi to rajma chawal, chole bhature, biryani and the ever-reliable Maggi — plus a "Paneer" night for guests and an "Order In" slice for when you just can't be bothered to cook.</p>
        <h3>How to use it</h3>
        <ol>
          <li>Spin as-is for a quick decision, or edit the list to match what's in your kitchen today.</li>
          <li>Add family favourites, leftovers to finish, or restaurants you like to order from.</li>
          <li>Spin — and commit to whatever the wheel lands on. No re-rolls!</li>
        </ol>
        <h3>Make it your own</h3>
        <p>Cooking for the week? Add seven options and use it to plan a different meal each day. Running a tiffin service or a small home kitchen? Use it to surprise customers with a dish of the day. Because your list is saved right in the page link, you can bookmark your personalised dinner wheel or share it with the family cook in one tap. Simple, fast, and a little bit fun — exactly what a tired evening needs.</p>
''',
    "related": ["study","kitty","santa"],
  },
  {
    "slug": "secret-santa-picker",
    "name": "Secret Santa Picker",
    "title": "Secret Santa Picker — Free Online Name Draw for Gift Exchange | Wheel Bolo",
    "desc": "Draw names for Secret Santa online. Add your group, spin the wheel, share results on WhatsApp. Free Secret Santa name picker for office and family gift exchanges in India.",
    "eyebrow": "🎁 Gift exchange",
    "h1": "Secret Santa Name Picker",
    "lead": "Draw names for your gift exchange without folded chits. Spin, reveal, and keep it fair.",
    "mode": "elim",
    "entries": ["Aisha","Rahul","Sneha","Karan","Tina","Mohit","Riya","Farhan","Jaspreet","Nikhil"],
    "article": '''
        <h2>A fairer way to draw Secret Santa names</h2>
        <p>Pulling names out of a hat works — until someone draws their own name, or two people peek. The Secret Santa Picker keeps your gift exchange fair and fuss-free. Add everyone taking part, then spin to reveal who's up. With <em>Elimination</em> mode on, each name is removed after it's picked, so nobody is chosen twice and the draw moves cleanly through the whole group.</p>
        <h3>How to run the draw</h3>
        <ul>
          <li>Type each participant's name, one per line.</li>
          <li>Spin to reveal the order, or to assign gift recipients one at a time.</li>
          <li>Hand the phone to the next person, or share the result privately.</li>
        </ul>
        <h3>Perfect for the whole season</h3>
        <p>Whether it's a Christmas Secret Santa at the office, a New Year gift exchange with friends, or a birthday game, this wheel handles any group draw. It works equally well for picking who goes first in a party game, who hosts next, or who does the washing up. Nothing is stored, so when the draw is done, it's done — reset and start a fresh one any time.</p>
''',
    "related": ["office","prize","diwali"],
  },
  {
    "slug": "birthday-wheel-generator",
    "name": "Birthday Wheel Generator",
    "title": "Birthday Wheel Generator — Party Game Picker | Wheel Bolo",
    "desc": "A free birthday wheel generator — spin to pick party games, choose a lucky guest, or decide who opens the next gift. Add your own options and play. No sign-up.",
    "eyebrow": "🎂 Party time",
    "h1": "Birthday Wheel Generator",
    "lead": "Make the party fair and fun — spin to pick the next game, a lucky guest, or who goes first.",
    "mode": "random",
    "entries": ["Musical Chairs", "Pass the Parcel", "Treasure Hunt", "Dance-off", "Balloon Pop",
                "Pin the Tail", "Lemon & Spoon Race", "Tug of War", "Karaoke", "Freeze Dance",
                "Charades", "Piñata"],
    "article": '''
        <h2>Spin up the birthday fun</h2>
        <p>Every birthday party hits the same moment: a room full of excited kids (or grown-ups) and nobody agreeing on what to do next. The Birthday Wheel Generator settles it in one spin. Load it with party games, give it a flick, and let the wheel decide the next activity — no arguments, no "but I wanted to go first", just instant fun with a confetti finish.</p>
        <h3>Fun ways to use the wheel</h3>
        <ul>
          <li><strong>Pick the next game:</strong> spin the pre-loaded list of classic party games and play whatever it lands on.</li>
          <li><strong>Choose a lucky guest:</strong> swap in your guests' names to pick who wins a prize, cuts the cake, or bursts the piñata.</li>
          <li><strong>Decide the order:</strong> who opens the first gift, who goes first in a game, or who picks the music.</li>
          <li><strong>Settle a tie:</strong> two kids both want the same balloon? Let the wheel be the referee.</li>
        </ul>
        <h3>Make it your own</h3>
        <p>The wheel starts with a dozen crowd-pleasing games, but you can replace them with anything — your child's favourite activities, party challenges, dares, or the names of every guest. Type one option per line, or paste a list. Because your setup is saved right in the page link, you can build the perfect party wheel in advance and reopen it on the day, or share it with co-hosts so everyone has the same games ready.</p>
        <p>It is free, works on any phone at the party, and keeps everything in your browser — spin as many times as the celebration needs.</p>
''',
    "related": ["classroom", "santa", "dinner"],
  },
  {
    "slug": "yes-no-wheel",
    "name": "Yes or No Wheel",
    "title": "Yes or No Wheel — Free Random Decision Maker | Wheel Bolo",
    "desc": "A free Yes or No wheel — spin to make a quick, unbiased decision. Perfect when you just can't choose. Add your own options too. No sign-up, works on any phone.",
    "eyebrow": "🤔 Can't decide?",
    "h1": "Yes or No Wheel",
    "lead": "Stuck on a decision? Give the wheel a spin and let chance settle it — yes or no.",
    "mode": "random",
    "entries": ["Yes", "No"],
    "article": '''
        <h2>Let the wheel decide</h2>
        <p>Some decisions are too small to agonise over and too annoying to keep debating. Should you order pizza? Go for the walk? Send the text? The Yes or No Wheel gives you a fast, fair, 50/50 answer with a satisfying spin — no overthinking required.</p>
        <h3>When to use it</h3>
        <ul>
          <li><strong>Everyday dilemmas:</strong> stay in or go out, buy it or skip it, now or later.</li>
          <li><strong>Settle a standoff:</strong> when two people can't agree, let the wheel be neutral.</li>
          <li><strong>Games &amp; dares:</strong> add a fun rule that whatever it lands on, you have to do.</li>
          <li><strong>Beat decision fatigue:</strong> hand the small calls to chance and save your energy.</li>
        </ul>
        <h3>Make it yours</h3>
        <p>The wheel starts as a clean Yes / No, but you are not limited to two answers. Add "Maybe", "Ask again later", or any custom options to build your own decision spinner. Type one option per line and the wheel updates instantly. Your setup travels in the page link, so you can bookmark a custom wheel or share it with a friend who needs to make the same call.</p>
        <p>It is completely free, needs no account, and runs entirely in your browser — spin as many times as you like.</p>
''',
    "related": ["truthdare", "prize", "dinner"],
  },
  {
    "slug": "truth-or-dare-wheel",
    "name": "Truth or Dare Wheel",
    "title": "Truth or Dare Wheel — Free Party Game Spinner | Wheel Bolo",
    "desc": "A free Truth or Dare wheel loaded with fun, family-friendly prompts. Spin to get a truth or a dare — great for parties, sleepovers and game nights. Add your own too.",
    "eyebrow": "😈 Game night",
    "h1": "Truth or Dare Wheel",
    "lead": "Spin for a truth or a dare and let the party decide your fate — fair and random every time.",
    "mode": "random",
    "entries": ["Truth: share a hidden talent", "Dare: do 10 jumping jacks", "Truth: funniest memory",
                "Dare: talk in a funny accent", "Truth: dream holiday", "Dare: sing a song chorus",
                "Truth: childhood nickname", "Dare: show your best dance move"],
    "article": '''
        <h2>The classic game, now on a wheel</h2>
        <p>Truth or Dare is a sleepover and party staple — but someone always argues about whose turn it is or what they have to do. The Truth or Dare Wheel takes over: give it a spin and it lands on a random prompt for whoever is up. No bias, no repeats of "I pick truth again", just instant fun with a confetti finish.</p>
        <h3>How to play</h3>
        <ul>
          <li>Sit in a circle and decide who spins first.</li>
          <li>Spin the wheel — do whatever truth or dare it lands on.</li>
          <li>Pass the phone to the next player and spin again.</li>
        </ul>
        <h3>Build your own deck</h3>
        <p>The wheel comes with a set of light, family-friendly prompts so you can start playing in seconds. But the best games are personalised — replace the prompts with your own inside jokes, challenges, or questions. Type one per line, mix easy and bold, and tailor it to your group, whether it is kids at a birthday, friends on a night out, or a team ice-breaker.</p>
        <p>Everything stays in your browser and your custom prompts are saved in the page link, so you can reopen your favourite deck any time or share it with the group.</p>
''',
    "related": ["yesno", "birthday", "team"],
  },
  {
    "slug": "team-picker-wheel",
    "name": "Team Picker Wheel",
    "title": "Team Picker Wheel — Random Team Generator | Wheel Bolo",
    "desc": "A free team picker wheel — spin to split players into fair, random teams. Great for sports, PE class, gaming and group projects. Add names and deal them out. No sign-up.",
    "eyebrow": "👥 Pick fair teams",
    "h1": "Team Picker Wheel",
    "lead": "Split the group into fair teams the fun way — spin to deal each player out, no captains needed.",
    "mode": "elim",
    "entries": ["Alex", "Sam", "Jordan", "Riya", "Noah", "Priya", "Liam", "Aanya", "Ethan", "Zara"],
    "article": '''
        <h2>Fair teams in seconds</h2>
        <p>Letting two captains pick teams always leaves someone chosen last. The Team Picker Wheel makes it fair and fast: add everyone's name and spin to deal players out one at a time. With <em>Elimination</em> mode on, each name is removed once it is picked, so you move cleanly through the whole group with no repeats.</p>
        <h3>How to use it</h3>
        <ul>
          <li><strong>Two teams:</strong> spin and send players alternately to Team A and Team B.</li>
          <li><strong>Pick captains first:</strong> spin twice for captains, then deal out the rest.</li>
          <li><strong>Random order:</strong> use it to set a batting order, turn order, or presentation order.</li>
        </ul>
        <h3>Great for any group</h3>
        <p>PE teachers use it for fair sports teams, gamers use it for squads and lobbies, and managers use it for breakout groups and project teams. Type one name per line or paste your roster, and the wheel is ready. Because your list is saved in the page link, you can reuse the same group next week or share it with a co-organiser.</p>
        <p>It is free, private, and runs entirely in your browser — reset any time to draw fresh teams.</p>
''',
    "related": ["giveaway", "classroom", "ipl"],
  },
  {
    "slug": "prize-wheel",
    "name": "Prize Wheel",
    "title": "Prize Wheel Spinner — Free Online Lucky Draw Prize Picker | Wheel Bolo",
    "desc": "Free online prize wheel spinner. Add your prizes, spin the wheel, announce the winner. Perfect for giveaways, school fairs, office events and social media contests.",
    "app_category": "GameApplication",
    "eyebrow": "🎟️ Spin to win",
    "h1": "Prize Wheel",
    "lead": "Load your prizes, give it a spin, and watch the wheel land on a winner with confetti.",
    "mode": "random",
    "entries": ["iPhone", "Amazon Gift Card", "Hamper", "Discount Voucher", "Free Product",
                "₹500 Cash", "Mystery Prize", "Try Again"],
    "article": '''
        <h2>How to set up your prize wheel</h2>
        <p>Nothing pulls a crowd like a spinning prize wheel, and this one takes seconds to set up. The wheel arrives loaded with sample prizes — an iPhone, an Amazon gift card, a hamper, a mystery prize and a cheeky "Try Again" — so you can see exactly how it works. Replace them with your own rewards by typing one prize per line, or paste a list you already have. Keep <em>Random pick</em> mode so a prize can be won more than once, or switch to <em>Elimination</em> when each prize is one-of-a-kind and should be removed after it is won. Spin, and the winner appears with a burst of confetti.</p>
        <h2>Best uses for an online prize wheel</h2>
        <ul>
          <li><strong>Giveaways:</strong> spin live on Instagram or YouTube so your audience sees the winning prize chosen fairly.</li>
          <li><strong>School prize distribution:</strong> run a fun, transparent draw at the annual day or a class party.</li>
          <li><strong>Social media contests:</strong> reward comments and shares by spinning for the prize each winner gets.</li>
          <li><strong>Event raffles:</strong> replace paper raffle tickets at a fair, mela or trade-show stall.</li>
          <li><strong>Office reward programs:</strong> spin for spot bonuses, vouchers or perks at team meetings.</li>
        </ul>
        <h2>Tips to make your prize draw exciting</h2>
        <p>Build suspense by spinning from the smallest prize up to the grand prize. Add a "Try Again" or "Bonus Spin" slice so not every spin wins — it makes the wins feel bigger. Show the wheel on a big screen or projector so everyone can watch, and read the prize out loud before revealing the winner. Because your prize list is saved right in the page link, you can bookmark your wheel, reopen the exact same one at your next event, or share it with your team so everyone has the same prizes ready. It is free, needs no sign-up, and works on any screen — from a phone at a stall to a large display.</p>
''',
    "faq": [
      ("Is the prize wheel free to use?",
       "Yes, the prize wheel is completely free with no sign-up or download. Add your prizes and spin as many times as your event needs."),
      ("Can I add my own prizes?",
       "Absolutely. Replace the sample prizes by typing one prize per line, or paste your own list. The wheel automatically resizes each segment to fit."),
      ("How do I make sure each prize is only won once?",
       "Switch to Elimination mode. Each prize the wheel lands on is removed after the spin, so every prize is awarded exactly once — ideal for one-of-a-kind rewards."),
      ("Can I use the prize wheel for an Instagram or YouTube giveaway?",
       "Yes. Spin it live on screen during your stream or story so your audience can watch the prize being chosen fairly, then tap Share result to post the outcome."),
    ],
    "related": ["office","diwali","kitty"],
  },
  {
    "slug": "giveaway-wheel",
    "name": "Giveaway Wheel",
    "title": "Giveaway Wheel — Free Random Winner Picker | Wheel Bolo",
    "desc": "A free giveaway wheel — paste your entrants and spin to pick a random winner, live and fair. Great for Instagram, YouTube and event giveaways. Removes each winner drawn.",
    "eyebrow": "🎉 Pick a winner",
    "h1": "Giveaway Wheel",
    "lead": "Run a fair giveaway live — paste your entrants, spin, and reveal a random winner everyone can trust.",
    "mode": "elim",
    "entries": ["@aisha", "@rohan", "@meera", "@dev", "@sara", "@kabir", "@nisha", "@arjun"],
    "article": '''
        <h2>Run a giveaway people trust</h2>
        <p>Picking a giveaway winner by hand always invites doubt. The Giveaway Wheel makes the draw transparent: paste your entrants, spin on camera, and let everyone watch the wheel land on a random winner. It is the fair, fuss-free way to run a contest on Instagram, YouTube, a livestream, or at an event.</p>
        <h3>How to run your draw</h3>
        <ul>
          <li>Copy your entrant list — names, usernames, comments, or ticket numbers — and paste it in, one per line.</li>
          <li>Spin live so your audience sees the result in real time.</li>
          <li>Need several winners? <em>Elimination</em> mode removes each winner as they are drawn, so nobody wins twice.</li>
          <li>Tap Share result to post the winner card, or Copy link to share the exact wheel.</li>
        </ul>
        <h3>Fair by design</h3>
        <p>Every spin uses your browser's secure random generator, so each entrant has an equal chance and there is no way to rig the outcome — which is exactly what makes a public giveaway credible. Nothing is stored on a server; your entrant list lives only in your browser and the link you choose to share.</p>
        <p>Completely free, no account, and ready in seconds.</p>
''',
    "related": ["prize", "team", "santa"],
  },
  {
    "slug": "classroom-reward-wheel",
    "name": "Classroom Reward Wheel",
    "title": "Classroom Reward Wheel — Student Rewards Spinner | Wheel Bolo",
    "desc": "A free classroom reward wheel for teachers — spin to give students fun rewards like free time, stickers or a homework pass. Customisable, no sign-up, works on the board.",
    "eyebrow": "⭐ For teachers",
    "h1": "Classroom Reward Wheel",
    "lead": "Reward great work the fun way — spin the wheel and let students win a classroom treat.",
    "mode": "random",
    "entries": ["5 min free time", "Sticker", "Homework pass", "Line leader", "Choose the game",
                "Teacher's helper", "Extra recess", "Class DJ", "Sit anywhere", "Show & tell"],
    "article": '''
        <h2>Turn rewards into a moment</h2>
        <p>A reward feels twice as exciting when it comes from a spinning wheel. The Classroom Reward Wheel gives teachers a fun, fair way to celebrate good behaviour, effort, and achievement — project it on the board, let a student spin, and reveal their prize with confetti.</p>
        <h3>Why teachers love it</h3>
        <ul>
          <li><strong>Positive reinforcement:</strong> reward effort and kindness, not just right answers.</li>
          <li><strong>No favouritism:</strong> the wheel is random, so every reward feels fair.</li>
          <li><strong>Low-cost incentives:</strong> most rewards are privileges, not prizes you have to buy.</li>
          <li><strong>Whole-class fun:</strong> the spin becomes a shared celebration.</li>
        </ul>
        <h3>Build your reward list</h3>
        <p>The wheel comes pre-loaded with classroom-friendly rewards like free time, a homework pass, line leader, and "choose the class game". Swap in the perks that work for your room — type one per line, or paste your own list. Keep <em>Random pick</em> so rewards can repeat, and reuse the same wheel every day, since your setup is saved right in the page link.</p>
        <p>It is free, needs no login, and works on any classroom device or smartboard.</p>
''',
    "related": ["classroom", "birthday", "team"],
  },
  {
    "slug": "antakshari-team-picker",
    "name": "Antakshari Team Picker",
    "title": "Antakshari Team Picker — Spin the Wheel to Make Teams | Wheel Bolo",
    "desc": "Make Antakshari teams fairly with a spin of the wheel. Free online Antakshari team picker — add player names, spin, divide into teams. Works on mobile, share on WhatsApp.",
    "app_category": "GameApplication",
    "eyebrow": "🎵 Game night",
    "h1": "Antakshari Team Picker",
    "lead": "Divide players into fair Antakshari teams the fun way — add names, spin, and let the wheel settle the sides.",
    "mode": "elim",
    "entries": ["Team 1", "Team 2", "Team 3", "Team 4"],
    "article": '''
        <h2>How to divide Antakshari teams with the wheel</h2>
        <ol>
          <li><strong>Add all player names to the wheel</strong> — type one name per line, replacing the sample teams.</li>
          <li><strong>Spin.</strong> Whoever the wheel lands on is assigned to Team 1 (note their name down).</li>
          <li><strong>Switch to Elimination mode</strong> and keep spinning to assign the rest — each player is removed once picked, so you deal everyone out alternately into Team 1 and Team 2.</li>
          <li><strong>Share the final teams on WhatsApp</strong> so everyone can see who is singing with whom.</li>
        </ol>
        <h2>Why Antakshari teams need to be random</h2>
        <p>Everyone knows the one cousin who remembers a thousand songs. When teams are picked by hand, the argument always starts before the singing does — one side ends up with all the strong singers and the game feels rigged before the first "aa" is sung. A random wheel takes the captaincy politics out of it entirely. Nobody can stack a team, nobody is picked last, and the sides come out balanced by pure chance. It keeps the mood light and the focus where it belongs: on the antakshari itself.</p>
        <h2>Antakshari team picker for these occasions</h2>
        <p>Antakshari is the classic Indian ice-breaker, and this wheel fits every setting. At <strong>family gatherings</strong> and festival get-togethers, it splits the young and old into fair mixed teams in seconds. At <strong>kitty parties</strong>, it decides sides without anyone feeling left out. During <strong>college fests</strong> and <strong>dorm nights</strong>, it settles large, noisy groups quickly so the round can start. On a <strong>road trip</strong>, one person's phone becomes the referee for a car-full of singers. And at an <strong>office party</strong> or team outing, it mixes departments into teams that would never have grouped themselves — exactly the kind of fun, fair split that gets everyone singing together.</p>
''',
    "faq": [
      ("What is this Antakshari team picker?",
       "It is a free online spin wheel that divides players into fair Antakshari teams. Add everyone's names, spin, and the wheel assigns players to teams at random — no captains, no arguments."),
      ("Can I make more than 2 teams?",
       "Yes. You can assign players into as many teams as you like — just keep spinning in Elimination mode and place each picked player into the next team in rotation (Team 1, Team 2, Team 3, and so on)."),
      ("How do I make equal teams?",
       "Turn on Elimination mode and deal players out alternately — first pick to Team 1, next to Team 2, and repeat. Because each name is removed after it is picked, the teams end up equal in size."),
      ("Can I share teams on WhatsApp?",
       "Yes. Once you have assigned everyone, tap Share result to send a card to your group, or Copy link to share the exact wheel so others can see it was fair."),
      ("Does it work for other team games like Dumb Charades?",
       "Absolutely. The same wheel works for Dumb Charades, Housie teams, quiz sides, or any party game where you need to split people into fair groups."),
    ],
    "related": ["kitty","gully","holi"],
  },
  {
    "slug": "kitty-party-wheel",
    "name": "Kitty Party Wheel",
    "title": "Kitty Party Game Wheel — Fun Online Games for Kitty Party | Wheel Bolo",
    "desc": "Make your kitty party more fun with the spin wheel. Randomly pick games, decide the host order, run lucky draws and play kitty party activities — free, mobile-friendly.",
    "app_category": "GameApplication",
    "eyebrow": "🪅 Kitty party fun",
    "h1": "Kitty Party Spin Wheel",
    "lead": "Pick the next game, decide the host, or draw a lucky winner — one spin keeps your kitty party moving.",
    "mode": "random",
    "entries": ["Tambola", "Antakshari", "Dumb Charades", "Housie", "Dance Performance",
                "Mehendi Competition", "Cooking Challenge", "Fashion Show", "Quiz", "Kitty Game"],
    "article": '''
        <h2>How to use the kitty party wheel</h2>
        <p>The wheel comes pre-loaded with the most popular kitty party games, so you can start in seconds. Spin to pick the next activity, or edit the list — type one game, name or prize per line — to build a wheel for your own group. Keep <em>Random pick</em> to let a game come up more than once, or switch to <em>Elimination</em> when you want each game or each hostess picked only once. Every spin ends with a confetti reveal, and you can Share result or Copy link to send the outcome to your kitty WhatsApp group.</p>
        <h2>Kitty party games you can run with the spin wheel</h2>
        <ul>
          <li><strong>Decide which game to play:</strong> spin the loaded list of Tambola, Antakshari, Dumb Charades, Housie and more instead of debating it.</li>
          <li><strong>Pick the host order for next month:</strong> add every member's name and spin to fairly decide who hosts the next kitty.</li>
          <li><strong>Run a lucky draw for the kitty prize:</strong> add all names and spin in Elimination mode to draw the pot winner transparently.</li>
          <li><strong>Assign teams for competitions:</strong> split members into sides for the dance, cooking or fashion round.</li>
        </ul>
        <h2>Kitty party lucky draw ideas</h2>
        <p>A spin wheel makes every prize moment feel special. Run a <strong>gift hamper lucky draw</strong> where each member's name goes on the wheel and one lucky winner takes home the hamper. Use it to <strong>pick the jewellery or best-dressed contest winner</strong> when the votes are close and you want a neutral tie-breaker. Spin to choose the <strong>best-dressed winner</strong> from a shortlist, or to fairly <strong>decide who brings what</strong> — snacks, sweets, the return gifts — for the next party. Because nothing is stored and every spin is genuinely random, no one can accuse the hostess of playing favourites.</p>
''',
    "faq": [
      ("Is the kitty party wheel free?",
       "Yes, it is completely free with no sign-up or app to download. Open it on your phone and start spinning at your next kitty party."),
      ("Can I add my own games or member names?",
       "Yes. Replace the pre-loaded games by typing one game, name or prize per line, or paste a list. The wheel resizes each segment automatically."),
      ("How do I run a fair kitty lucky draw?",
       "Add every member's name and switch to Elimination mode. Each spin removes the name it lands on, so you can draw one or more winners without anyone being picked twice."),
      ("Can I decide who hosts the next kitty with it?",
       "Yes. Add all the members' names and spin — whoever the wheel lands on hosts next month. It is a fair, neutral way to settle the host rotation."),
      ("Can I share the result with my kitty group?",
       "Yes. Tap Share result to send a winner card to your WhatsApp group, or Copy link to share the exact wheel so everyone can see it was fair."),
    ],
    "related": ["antakshari","diwali","prize"],
  },
  {
    "slug": "office-lucky-draw-wheel",
    "name": "Office Lucky Draw",
    "title": "Office Lucky Draw Wheel — Free Online Tambola & Prize Draw for Office | Wheel Bolo",
    "desc": "Run a fair office lucky draw with a spin of the wheel. Free online tool for office parties, Diwali gifting, tambola, team rewards and farewell gifts. No app download needed.",
    "app_category": "GameApplication",
    "eyebrow": "🏢 For the workplace",
    "h1": "Office Lucky Draw Wheel",
    "lead": "Run a transparent office lucky draw on the big screen — add names, spin, and reveal the winner for all to see.",
    "mode": "random",
    "entries": ["Employee 1", "Employee 2", "Employee 3"],
    "article": '''
        <h2>How to run an office lucky draw online</h2>
        <ol>
          <li><strong>Add all eligible employee names</strong> — type one name per line, or paste the list from your team roster.</li>
          <li><strong>Spin the wheel live</strong> on a shared screen or projector so the whole office can watch it land.</li>
          <li><strong>Announce the winner</strong> and tap Share result to post the winner card to the company WhatsApp or Teams group.</li>
        </ol>
        <h2>Office occasions that need a lucky draw</h2>
        <ul>
          <li><strong>Diwali office party prize:</strong> draw for hampers and gift vouchers so the festive prizes are handed out fairly in front of everyone.</li>
          <li><strong>Employee of the Month (fun category):</strong> spin for light-hearted awards like "best chai break" or "most helpful desk neighbour".</li>
          <li><strong>Farewell gift draw:</strong> decide who gives the farewell speech or which team member picks the going-away gift.</li>
          <li><strong>Team outing activity:</strong> pick who plans the next outing, or draw for the window seat on the bus.</li>
          <li><strong>Anniversary celebration:</strong> run a work-anniversary raffle where long-serving employees go into a prize draw.</li>
          <li><strong>Secret Santa gift assignment:</strong> spin to assign who gives to whom without paper chits or peeking.</li>
          <li><strong>Work-from-home survival kit giveaway:</strong> draw remote employees for a care package or gadget.</li>
          <li><strong>Quarterly reward draw:</strong> put everyone who hit their targets into a fair spin for a bonus prize.</li>
        </ul>
        <h2>Tips for a transparent office lucky draw</h2>
        <p>Show the full list of names on the screen to everyone before spinning, so people can confirm they are included. Use Elimination mode when there are multiple prizes, so each winner is removed and nobody wins twice. Screenshot the final result as a record for HR, and share the wheel link so anyone who missed the event can reopen the exact same draw and verify it was fair. Because the pick uses your browser's secure random generator, there is no way to rig it — which is exactly what makes an office draw feel trustworthy.</p>
''',
    "faq": [
      ("Can I use this for a tambola number pick?",
       "Yes. Add the numbers or tickets you want to draw from, one per line, and spin. In Elimination mode each number is removed after it is called, just like a tambola draw."),
      ("How do I run a multi-prize lucky draw?",
       "Turn on Elimination mode. Each name the wheel lands on is removed after the spin, so you can draw a different winner for every prize without anyone being picked twice."),
      ("Can I project this on a TV or screen in the office?",
       "Yes. Open the wheel in any browser and share your screen or connect to a projector. The wheel and confetti scale up cleanly for a big display."),
      ("Is it truly random?",
       "Yes. Every spin uses your browser's secure random number generator, so each name has an exactly equal chance. Showing the list before you spin makes the fairness visible to everyone."),
      ("Can I add emojis or prize names to the wheel?",
       "Yes. You can type prize names, emojis or employee names — anything you like, one per line. The wheel adjusts each segment to fit."),
    ],
    "related": ["diwali","prize","santa"],
  },
  {
    "slug": "holi-team-picker",
    "name": "Holi Team Picker",
    "title": "Holi Team Picker Wheel — Spin to Make Holi Colour Teams | Wheel Bolo",
    "desc": "Make Holi colour teams with a spin of the wheel. Free Holi team picker for housing societies, schools and office Holi events. Pick teams by colour — red, blue, green, yellow.",
    "app_category": "GameApplication",
    "eyebrow": "🌈 Happy Holi",
    "h1": "Holi Team Picker",
    "lead": "Split the crowd into colour teams the fun way — spin to sort everyone into red, blue, green and more.",
    "mode": "random",
    "entries": ["Red Team", "Blue Team", "Green Team", "Yellow Team", "Pink Team", "Orange Team"],
    "article": '''
        <h2>How to make Holi teams with the spin wheel</h2>
        <p>The wheel comes loaded with six colour teams, so you are ready to play in seconds. To sort players, have each person spin once — the colour it lands on is their team. Or add every player's name to the wheel, switch to <em>Elimination</em> mode, and deal names out into each colour team in turn so the sides come out equal. Either way, the split is random and nobody can complain that the teams were stacked. Spin, get your colour, and grab your gulaal.</p>
        <h2>Holi game ideas that need team picking</h2>
        <ul>
          <li><strong>Rang panchami colour battle:</strong> two or more colour teams face off to cover the other side in their shade.</li>
          <li><strong>Water gun (pichkari) teams:</strong> divide the kids into squads for a friendly water fight.</li>
          <li><strong>Holi trivia quiz teams:</strong> sort guests into sides for a festival quiz between the snacks and thandai.</li>
          <li><strong>Tug of war at the society Holi:</strong> spin to build two even teams for the classic rope pull.</li>
          <li><strong>Colour powder relay race:</strong> assign relay teams and race to carry the gulaal to the finish.</li>
        </ul>
        <h2>Running a Holi lucky draw</h2>
        <p>Housing societies often pair the Holi celebration with a prize draw for the best-dressed, the best rangoli, or a simple raffle. Add every resident's name to the wheel and spin to pick winners fairly in front of the whole society — no folded chits, no doubts. For a full festive prize draw with multiple gifts, the <a href="/diwali-lucky-draw-wheel/">Diwali Lucky Draw Wheel</a> works exactly the same way and is handy any time of year.</p>
''',
    "faq": [
      ("Is the Holi team picker free?",
       "Yes, it is completely free with no sign-up or download. Open it on any phone and start making colour teams straight away."),
      ("Can I change the colour team names?",
       "Yes. Edit the list to add, remove or rename teams — type one team per line. You can also add player names instead of colours if you prefer."),
      ("How do I make equal Holi teams?",
       "Add all the players' names, switch to Elimination mode, and deal them out into each colour team in rotation. Because each name is removed after it is picked, the teams end up equal."),
      ("Can I use it for a housing society Holi event?",
       "Yes. It is ideal for societies and schools — spin on a phone or a big screen so every resident or student can see the teams and any lucky-draw winners are chosen fairly."),
    ],
    "related": ["gully","antakshari","kitty"],
  },
  {
    "slug": "gully-cricket-team-picker",
    "name": "Gully Cricket Team Picker",
    "title": "Gully Cricket Team Picker — Spin the Wheel to Pick Cricket Teams | Wheel Bolo",
    "desc": "Pick gully cricket teams fairly with a spin of the wheel. Free random cricket team selector — add player names, spin to assign teams. Perfect for mohalla cricket, box cricket and tape ball matches.",
    "app_category": "GameApplication",
    "eyebrow": "🏏 Mohalla cricket",
    "h1": "Gully Cricket Team Picker",
    "lead": "Split the players into fair sides before the first over — spin the wheel and let it pick the teams.",
    "mode": "elim",
    "entries": ["Team India", "Team Pakistan", "Team Australia", "Team England",
                "Team South Africa", "Team Sri Lanka", "Team New Zealand",
                "Team West Indies", "Team Bangladesh", "Team Afghanistan"],
    "article": '''
        <h2>How to pick gully cricket teams with the wheel</h2>
        <p><strong>Method A — Country assignment:</strong> keep the pre-loaded country names on the wheel. Each person spins once, and the country it lands on is the side they play as. In Elimination mode each country is removed as it is taken, so no two players get the same one.</p>
        <p><strong>Method B — Player split:</strong> clear the list and add all the players' names instead. Spin in Elimination mode and alternate the picks between Team A and Team B until everyone is assigned. Because each name is removed after it is picked, the two teams come out even and nobody is left standing awkwardly at the end.</p>
        <h2>Types of cricket where this helps</h2>
        <ul>
          <li><strong>Mohalla cricket:</strong> settle the neighbourhood match sides in seconds so the game starts before it gets dark.</li>
          <li><strong>Box cricket tournaments:</strong> assign players to franchises or split a large group into balanced box-cricket squads.</li>
          <li><strong>Tape ball cricket:</strong> pick fair teams for the fast, high-scoring tape ball format everyone loves.</li>
          <li><strong>Terrace cricket:</strong> divide the cousins and kids into two sides for a Sunday terrace game.</li>
          <li><strong>Corporate cricket days:</strong> mix departments into random teams so it is not just one team against another.</li>
          <li><strong>College cricket festivals:</strong> draw sides quickly when many players turn up and captains cannot agree.</li>
        </ul>
        <h2>Toss the coin vs spin the wheel</h2>
        <p>A coin toss only answers one question — who bats first. It cannot split eight or ten players into two fair teams. Picking sides by hand with two captains always leaves someone chosen last and someone grumbling that the teams are lopsided. Spinning a wheel with everyone's names on it is more fun and more transparent: every player watches their own spin, the split is genuinely random, and there is no captain bias to argue about. When a big group needs to be divided fairly and fast, the wheel beats the coin every time.</p>
''',
    "faq": [
      ("How do I split 12 players into 2 equal teams?",
       "Add all 12 names to the wheel and turn on Elimination mode. Spin and send picks alternately to Team A and Team B. Each name is removed after it is picked, so you end up with two teams of six."),
      ("Can I add substitute players to the wheel?",
       "Yes. Add substitutes as extra names, or keep a separate spin for them. You can edit the list any time — just type one name per line."),
      ("Can I use this for box cricket team assignment?",
       "Yes. It works for box cricket, tape ball, terrace and mohalla cricket alike. Add the players or franchise names and spin to assign teams fairly."),
      ("How do I pick batting and fielding order with this?",
       "Add the players' names and spin in Elimination mode. The order in which names come out becomes your batting or bowling order, with no repeats."),
      ("Can I save the teams and share on WhatsApp?",
       "Yes. Tap Share result to send a card to your group, or Copy link to share the exact wheel so everyone can see how the teams were picked."),
    ],
    "related": ["ipl","antakshari","holi"],
  },
  {
    "slug": "study-topic-picker",
    "name": "Study Topic Picker",
    "title": "Study Topic Picker Wheel — Spin to Decide What to Study | Wheel Bolo",
    "desc": "Can't decide what subject to study today? Spin the wheel to pick your study topic. Free random study planner for JEE, NEET, board exams and college students. Works on mobile.",
    "app_category": "EducationApplication",
    "eyebrow": "📚 Study smarter",
    "h1": "Study Topic Picker Wheel",
    "lead": "Stop debating what to study and just spin. The wheel picks your next subject so you can start now.",
    "mode": "random",
    "entries": ["Physics", "Chemistry", "Maths", "Biology", "English", "History",
                "Geography", "Economics", "Revision", "Break Time 😄"],
    "article": '''
        <h2>How to use the study topic picker</h2>
        <p>Add your subjects or chapters to the wheel — type one per line, replacing the samples — and spin to decide what to study first. The wheel removes all the "which subject should I do now?" indecision: you study what it lands on, not just what you feel like. Keep <em>Random pick</em> to let any subject come up, or switch to <em>Elimination</em> mode to go through every subject in a random order without repeating, so nothing gets skipped. There is no bias and no favourite-subject procrastination — the wheel decides, and you get to work.</p>
        <h2>Who uses the study topic picker</h2>
        <ul>
          <li><strong>JEE and NEET aspirants</strong> who have to cover Physics, Chemistry, Maths or Biology every single day and need a fair way to rotate them.</li>
          <li><strong>Class 10 and 12 students</strong> preparing for board exams across many subjects at once.</li>
          <li><strong>College students</strong> juggling multiple papers, assignments and revision.</li>
          <li><strong>Students who procrastinate</strong> by debating what to study — the spin makes the choice for them in one second.</li>
        </ul>
        <h2>Study planning tips with the spin wheel</h2>
        <p>Gamify your timetable by spinning for <strong>45-minute Pomodoro subject blocks</strong> — study whatever comes up, take a short break, then spin again. Use the wheel to pick <strong>which past-year paper</strong> to solve when you cannot decide. Add <strong>Revision</strong>, <strong>Break</strong> and small <strong>rewards</strong> to the wheel too, so rest is built into the plan and not just an afterthought. And when you want guaranteed full coverage before an exam, use <strong>Elimination mode</strong> so every subject is picked exactly once before any repeats — a simple way to make sure no topic is left behind.</p>
''',
    "faq": [
      ("Is this really helpful for exam preparation?",
       "Yes. Rotating subjects at random keeps your study balanced and stops you from over-studying favourites while ignoring weaker areas. It also removes the decision fatigue of choosing what to study, so you start sooner."),
      ("Can I add chapters instead of full subjects?",
       "Absolutely. Type individual chapters or topics — one per line — instead of whole subjects, and spin to pick exactly what to study next."),
      ("How do I make sure I cover all topics?",
       "Use Elimination mode. Each topic the wheel lands on is removed after it is picked, so you cycle through every subject or chapter once before any of them repeat."),
      ("Can I add a \"Take a Break\" slice to the wheel?",
       "Yes. Add Break, Revision or reward slices to the wheel so rest is part of the plan. Landing on a break is a fair, earned pause between study blocks."),
      ("Is this useful for UPSC preparation?",
       "Yes. UPSC aspirants juggle many subjects — History, Geography, Polity, Economics, current affairs and optionals. Add them all and spin to rotate your daily coverage without bias."),
    ],
    "related": ["classroom","dinner"],
  },
  {
    "slug": "ipl-player-picker-wheel",
    "name": "IPL Player Picker",
    "title": "IPL Player Picker Wheel — Random IPL Player Selector | Wheel Bolo",
    "desc": "Spin the wheel to pick a random IPL player. Top batters, bowlers and all-rounders from IPL 2026 loaded. Free, instant, no sign-up — great for fantasy cricket.",
    "app_category": "GameApplication",
    "eyebrow": "🏏 Cricket season",
    "h1": "IPL Player Picker Wheel",
    "lead": "Can't decide which IPL star to back today? Spin the wheel and let it pick your player.",
    "mode": "random",
    "entries": ["Rohit Sharma","Virat Kohli","Jasprit Bumrah","KL Rahul","Suryakumar Yadav",
                "Hardik Pandya","Rishabh Pant","Ravindra Jadeja","Shubman Gill","Mohammed Shami",
                "Yuzvendra Chahal","Jos Buttler"],
    "article": '''
        <h2>How to use the IPL player picker</h2>
        <ol>
          <li><strong>Open the page.</strong> Twelve marquee IPL players are already on the wheel — no setup needed.</li>
          <li><strong>Spin.</strong> The wheel lands on a random player — that is your pick for the fantasy slot, the debate, or the trivia round.</li>
          <li><strong>Edit the list</strong> to add your own squad, then Copy link to share the exact wheel with friends.</li>
        </ol>
        <h2>Best uses for a random IPL player selector</h2>
        <ul>
          <li><strong>Fantasy cricket team building:</strong> spin to fill a slot when two players are too close to call.</li>
          <li><strong>Who to captain today:</strong> let the wheel choose your captain or vice-captain pick.</li>
          <li><strong>Settle debates:</strong> "best batter in the league?" — put the names on and let chance referee.</li>
          <li><strong>IPL trivia games:</strong> spin to pick which player a question is about.</li>
        </ul>
        <h2>About the players on the wheel</h2>
        <p>The wheel is pre-loaded with twelve of the biggest names across the IPL 2026 season — a mix of explosive top-order batters, death-over specialists, wily spinners and match-winning all-rounders. It is only a starting point: clear the list and add your own team's full squad, a shortlist of uncapped youngsters, or the players in your fantasy draft pool. The wheel resizes each segment automatically however many names you add.</p>
        <h2>More cricket tools on Wheel Bolo</h2>
        <p>Need a team instead of a player? Use the <a href="/ipl-team-picker-wheel/">IPL Team Picker</a> to assign one of all ten franchises, or the <a href="/gully-cricket-team-picker/">Gully Cricket Team Picker</a> to split your mohalla match into fair sides.</p>
''',
    "faq": [
      ("Which players are on the IPL player wheel?",
       "It comes loaded with twelve marquee IPL 2026 players across batting, bowling and all-rounder roles. You can edit the list freely to add any players or your full fantasy pool."),
      ("Can I add my own players?",
       "Yes. Clear the list and type your own player names, one per line, or paste a squad. The wheel adjusts each segment automatically."),
      ("Is this good for fantasy cricket?",
       "Yes. Fantasy players use it to break ties between similar picks, choose a captain, or randomise selections across a draft pool."),
    ],
    "related": ["ipl","gully","cricket"],
  },
  {
    "slug": "ipl-auction-wheel",
    "name": "IPL Auction Wheel",
    "title": "IPL Auction Wheel — Spin for IPL Player Auction Fun | Wheel Bolo",
    "desc": "Run a mock IPL auction with the spin wheel. Spin to decide which player category to bid on next. Free online IPL auction game for friends and fantasy leagues.",
    "app_category": "GameApplication",
    "eyebrow": "🏏 Cricket season",
    "h1": "IPL Auction Spin Wheel",
    "lead": "Host your own mini IPL auction — spin to decide the next player category up for bidding.",
    "mode": "random",
    "entries": ["Top-Order Batter","Fast Bowler","Spinner","All-Rounder","Wicketkeeper",
                "Overseas Player","Uncapped Talent","Finisher","Opening Pacer","Death Bowler"],
    "article": '''
        <h2>How to play the IPL auction wheel game</h2>
        <p>Turn a get-together into your own mini-IPL auction. Give each player (or team) an equal purse of pretend crores. Take turns spinning the wheel — the category it lands on is the type of player up for auction in that round. Everyone bids from their purse, and the highest bidder wins a player of that category for their squad. Keep going until purses run dry or every squad is full, then compare the teams you have built.</p>
        <h2>Use it for fantasy cricket draft order</h2>
        <p>Running a fantasy league draft? Spin the wheel to decide which position each manager must draft next, so nobody stacks all the batters early. It keeps the draft balanced and adds a bit of suspense to every pick.</p>
        <h2>IPL 2026 auction categories explained</h2>
        <ul>
          <li><strong>Top-Order Batter &amp; Finisher:</strong> the run-scorers who set up or close out an innings.</li>
          <li><strong>Fast Bowler, Opening Pacer &amp; Death Bowler:</strong> pace for the new ball and the final overs.</li>
          <li><strong>Spinner &amp; All-Rounder:</strong> the middle-overs controllers and the two-in-one match winners.</li>
          <li><strong>Wicketkeeper, Overseas Player &amp; Uncapped Talent:</strong> the specialists and wildcards every squad needs.</li>
        </ul>
        <p>Edit the list to match the exact categories or player names in your auction — the wheel is yours to customise.</p>
''',
    "faq": [
      ("How do I run a mock IPL auction with this?",
       "Give each participant an equal budget, take turns spinning for the next player category, and let the highest bidder win a player of that type. Continue until squads are full."),
      ("Can I change the auction categories?",
       "Yes. Edit the list to add real player names, set roles, or price brackets — type one per line and the wheel updates instantly."),
    ],
    "related": ["ipl","iplplayer","prize"],
  },
  {
    "slug": "cricket-team-picker",
    "name": "Cricket Team Picker",
    "title": "Cricket Team Picker Wheel — Random International Cricket Team | Wheel Bolo",
    "desc": "Spin the wheel for a random international cricket team. 12 ICC nations loaded — perfect for World Cup sweepstakes, gully cricket and trivia. Free, no sign-up.",
    "app_category": "GameApplication",
    "eyebrow": "🏏 Cricket",
    "h1": "Cricket Team Picker Wheel",
    "lead": "Which cricket nation will you back? Spin the wheel to draw a team.",
    "mode": "random",
    "entries": ["India","Australia","England","Pakistan","South Africa","New Zealand",
                "West Indies","Sri Lanka","Bangladesh","Afghanistan","Zimbabwe","Ireland"],
    "article": '''
        <h2>How to use the cricket team picker</h2>
        <p>The wheel comes loaded with twelve international cricket nations. Spin once to draw a random team, or have each person in your group spin in turn to get the country they will support or play as. Edit the list any time — remove the minnows, add associate nations, or swap in club sides instead.</p>
        <h2>Perfect for ICC World Cup sweepstakes</h2>
        <p>Running an office or family sweepstake for the T20 World Cup, the ODI World Cup or the Champions Trophy? The cricket team picker draws teams fairly and in full view, so nobody can claim the office favourite was rigged. Spin in Elimination mode to hand every participant a different nation with no repeats.</p>
        <h2>Other cricket uses</h2>
        <ul>
          <li><strong>Gully &amp; backyard cricket:</strong> each side plays as the country the wheel gives them.</li>
          <li><strong>Watch-party games:</strong> back the team you draw for the match and see who ends up on the winning side.</li>
          <li><strong>Cricket trivia:</strong> spin to pick which nation the next question is about.</li>
        </ul>
        <p>For the franchise game, try the <a href="/ipl-team-picker-wheel/">IPL Team Picker</a>; to split real players into sides, use the <a href="/gully-cricket-team-picker/">Gully Cricket Team Picker</a>.</p>
''',
    "faq": [
      ("Which teams are on the cricket wheel?",
       "Twelve international nations are loaded: India, Australia, England, Pakistan, South Africa, New Zealand, West Indies, Sri Lanka, Bangladesh, Afghanistan, Zimbabwe and Ireland. Edit the list to add or remove any."),
      ("How do I run a World Cup sweepstake?",
       "Add every participant's nation options, switch to Elimination mode, and spin once per person so each gets a different team with no repeats."),
    ],
    "related": ["ipl","gully","football"],
  },
  {
    "slug": "football-team-picker",
    "name": "Football Team Picker",
    "title": "Football Team Picker Wheel — Random Football Club Selector | Wheel Bolo",
    "desc": "Spin the wheel for a random football team. Top Premier League, La Liga and Champions League clubs loaded. Free football team randomizer for fantasy drafts and sweepstakes.",
    "app_category": "GameApplication",
    "eyebrow": "⚽ Football",
    "h1": "Football Team Picker Wheel",
    "lead": "Pick a football club at random — spin for fantasy drafts, sweepstakes and match-night fun.",
    "mode": "random",
    "entries": ["Manchester City","Arsenal","Liverpool","Chelsea","Manchester United","Real Madrid",
                "Barcelona","Bayern Munich","PSG","Juventus","Borussia Dortmund","Atletico Madrid"],
    "article": '''
        <h2>How to use the football team picker</h2>
        <p>The wheel is loaded with twelve of Europe's biggest clubs. Spin to draw a random team for a game, a sweepstake, or a friendly bet — or have each person spin in turn to get the club they will manage or support. Edit the list to use just your league, your five-a-side sides, or the ISL clubs from back home.</p>
        <h2>Great for Premier League fantasy drafts</h2>
        <p>Settle your fantasy football draft order with a spin, decide who supports which club for the weekend, or pick who hosts the next match-night. Because every spin is random and visible, there is no arguing about favouritism.</p>
        <h2>World Cup and Champions League uses</h2>
        <ul>
          <li><strong>World Cup sweepstakes:</strong> add the qualifying nations and spin to assign each person a country.</li>
          <li><strong>Champions League group draws:</strong> use it for a fun mock group-stage draw with friends.</li>
          <li><strong>Five-a-side team picks:</strong> add the players and split them into fair sides.</li>
        </ul>
        <p>Prefer cricket? Try the <a href="/cricket-team-picker/">Cricket Team Picker</a> or the <a href="/ipl-team-picker-wheel/">IPL Team Picker</a>. To split a specific group of players into teams, use the <a href="/team-picker-wheel/">Team Picker Wheel</a>.</p>
''',
    "faq": [
      ("Which clubs are on the football wheel?",
       "Twelve top European clubs across the Premier League, La Liga, Bundesliga, Serie A and Ligue 1. You can edit the list to add your own league or local teams."),
      ("Can I use it for a World Cup sweepstake?",
       "Yes. Replace the clubs with the competing nations, switch to Elimination mode, and spin once per person so everyone gets a different country."),
    ],
    "related": ["cricket","ipl","team"],
  },
]

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("wrote", path)

# ----------------------------------------------------------- build template pages
for tpl in TEMPLATES:
    url = f"{SITE}/{tpl['slug']}/"
    cfg = "window.SPIN_CONFIG = " + json.dumps({"entries": tpl["entries"], "mode": tpl["mode"]}, ensure_ascii=False) + ";"
    extra = f'  <script>{cfg}</script>'
    if tpl.get("team_data"):
        td = "window.WB_TEAM_DATA = " + json.dumps(tpl["team_data"], ensure_ascii=False) + ";"
        extra += f'\n  <script>{td}</script>'
    rel_cards = [CARDS[k] for k in tpl["related"]]
    jl = [
        breadcrumb_jsonld(tpl["name"], url),
        webapp_jsonld(tpl["name"] + " — Wheel Bolo", url, tpl.get("app_desc", tpl["desc"]),
                      category=tpl.get("app_category", "UtilitiesApplication"),
                      features=tpl.get("features")),
    ]
    faq = list(tpl.get("faq") or []) + PRODUCT_FAQ
    jl.append(faq_jsonld(faq))
    body_html = tpl["article"] + faq_html(faq)
    page = (
        head(tpl["title"], tpl["desc"], url, og_type="website",
             jsonld=jl, extra_head=extra)
        + HEADER
        + breadcrumbs(tpl["name"])
        + '\n  <main id="main">'
        + app_section(tpl["eyebrow"], tpl["h1"], tpl["lead"])
        + AD_SLOT
        + '\n    <section class="section">\n      <article class="container prose">'
        + body_html
        + '      </article>\n    </section>'
        + related(rel_cards)
        + '\n  </main>'
        + FOOTER
    )
    write(f"{tpl['slug']}/index.html", page)

print("templates done")

# --------------------------------------------------------------- trust pages
def simple_page(slug, name, title, desc, article_html):
    url = f"{SITE}/{slug}/"
    page = (
        head(title, desc, url, jsonld=breadcrumb_jsonld(name, url))
        + HEADER
        + breadcrumbs(name)
        + '\n  <main id="main">\n    <section class="section">\n      <article class="container prose">'
        + article_html
        + '\n      </article>\n    </section>\n  </main>'
        + FOOTER
    )
    write(f"{slug}/index.html", page)

EMAIL = "contact@wheelbolo.com"

simple_page(
    "about", "About",
    "About Wheel Bolo — Free Spin the Wheel Random Picker",
    "About Wheel Bolo, a free, privacy-friendly spin-the-wheel random picker for classrooms, raffles, teams, dinner and everyday decisions. English & Hindi.",
    f'''
        <h1>About Wheel Bolo</h1>
        <p>Wheel Bolo is a free online <strong>spin the wheel</strong> tool — a colourful random name picker and decision wheel built for the way people actually make choices: together, out loud, and with a bit of drama.</p>
        <p>It started with a simple frustration. Picking a student to answer, choosing a Diwali lucky-draw winner, deciding what to cook, or sorting out who bats first always ends in the same place — folded paper chits, "you choose", or someone quietly rigging it. We wanted something instant, obviously fair, and genuinely fun to watch.</p>
        <h2>What makes it different</h2>
        <ul>
          <li><strong>Ready-made templates:</strong> wheels for classrooms, lucky draws, team pickers, dinner and gift exchanges, with a one-tap Hindi (हिंदी) interface alongside English.</li>
          <li><strong>Private by design:</strong> there is no account and no database. Your list lives only in your browser and in the link you choose to share.</li>
          <li><strong>Fair every time:</strong> winners are chosen with your browser's secure random generator, so every option has an equal chance.</li>
          <li><strong>Fast on any phone:</strong> a lightweight site that loads quickly even on a patchy mobile connection.</li>
        </ul>
        <p>Wheel Bolo is free to use and supported by advertising. If you have an idea, a template you'd like us to add, or a bug to report, we'd love to hear from you on our <a href="/contact/">contact page</a>.</p>
''')

simple_page(
    "contact", "Contact",
    "Contact Wheel Bolo",
    "Get in touch with the Wheel Bolo team — questions, feedback, template ideas, or bug reports.",
    f'''
        <h1>Contact us</h1>
        <p>We'd genuinely love to hear from you — whether it's feedback, a new wheel template you'd like us to build, a partnership idea, or a bug you've spotted.</p>
        <p>Email us at <a href="mailto:{EMAIL}">{EMAIL}</a> and we'll get back to you as soon as we can.</p>
        <h2>Before you write</h2>
        <ul>
          <li><strong>Found a bug?</strong> Tell us which page and what device or browser you were using — it helps us fix it faster.</li>
          <li><strong>Want a new template?</strong> Describe the wheel and the options it should come with.</li>
          <li><strong>Privacy questions?</strong> Our <a href="/privacy-policy/">Privacy Policy</a> explains exactly what data is and isn't collected.</li>
        </ul>
        <p>Wheel Bolo is an independent project, free for everyone to use. Thank you for spinning with us!</p>
''')

simple_page(
    "privacy-policy", "Privacy Policy",
    "Privacy Policy — Wheel Bolo",
    "Wheel Bolo's privacy policy: how we use cookies, Google AdSense and third-party advertising, and why your wheel data never leaves your browser.",
    f'''
        <h1>Privacy Policy</h1>
        <p><em>Last updated: 9 July 2026.</em></p>
        <p>Wheel Bolo ("we", "us") respects your privacy. This policy explains what information is and is not collected when you use <a href="/">wheelbolo.com</a>.</p>

        <h2>Your wheel data stays with you</h2>
        <p>The names and options you type into the wheel are processed entirely in your own browser. We do <strong>not</strong> have a server database and we never receive, store, or transmit your lists. The only way your data leaves your device is if <em>you</em> choose to share it — using the Copy link button (which encodes your list into the page URL) or the Share result button (which creates an image on your device).</p>

        <h2>Cookies and local storage</h2>
        <p>To make the tool more convenient, Wheel Bolo saves a small amount of information in your browser's <strong>local storage</strong> — only on your own device. This includes the list of names or options you last entered (so it can be offered back to you if you return to the same wheel), and your preferences: the wheel title you type, your chosen colour palette, background theme, and sound volume. This data is stored <strong>only in your browser</strong>. It is never sent to us or to any server, is not used to identify or track you, and you can clear it at any time from your browser settings. The tool works fully even if local storage is disabled. Separately, the third-party advertising described below may set its own cookies in your browser.</p>

        <h2>Advertising &amp; Google AdSense</h2>
        <p>Wheel Bolo is free and is supported by advertising. We use <strong>Google AdSense</strong> to display ads. Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this and other websites.</p>
        <ul>
          <li>Google's use of advertising cookies enables it and its partners to serve ads to you based on your visits to Wheel Bolo and/or other sites on the Internet.</li>
          <li>You may opt out of personalised advertising by visiting <a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Google Ads Settings</a>.</li>
          <li>You can also opt out of some third-party vendors' use of cookies for personalised advertising at <a href="https://www.aboutads.info/choices/" rel="nofollow noopener" target="_blank">aboutads.info</a>.</li>
          <li>Google uses the advertising cookie (the DART cookie and others) in accordance with <a href="https://policies.google.com/technologies/ads" rel="nofollow noopener" target="_blank">Google's advertising policies</a>.</li>
        </ul>

        <h2>Analytics</h2>
        <p>We may use privacy-respecting, aggregate analytics to understand which wheels are popular. Any such data is anonymised and is never linked to the contents of your wheels.</p>

        <h2>Children's privacy</h2>
        <p>Wheel Bolo is a general-audience tool and does not knowingly collect personal information from children.</p>

        <h2>Changes to this policy</h2>
        <p>We may update this policy from time to time. Material changes will be reflected by the "last updated" date above.</p>

        <h2>Contact</h2>
        <p>Questions about this policy? Email us at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
''')

print("trust pages done")

# ------------------------------------------------------------ 404 page
not_found = (
    head("Page not found — Wheel Bolo", "The page you were looking for doesn't exist. Spin back to the Wheel Bolo home page.",
         SITE + "/404.html")
    + HEADER
    + '''
  <main id="main">
    <section class="section">
      <article class="container prose text-center">
        <h1>404 — this slice doesn't exist</h1>
        <p>The wheel spun off the page! The link may be broken or the page may have moved.</p>
        <p class="tag-row">
          <a class="btn btn-primary" href="/">Back to the wheel</a>
          <a class="btn btn-secondary" href="/#templates">Browse templates</a>
        </p>
      </article>
    </section>
  </main>'''
    + FOOTER
)
write("404.html", not_found)

# ------------------------------------------------------------ technical files
PAGES = ["/", "/classroom-name-picker/", "/diwali-lucky-draw-wheel/", "/ipl-team-picker-wheel/",
         "/dinner-decider-wheel/", "/secret-santa-picker/", "/birthday-wheel-generator/",
         "/yes-no-wheel/", "/truth-or-dare-wheel/", "/team-picker-wheel/", "/prize-wheel/",
         "/giveaway-wheel/", "/classroom-reward-wheel/",
         "/antakshari-team-picker/", "/kitty-party-wheel/", "/office-lucky-draw-wheel/",
         "/holi-team-picker/", "/gully-cricket-team-picker/", "/study-topic-picker/",
         "/ipl-player-picker-wheel/", "/ipl-auction-wheel/", "/cricket-team-picker/",
         "/football-team-picker/",
         "/about/", "/contact/", "/privacy-policy/"]
PRIORITY = {
    "/": "1.0",
    "/ipl-team-picker-wheel/": "0.9",
    "/classroom-name-picker/": "0.9",
    "/ipl-player-picker-wheel/": "0.8",
    "/ipl-auction-wheel/": "0.8",
    "/cricket-team-picker/": "0.8",
    "/football-team-picker/": "0.8",
    "/gully-cricket-team-picker/": "0.8",
    "/antakshari-team-picker/": "0.8",
    "/office-lucky-draw-wheel/": "0.8",
    "/kitty-party-wheel/": "0.8",
    "/holi-team-picker/": "0.8",
    "/study-topic-picker/": "0.7",
    "/diwali-lucky-draw-wheel/": "0.7",
    "/dinner-decider-wheel/": "0.7",
    "/secret-santa-picker/": "0.6",
    "/prize-wheel/": "0.7",
    "/about/": "0.3",
    "/contact/": "0.3",
    "/privacy-policy/": "0.2",
}
CHANGEFREQ = {
    "/": "weekly",
    "/diwali-lucky-draw-wheel/": "yearly",
    "/secret-santa-picker/": "yearly",
    "/about/": "yearly",
    "/contact/": "yearly",
    "/privacy-policy/": "yearly",
}
today = datetime.date.today().isoformat()
urls = "\n".join(
    f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{today}</lastmod>\n"
    f"    <changefreq>{CHANGEFREQ.get(p, 'monthly')}</changefreq>\n"
    f"    <priority>{PRIORITY.get(p, '0.8')}</priority>\n  </url>"
    for p in PAGES)
write("sitemap.xml",
      '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")

write("robots.txt",
      "User-agent: *\n"
      "Allow: /\n\n"
      f"Sitemap: {SITE}/sitemap.xml\n")

write("ads.txt",
      "# Google AdSense — replace pub-XXXXXXXXXXXXXXXX with your real publisher ID after approval\n"
      "google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0\n")

# Content-Security-Policy: locks the site to first-party code + the Google ad
# network only. 'unsafe-inline'/'unsafe-eval' in script-src are REQUIRED by
# Google AdSense (it injects inline scripts and uses eval); if you ever drop
# AdSense you can remove them for a stricter policy. All first-party code uses
# no inline event handlers and HTML-escapes every user-supplied value, so the
# realistic XSS surface is already closed — the other directives (object-src,
# base-uri, frame-ancestors, form-action) block clickjacking, base-tag and
# form-hijacking attacks even with the ad allowances in place.
GOOGLE = ("https://pagead2.googlesyndication.com https://*.googlesyndication.com "
          "https://*.google.com https://*.googleadservices.com https://*.gstatic.com "
          "https://*.doubleclick.net https://adservice.google.com https://tpc.googlesyndication.com "
          "https://*.adtrafficquality.google")
# Google Analytics (gtag.js) hosts — script from googletagmanager, beacons to google-analytics.
GA = "https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com"
# Cloudflare Web Analytics — Pages auto-injects beacon.min.js from
# static.cloudflareinsights.com; it reports to cloudflareinsights.com/cdn-cgi/rum.
CF_BEACON_SRC = "https://static.cloudflareinsights.com"
CF_BEACON_CONNECT = "https://cloudflareinsights.com https://static.cloudflareinsights.com"
CSP = (
    "default-src 'self'; "
    f"script-src 'self' 'unsafe-inline' 'unsafe-eval' {GOOGLE} {GA} {CF_BEACON_SRC}; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self'; "
    f"connect-src 'self' {GOOGLE} {GA} {CF_BEACON_CONNECT}; "
    f"frame-src {GOOGLE}; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'self'; "
    "upgrade-insecure-requests"
)
write("_headers",
      "/assets/*\n"
      "  Cache-Control: public, max-age=31536000, immutable\n\n"
      "/*\n"
      "  X-Content-Type-Options: nosniff\n"
      "  Referrer-Policy: strict-origin-when-cross-origin\n"
      "  X-Frame-Options: SAMEORIGIN\n"
      "  Permissions-Policy: geolocation=(), microphone=(), camera=(), interest-cohort=()\n"
      "  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload\n"
      "  Cross-Origin-Opener-Policy: same-origin-allow-popups\n"
      f"  Content-Security-Policy: {CSP}\n")

print("technical files done")

# ---- keep the hand-written homepage's asset fingerprints in sync ----------
# index.html is authored by hand (never regenerated), but its CSS/JS URLs must
# carry the same ?v= fingerprint as the generated pages or the homepage would
# keep loading stale cached assets after a deploy.
idx_path = os.path.join(ROOT, "index.html")
with open(idx_path, encoding="utf-8") as f:
    idx = f.read()
idx_new = re.sub(
    r'(/assets/(?:css/style\.css|js/i18n\.js|js/wheel-engine\.js))(\?v=[0-9a-f]+)?',
    lambda m: m.group(1) + "?v=" + ASSET_VER,
    idx)
if idx_new != idx:
    with open(idx_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(idx_new)
    print("synced index.html asset version ->", ASSET_VER)
else:
    print("index.html asset version already", ASSET_VER)
