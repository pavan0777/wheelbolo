# -*- coding: utf-8 -*-
"""Generates Wheel Bolo template + trust pages and technical files.
Output files are committed static HTML — there is NO runtime build step.
Run: python _gen.py  (re-run if shared chrome changes)."""
import os, json, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://wheelbolo.com"
ADS_CLIENT = "ca-pub-XXXXXXXXXXXXXXXX"  # <-- replace after AdSense approval

# ---------------------------------------------------------------- shared chrome
def head(title, desc, canonical, *, og_type="website", og_image="/assets/img/og-default.png",
         extra_head="", jsonld=None):
    blocks = []
    blocks.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
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
  <link rel="stylesheet" href="/assets/css/style.css" />

  <!-- Google AdSense — replace {ADS_CLIENT} with your publisher ID after approval -->
  <link rel="preconnect" href="https://pagead2.googlesyndication.com" crossorigin />
  <link rel="preconnect" href="https://googleads.g.doubleclick.net" crossorigin />
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS_CLIENT}" crossorigin="anonymous"></script>''')
    if jsonld:
        blocks.append('  <script type="application/ld+json">\n' +
                      json.dumps(jsonld, ensure_ascii=False, indent=2) + '\n  </script>')
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

FOOTER = '''
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

  <script src="/assets/js/i18n.js"></script>
  <script src="/assets/js/wheel-engine.js"></script>
</body>
</html>
'''

def app_section(eyebrow, h1, lead):
    return f'''
    <section class="hero">
      <div class="container">
        <div class="app-grid">
          <div class="wheel-col">
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
            </div>
            <p id="winner-banner" class="winner-banner" role="status" aria-live="polite"></p>
          </div>

          <div class="controls-col">
            <div class="panel">
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
                <button class="btn btn-primary btn-lg" type="button" data-spin>
                  <span aria-hidden="true">🎯</span> <span data-spin-label data-i18n="app.spin">Spin the Wheel</span>
                </button>
                <button class="btn btn-secondary" type="button" data-shuffle data-i18n="app.shuffle">Shuffle</button>
                <button class="btn btn-secondary" type="button" data-reset data-i18n="app.reset">Reset</button>
              </div>
              <div class="action-row" style="margin-top:0.6rem">
                <button class="btn btn-secondary" type="button" data-share>
                  <span aria-hidden="true">📲</span> <span data-i18n="app.share">Share result</span>
                </button>
                <button class="btn btn-secondary" type="button" data-copy-link>
                  <span aria-hidden="true">🔗</span> <span data-i18n="app.copyLink">Copy link</span>
                </button>
              </div>
            </div>

            <div class="history">
              <h2><span aria-hidden="true">📜</span> <span data-i18n="history.title">Spin history</span></h2>
              <p id="history-empty" class="history-empty" data-i18n="history.empty">No spins yet — your results will appear here.</p>
              <ol id="history-list" class="history-list" aria-live="polite"></ol>
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

# ------------------------------------------------------------------- page data
CARDS = {
  "classroom": ("🎓", "Classroom Name Picker", "Pick a student fairly for answers, turns and group work.", "/classroom-name-picker/"),
  "diwali":    ("🪔", "Diwali Lucky Draw", "Run a fair lucky draw at your Diwali party or office.", "/diwali-lucky-draw-wheel/"),
  "ipl":       ("🏏", "IPL Team Picker", "Spin to assign an IPL team for fantasy or gully cricket.", "/ipl-team-picker-wheel/"),
  "dinner":    ("🍛", "What's for Dinner?", "End the daily debate — spin the wheel of dinner ideas.", "/dinner-decider-wheel/"),
  "santa":     ("🎁", "Secret Santa Picker", "Draw names for a gift exchange without rigging.", "/secret-santa-picker/"),
}

TEMPLATES = [
  {
    "slug": "classroom-name-picker",
    "name": "Classroom Name Picker",
    "title": "Classroom Name Picker — Random Student Wheel | Wheel Bolo",
    "desc": "A free random student name picker wheel for teachers. Add your class list, spin, and call on a student fairly. Hindi & English names. No sign-up.",
    "eyebrow": "🎓 For teachers &amp; classrooms",
    "h1": "Classroom Name Picker",
    "lead": "Call on students fairly. Add your class list, spin the wheel, and let chance decide who answers next.",
    "mode": "random",
    "entries": ["Aarav","Diya","Kabir","Saanvi","Vihaan","Anaya","Reyansh","Ananya","Arjun",
                "Ishita","Aditya","Myra","रिया","कबीर","आरव","दीया"],
    "article": '''
        <h2>A fair way to call on students</h2>
        <p>Calling on the same few raised hands is easy — but it leaves quieter students behind. The Classroom Name Picker spins through your whole class list and lands on one name at random, so every student has an equal chance to answer, read aloud, or lead an activity. It takes the pressure off you and adds a little fun to the room.</p>
        <h3>How teachers use it</h3>
        <ul>
          <li><strong>Cold-call fairly:</strong> spin to pick who answers the next question.</li>
          <li><strong>Assign turns:</strong> reading, presenting, or solving a problem on the board.</li>
          <li><strong>Make groups:</strong> use elimination mode to draw students one by one into teams.</li>
          <li><strong>Pick a helper:</strong> line leader, monitor, or attendance helper for the day.</li>
        </ul>
        <h3>Add your own class list</h3>
        <p>The wheel comes pre-filled with sample names in both English and Hindi (हिंदी) so you can see how it works. Replace them with your students — type one name per line, or paste your list from a register. Switch on <em>Elimination</em> mode when you want each student picked only once, which is perfect for fair group formation or a turn order that covers everyone before repeating.</p>
        <p>Everything runs in your browser. Nothing is saved or sent anywhere, and you can share the exact list with a colleague using the Copy link button.</p>
''',
    "related": ["diwali","santa","dinner"],
  },
  {
    "slug": "diwali-lucky-draw-wheel",
    "name": "Diwali Lucky Draw",
    "title": "Diwali Lucky Draw Wheel — Lucky Winner Picker | Wheel Bolo",
    "desc": "Run a fair Diwali lucky draw online. Add names, spin the wheel, and pick a lucky winner for your Diwali party, office, or housing society. Free, no sign-up.",
    "eyebrow": "🪔 Happy Diwali",
    "h1": "Diwali Lucky Draw Wheel",
    "lead": "Pick a lucky winner the fun way. Add the names, spin, and let the festival of lights choose.",
    "mode": "elim",
    "entries": ["Priya","Rohan","Aunty ji","Sharma uncle","Neha","Vikram","Meera","Anil",
                "Pooja","Sanjay","Kavya","Deepak"],
    "article": '''
        <h2>The joy of a Diwali lucky draw</h2>
        <p>No Diwali party is complete without a lucky draw. Whether it's a get-together at home, a Diwali celebration at the office, or the annual function in your housing society, the lucky draw is the moment everyone waits for. This wheel makes it effortless — add every guest's name, spin, and reveal the winner with a burst of confetti. No paper slips, no folded chits in a bowl, and no arguments about whether the draw was fair.</p>
        <h3>How to run your draw</h3>
        <ol>
          <li>Type each participant's name, one per line, or paste your guest list.</li>
          <li>Keep <em>Elimination</em> mode on so each winner is removed — ideal when you have several prizes to give away.</li>
          <li>Spin once per prize, from the smallest gift up to the grand prize.</li>
          <li>Tap Share result to send the winner card to your family or office WhatsApp group instantly.</li>
        </ol>
        <h3>Why it feels fair to everyone</h3>
        <p>Each spin uses your browser's secure random generator, so there is genuinely no way to rig the outcome — every name has the same chance. That transparency is what makes a lucky draw fun rather than suspicious. Light the diyas, gather everyone around the phone or screen, and let Wheel Bolo pick your Diwali winners. Shubh Deepavali!</p>
''',
    "related": ["santa","classroom","ipl"],
  },
  {
    "slug": "ipl-team-picker-wheel",
    "name": "IPL Team Picker",
    "title": "IPL Team Picker Wheel — Randomly Assign IPL Teams | Wheel Bolo",
    "desc": "Spin to randomly assign an IPL team. All 10 teams pre-loaded — perfect for fantasy leagues, gully cricket, friendly predictions and box cricket. Free wheel.",
    "eyebrow": "🏏 Cricket season",
    "h1": "IPL Team Picker Wheel",
    "lead": "Let the wheel hand you an IPL team. All 10 teams loaded and ready — spin and play.",
    "mode": "elim",
    "entries": ["Chennai Super Kings","Mumbai Indians","Royal Challengers Bengaluru",
                "Kolkata Knight Riders","Sunrisers Hyderabad","Delhi Capitals",
                "Punjab Kings","Rajasthan Royals","Gujarat Titans","Lucknow Super Giants"],
    "article": '''
        <h2>Pick your IPL team at random</h2>
        <p>When friends gather for a prediction game, a fantasy draft, or a round of box cricket, the first question is always the same: who gets which team? The IPL Team Picker settles it instantly. All ten franchises are pre-loaded on the wheel — Chennai Super Kings, Mumbai Indians, Royal Challengers Bengaluru, Kolkata Knight Riders, Sunrisers Hyderabad, Delhi Capitals, Punjab Kings, Rajasthan Royals, Gujarat Titans and Lucknow Super Giants — so you just spin and go.</p>
        <h3>Great for</h3>
        <ul>
          <li><strong>Fantasy &amp; prediction leagues:</strong> assign each player a team to support for the season.</li>
          <li><strong>Gully &amp; box cricket:</strong> decide which side each captain represents.</li>
          <li><strong>Watch-party games:</strong> everyone backs the team the wheel gives them.</li>
          <li><strong>Friendly bets:</strong> a neutral, unbiased way to draw teams.</li>
        </ul>
        <h3>Each team only once</h3>
        <p>This wheel uses <em>Elimination</em> mode by default, so once a team is picked it is removed — letting you deal out all ten teams to your group without repeats. Want to keep picking from the full list instead? Switch to <em>Random pick</em> mode. You can also edit the list to use just your favourite teams, or add player names for a captain draft.</p>
''',
    "related": ["dinner","classroom","santa"],
  },
  {
    "slug": "dinner-decider-wheel",
    "name": "Dinner Decider",
    "title": "What's for Dinner? — Indian Food Decision Wheel | Wheel Bolo",
    "desc": "Can't decide what to cook or order? Spin the dinner decider wheel loaded with Indian food favourites and let it choose tonight's meal. Free and fun.",
    "eyebrow": "🍛 What's cooking tonight?",
    "h1": "What's for Dinner? Decision Wheel",
    "lead": "End the daily 'kya banaye?' debate. Spin the wheel of Indian favourites and let dinner decide itself.",
    "mode": "random",
    "entries": ["Biryani","Masala Dosa","Paneer Butter Masala","Chole Bhature","Rajma Chawal",
                "Pav Bhaji","Maggi","Idli Sambhar","Khichdi","Veg Pulao","Roti Sabzi","Pasta",
                "Order out 🛵"],
    "article": '''
        <h2>Never argue about dinner again</h2>
        <p>"Aaj khaane mein kya banaye?" is the question that stumps every household, every single evening. The Dinner Decider takes the decision off your plate. The wheel comes loaded with everyday Indian favourites — from biryani and masala dosa to rajma chawal, pav bhaji and the ever-reliable Maggi — plus a cheeky "Order out" slice for the nights you just can't be bothered.</p>
        <h3>How to use it</h3>
        <ol>
          <li>Spin as-is for a quick decision, or edit the list to match what's in your kitchen.</li>
          <li>Add family favourites, leftovers to finish, or restaurants you like to order from.</li>
          <li>Spin — and commit to whatever the wheel lands on. No re-rolls!</li>
        </ol>
        <h3>Make it your own</h3>
        <p>Cooking for the week? Add seven options and use it to plan a different meal each day. Running a tiffin service or a small kitchen? Use it to surprise customers with a dish of the day. Because your list is saved right in the page link, you can bookmark your personalised dinner wheel or share it with the family cook in one tap. Simple, fast, and a little bit fun — exactly what a tired evening needs.</p>
''',
    "related": ["ipl","classroom","diwali"],
  },
  {
    "slug": "secret-santa-picker",
    "name": "Secret Santa Picker",
    "title": "Secret Santa Picker — Free Gift Exchange Wheel | Wheel Bolo",
    "desc": "Run a fair Secret Santa or gift exchange draw online. Add names, spin, and pick who gives to whom — no paper chits needed. Free, private, no sign-up.",
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
    "related": ["diwali","classroom","dinner"],
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
    rel_cards = [CARDS[k] for k in tpl["related"]]
    page = (
        head(tpl["title"], tpl["desc"], url, og_type="website",
             jsonld=breadcrumb_jsonld(tpl["name"], url), extra_head=extra)
        + HEADER
        + breadcrumbs(tpl["name"])
        + '\n  <main id="main">'
        + app_section(tpl["eyebrow"], tpl["h1"], tpl["lead"])
        + AD_SLOT
        + '\n    <section class="section">\n      <article class="container prose">'
        + tpl["article"]
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
        <p><em>Last updated: 23 June 2026.</em></p>
        <p>Wheel Bolo ("we", "us") respects your privacy. This policy explains what information is and is not collected when you use <a href="/">wheelbolo.com</a>.</p>

        <h2>Your wheel data stays with you</h2>
        <p>The names and options you type into the wheel are processed entirely in your own browser. We do <strong>not</strong> have a server database and we never receive, store, or transmit your lists. The only way your data leaves your device is if <em>you</em> choose to share it — using the Copy link button (which encodes your list into the page URL) or the Share result button (which creates an image on your device).</p>

        <h2>Cookies and local storage</h2>
        <p>The core tool does not require cookies or local storage to function. However, the third-party advertising described below may set cookies in your browser.</p>

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
         "/dinner-decider-wheel/", "/secret-santa-picker/", "/about/", "/contact/", "/privacy-policy/"]
PRIORITY = {"/": "1.0"}
today = "2026-06-23"
urls = "\n".join(
    f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{today}</lastmod>\n"
    f"    <changefreq>{'weekly' if p in ('/',) else 'monthly'}</changefreq>\n"
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
          "https://*.doubleclick.net https://adservice.google.com https://tpc.googlesyndication.com")
CSP = (
    "default-src 'self'; "
    f"script-src 'self' 'unsafe-inline' 'unsafe-eval' {GOOGLE}; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self'; "
    f"connect-src 'self' {GOOGLE}; "
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
