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
  "birthday":  ("🎂", "Birthday Wheel Generator", "Spin to pick party games, a lucky guest or who goes first.", "/birthday-wheel-generator/"),
  "yesno":     ("🤔", "Yes or No Wheel", "Can't decide? Let the wheel say yes or no.", "/yes-no-wheel/"),
  "truthdare": ("😈", "Truth or Dare Wheel", "Spin for truths and dares — instant party fun.", "/truth-or-dare-wheel/"),
  "team":      ("👥", "Team Picker Wheel", "Split players into fair teams with a spin.", "/team-picker-wheel/"),
  "prize":     ("🎟️", "Prize Wheel", "Spin a prize wheel for rewards and offers.", "/prize-wheel/"),
  "giveaway":  ("🎉", "Giveaway Wheel", "Pick a random giveaway winner — fair and live.", "/giveaway-wheel/"),
  "reward":    ("⭐", "Classroom Reward Wheel", "Reward students with fun classroom perks.", "/classroom-reward-wheel/"),
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
    "title": "Prize Wheel — Free Spin to Win Prize Picker | Wheel Bolo",
    "desc": "A free online prize wheel — load your rewards, offers or prizes and spin to win. Perfect for events, stalls, classrooms and promotions. Customisable and free.",
    "eyebrow": "🎟️ Spin to win",
    "h1": "Prize Wheel",
    "lead": "Load your prizes, give it a spin, and watch the wheel land on a winner with confetti.",
    "mode": "random",
    "entries": ["Gift Card", "Free Coffee", "Movie Tickets", "10% Off", "Try Again",
                "Free Dessert", "Mystery Box", "Bonus Spin"],
    "article": '''
        <h2>A prize wheel for any event</h2>
        <p>Nothing pulls a crowd like a spinning prize wheel. Whether it is a school fair stall, a shop promotion, a trade-show booth, or a classroom treat, this free prize wheel brings the excitement without the cost of a physical wheel. Load your rewards, let people spin, and reveal the prize with a burst of confetti.</p>
        <h3>Ways to use it</h3>
        <ul>
          <li><strong>Promotions:</strong> discounts, freebies, and "try again" slices to drive footfall.</li>
          <li><strong>Events &amp; fairs:</strong> a fun, fair way to hand out prizes at a stall.</li>
          <li><strong>Classrooms &amp; teams:</strong> reward points, treats, or privileges.</li>
          <li><strong>Streams &amp; socials:</strong> spin live for your audience and share the result.</li>
        </ul>
        <h3>Set up your prizes</h3>
        <p>Replace the sample prizes with your own — type one per line, or paste a list. Keep <em>Random pick</em> mode so every prize can be won more than once, or switch to <em>Elimination</em> if each prize is one-of-a-kind and should be removed after it is won. Your prize list is saved in the page link, so you can reopen the same wheel at your next event or share it with your team.</p>
        <p>Free, no sign-up, and works on any screen — from a phone at a stall to a big display.</p>
''',
    "related": ["giveaway", "birthday", "yesno"],
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
         "/dinner-decider-wheel/", "/secret-santa-picker/", "/birthday-wheel-generator/",
         "/yes-no-wheel/", "/truth-or-dare-wheel/", "/team-picker-wheel/", "/prize-wheel/",
         "/giveaway-wheel/", "/classroom-reward-wheel/",
         "/about/", "/contact/", "/privacy-policy/"]
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
          "https://*.doubleclick.net https://adservice.google.com https://tpc.googlesyndication.com "
          "https://*.adtrafficquality.google")
# Google Analytics (gtag.js) hosts — script from googletagmanager, beacons to google-analytics.
GA = "https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com"
CSP = (
    "default-src 'self'; "
    f"script-src 'self' 'unsafe-inline' 'unsafe-eval' {GOOGLE} {GA}; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self'; "
    f"connect-src 'self' {GOOGLE} {GA}; "
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
