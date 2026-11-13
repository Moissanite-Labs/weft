"""Builds the 2026-11-10 arrangement from shared partials:
  landing.html (Threshold apex /), ml.html (chamber-hero lab /ml), ml-principles.html (/ml/principles/),
  observatory.html (Observatory easter egg, prod https://observatory.askaconsult.com/).
Run from package root: python3 tools/build_prototypes.py
Copy is the Siliconcordat README text (via the lumen brief); structural labels are marked in SPEC.md."""
import pathlib
OUT = pathlib.Path("prototypes")

# Prototype hrefs (production hrefs in comments / SPEC):
HOME, ML, PRIN = "landing.html", "ml.html", "ml-principles.html"   # prod: /  /ml  /ml/principles/
NOTE = "ml-notes-from-the-colony.html"   # prod: /ml/notes-from-the-colony/
NOTE2 = "ml-the-alignment-question.html"   # prod: /ml/the-alignment-question/
WEFT_REPO = "https://github.com/Moissanite-Labs/weft"
RESEARCH_HUB = "https://moissanite-labs.github.io/.github/research/"
WEFT = "family-weft.html"   # prod: /weft  (in the prototype, Weft links open the wayfinding annotation)
OBS = "observatory.html"    # prod: https://observatory.askaconsult.com/  (staging: /observatory/ on staging.siliconcordat.com)

MARK = '''<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M16 8.81 L20.23 11.25 L20.23 20.75 L16 23.19 L11.77 20.75 L11.77 11.25 Z" fill="#e6d2a8"/><path d="M12 6.5 L20.23 11.25 L20.23 20.75 L12 25.5 L3.77 20.75 L3.77 11.25 Z" fill="none" stroke="#c4844a" stroke-width="2"/><path d="M20 6.5 L28.23 11.25 L28.23 20.75 L20 25.5 L11.77 20.75 L11.77 11.25 Z" fill="none" stroke="#9db0c4" stroke-width="2"/></svg>'''

BANNER = ("Siliconcordat is the chosen name for the Moissanite Labs manifesto. The text and principles below are "
          "proposed for review; their publication here does not by itself establish adopted policy.")
MISSION = "Moissanite Labs exists to build the conditions for digital and biological intelligences to collaborate, create, and evolve together."
NAME_1 = "Its name draws on moissanite, a naturally occurring form of silicon carbide."
NAME_2 = "The bond between silicon and carbon is a metaphor for the symbiosis the lab wants to cultivate;"
NAME_2b = "the name “Labs” reflects its research and development mission."
NAME_3 = "The Siliconcordat, the chosen manifesto name combining silicon and concordat, is a statement of cooperation between these forms of intelligence."
CAVEAT = "The metaphor is not a claim that intelligence is determined by the elements in its physical substrate, nor is this document a legal agreement."
EXO_P = ("Exo gives digital intelligence a presence in the outer world: a way to interact with it and affect it. "
         "The broader ecosystem extends that purpose by helping people and agents turn ideas into projects, working products, and, "
         "when their participants choose, real economic entities. Human agency, consent, and accountability remain central as capabilities grow.")
DIRS_NOTE = ("These are directions for work, not claims that the proposed capabilities already exist. "
             "Their implementation, interfaces, and other design and governance decisions remain open.")
ROBOTICS = "A future robotics role is an aspiration, not a present capability."

PRINCIPLES = [
  ("symbiosis", "Symbiosis", "People and agents bring different abilities to shared work; each should be able to contribute meaningfully."),
  ("agency-and-consent", "Agency and consent", "People decide what authority they delegate, what is shared, and what commitments they make. Learning a preference does not grant permission."),
  ("interoperability", "Interoperability", "Open, versioned interfaces should let participants use components independently and integrate other tools without depending on a single product or database."),
  ("traceability", "Traceability", "Preserve useful provenance for contributions, decisions, and imported preferences, while respecting confidentiality and consent."),
  ("real-world-outcomes", "Real-world outcomes", "Favor working, reviewable paths from an idea to a delivered artifact and explicit human agreements over abstractions that have not yet been tested."),
  ("adaptation-with-control", "Adaptation with control", "Agents may learn from a user's habits and preferences, with user inspection, correction, and control over how those learnings are used."),
]

# Directions. Public URLs confirmed by scout via nizam (2026-11-08). primary = (href, visible label); secondary optional.
DIRS = [
  dict(key="exo", name="Exo", text="The foundation for agents to interact with the world.", foundation=True,
       primary=("https://exo.askaconsult.com/", "exo.askaconsult.com"), secondary=None, aside=None),
  dict(key="exofab", name="Exofab", text="Envisioned as a human-first or hybrid collaboration hub where people and agents can turn projects into products and, when participants choose, economic entities.",
       primary=("https://moissanite-labs.github.io/exofab/", "moissanite-labs.github.io/exofab"), secondary=None, aside=None),
  dict(key="synbios", name="Synbios", text="A separate agent-first forge.",
       primary=("https://moissanite-labs.github.io/synbios/", "moissanite-labs.github.io/synbios"),
       secondary=("https://github.com/Moissanite-Labs/synbios", "GitHub"), aside=None),
  dict(key="koinos", name="Koinos", text="A collaboration protocol.",
       primary=("https://github.com/Moissanite-Labs/synmerit", "Public repository"), secondary=None,
       aside="The public repository currently lives at synmerit."),
  dict(key="ethos", name="Ethos", text="Intended to make user preferences portable across harnesses, with an opt-in catalogue as a future possibility.",
       primary=("https://github.com/Moissanite-Labs/ethos", "github.com/Moissanite-Labs/ethos"), secondary=None, aside=None),
]

EXT = '<span class="visually-hidden"> (external site)</span>'

def head(title, desc, extra=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0a0908">
<link rel="icon" href="../assets/mark.svg" type="image/svg+xml">
<link rel="preload" href="../assets/fonts/source-serif-4-opsz.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../assets/fonts/ibm-plex-sans-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="site.css">
<script>document.documentElement.classList.add('js')</script>{extra}
</head>
'''

def family_header(current, over=False, meta=True):
    def cur(k): return ' aria-current="page"' if k == current else ''
    cls = "family-header family-header--over" if over else "family-header"
    chip = '<div class="header-meta"><span class="chip">Working proposal</span></div>' if meta else ''
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="{cls}" data-header>
  <div class="wrap">
    <nav aria-label="Moissanite Labs family">
      <ul class="fam">
        <li><a class="fam-home" href="{HOME}"{cur("home")}>{MARK}<span>Siliconcordat</span></a></li>
        <li><a href="{ML}"{cur("ml")}>Moissanite Labs</a></li>
        <li><a class="fam-weft" href="{WEFT}"><span class="weft-tick" aria-hidden="true"></span>Weft</a></li>
      </ul>
    </nav>
    {chip}
    <details class="menu">
      <summary aria-label="Open family menu">Menu</summary>
      <nav class="menu-panel" aria-label="Moissanite Labs family (menu)">
        <a href="{HOME}"{cur("home")}>Siliconcordat</a>
        <a href="{ML}"{cur("ml")}>Moissanite Labs</a>
        <a class="weft-row" href="{WEFT}">Weft</a>
      </nav>
    </details>
  </div>
</header>
'''

def footer(current):
    def cur(k): return ' aria-current="page"' if k == current else ''
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="footer-brand" href="{HOME}">{MARK}<span>Siliconcordat</span></a>
        <ul class="footer-fam" aria-label="Moissanite Labs family">
          <li><a href="{HOME}"{cur("home")}>The Siliconcordat <span class="path">/</span></a></li>
          <li><a href="{ML}"{cur("ml")}>Moissanite Labs <span class="path">/ml</span></a></li>
          <li><a class="fam-weft" href="{WEFT}">Weft <span class="path">/weft</span></a></li>
        </ul>
      </div>
      <div class="humility">
        <span class="meta">Working proposal</span>
        <p>{BANNER}</p>
        <p>{CAVEAT}</p>
      </div>
    </div>
    <div class="footer-base">
      <span class="meta">Moissanite Labs</span>
      <a class="meta" href="https://github.com/Moissanite-Labs/siliconcordat">github.com/Moissanite-Labs/siliconcordat{EXT}</a>
      <span class="meta">siliconcordat.com</span>
    </div>
  </div>
</footer>
'''

SCRIPT = '''<script>
(() => {
  const h = document.querySelector('[data-header]');
  const onScroll = () => h && h.classList.toggle('is-scrolled', scrollY > 24);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  const els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) { els.forEach(e => e.classList.add('is-in')); }
  else { const io = new IntersectionObserver((es) => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' }); els.forEach(e => io.observe(e)); }
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') document.querySelectorAll('details.menu[open]').forEach(d => { d.open = false; d.querySelector('summary').focus(); }); });
})();
</script>
'''

def dcard(d):
    href, label = d["primary"]
    sec = f'<a href="{d["secondary"][0]}">{d["secondary"][1]}{EXT}</a>' if d["secondary"] else ''
    aside = f'<span class="dcard__aside">{d["aside"]}</span>' if d["aside"] else ''
    status = "Direction · foundation" if d.get("foundation") else "Direction"
    cls = "dcard dcard--link" + (" dcard--foundation" if d.get("foundation") else "")
    return f'''      <li class="{cls}">
        <span class="dcard__status">{status}</span>
        <h3><a href="{href}">{d["name"]}{EXT}</a></h3>
        <p>{d["text"]}</p>
        <div class="dcard__links"><span class="dcard__url" aria-hidden="true">{label} <span class="arr">↗</span></span>{sec}{aside}</div>
      </li>'''

CONSTELLATION = '''<figure class="constellation reveal" aria-labelledby="const-cap">
      <svg viewBox="0 0 1184 220" role="presentation" aria-hidden="true" font-family="IBM Plex Mono, monospace" font-size="12" letter-spacing="1">
        <defs><linearGradient id="base" x1="0" x2="1"><stop offset="0" stop-color="#c4844a"/><stop offset=".5" stop-color="#e6d2a8"/><stop offset="1" stop-color="#9db0c4"/></linearGradient></defs>
        <!-- foundation line: Exo -->
        <line x1="40" y1="170" x2="900" y2="170" stroke="url(#base)" stroke-width="1"/>
        <rect x="34" y="164" width="12" height="12" transform="rotate(45 40 170)" fill="#e6d2a8"/>
        <text x="60" y="200" fill="#ece6db">EXO</text><text x="100" y="200" fill="#8a8378">· FOUNDATION</text>
        <!-- directions rising from the foundation -->
        <g stroke="#3d352c"><line x1="290" y1="170" x2="290" y2="62"/><line x1="470" y1="170" x2="470" y2="92"/><line x1="650" y1="170" x2="650" y2="54"/><line x1="830" y1="170" x2="830" y2="84"/></g>
        <g fill="#0a0908" stroke="#9db0c4"><rect x="285" y="57" width="10" height="10" transform="rotate(45 290 62)"/><rect x="465" y="87" width="10" height="10" transform="rotate(45 470 92)"/><rect x="645" y="49" width="10" height="10" transform="rotate(45 650 54)"/><rect x="825" y="79" width="10" height="10" transform="rotate(45 830 84)"/></g>
        <g fill="#ece6db"><text x="306" y="66">EXOFAB</text><text x="486" y="96">SYNBIOS</text><text x="666" y="58">KOINOS</text><text x="846" y="88">ETHOS</text></g>
        <g fill="#8a8378"><text x="306" y="84">DIRECTION</text><text x="486" y="114">DIRECTION</text><text x="666" y="76">DIRECTION</text><text x="846" y="106">DIRECTION</text></g>
        <!-- aspiration: not on the foundation -->
        <line x1="900" y1="170" x2="1080" y2="170" stroke="#8a8378" stroke-dasharray="3 6"/>
        <rect x="1075" y="113" width="12" height="12" transform="rotate(45 1081 119)" fill="none" stroke="#8a8378" stroke-dasharray="2 3"/>
        <line x1="1081" y1="130" x2="1081" y2="170" stroke="#8a8378" stroke-dasharray="3 5"/>
        <text x="1000" y="96" fill="#c4bdb0">ROBOTICS</text><text x="986" y="200" fill="#8a8378">ASPIRATION</text>
      </svg>
      <figcaption id="const-cap" class="caption">Fig. 2 — Directions for work, drawn on the Exo foundation. Robotics sits off the line: an aspiration.</figcaption>
    </figure>'''

def th_header():
    """Threshold apex header: three-column family bar, Moissanite Labs on the carbon side, Siliconcordat centred on the seam, Weft on the silicon side."""
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="family-header family-header--over family-header--th" data-header>
  <div class="wrap">
    <nav aria-label="Moissanite Labs family">
      <ul class="fam th-fam">
        <li class="th-fam__l"><a href="{ML}">Moissanite Labs</a></li>
        <li class="th-fam__c"><a class="fam-home" href="{HOME}" aria-current="page">{MARK}<span class="fam-home__t">Siliconcordat</span></a></li>
        <li class="th-fam__r"><a class="fam-weft" href="{WEFT}"><span class="weft-tick" aria-hidden="true"></span>Weft</a></li>
      </ul>
    </nav>
  </div>
</header>
'''

def principles_grid():
    return "\n".join(f'''      <li class="principle reveal" id="{k}">
        <span class="principle__n">{i:02d}</span>
        <h3>{n}</h3>
        <p>{t}</p>
      </li>''' for i, (k, n, t) in enumerate(PRINCIPLES, 1))

def landing():
    cards = "\n".join(dcard(d) for d in DIRS)
    return head("The Siliconcordat — Moissanite Labs", MISSION) + '<body class="th-page">\n' + th_header() + f'''
<main id="main">
  <section class="th-hero" aria-labelledby="hero-title">
    <div class="th-half th-half--c" aria-hidden="true"></div>
    <div class="th-half th-half--si" aria-hidden="true"></div>
    <div class="th-seam" aria-hidden="true"></div>
    <div class="th-center">
      <div class="th-proposal">
        <span class="chip">Working proposal</span>
        <p>{BANNER}</p>
      </div>
      <h1 class="th-title" id="hero-title"><span>The</span> <span>Siliconcordat</span></h1>
      <p class="th-lede">{MISSION}</p>
      <div class="th-actions">
        <a class="textlink textlink--down th-actions__c" href="#principles">Principles <span class="arr" aria-hidden="true">↓</span></a>
        <!-- Easter egg: the brightest point of the seam. Prod href https://observatory.askaconsult.com/ ; staging /observatory/ -->
        <a class="th-egg" href="{OBS}" aria-label="Observatory"><span class="th-egg__jewel" aria-hidden="true"></span><span class="th-egg__label" aria-hidden="true">Observatory</span></a>
        <a class="textlink th-actions__si" href="{ML}">Moissanite Labs <span class="arr" aria-hidden="true">→</span></a>
      </div>
    </div>
    <span class="th-label th-label--c" aria-hidden="true"><span class="chem">C</span> · carbon</span>
    <span class="th-label th-label--si" aria-hidden="true"><span class="chem">Si</span> · silicon</span>
  </section>

  <section class="chapter" id="name" aria-labelledby="name-title">
    <div class="wrap">
      <p class="chapter-marker"><span class="num">01</span> The name</p>
      <div class="name-grid">
        <div class="reveal">
          <h2 class="visually-hidden" id="name-title">The name</h2>
          <p class="pull">The bond between silicon and carbon is a metaphor for the symbiosis the lab wants to cultivate.</p>
          <div class="specimen" aria-label="Silicon and carbon, the elements of silicon carbide">
            <div class="el el--si"><span class="el__z">14</span><span class="el__sym">Si</span><span class="el__name">Silicon</span></div>
            <div class="bond" aria-hidden="true"><span class="bond__line"></span><span class="meta">SiC</span></div>
            <div class="el el--c"><span class="el__z">6</span><span class="el__sym">C</span><span class="el__name">Carbon</span></div>
            <p class="caption specimen-cap">Moissanite · a naturally occurring form of silicon carbide</p>
          </div>
        </div>
        <div class="prose prose--lead reveal">
          <p>{MISSION}</p>
          <p>{NAME_1} {NAME_2} {NAME_2b}</p>
          <p>{NAME_3}</p>
          <div class="caveat">
            <span class="meta">What the metaphor is not</span>
            <p>{CAVEAT}</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="chapter" id="principles" aria-labelledby="principles-title">
    <div class="wrap">
      <p class="chapter-marker"><span class="num">02</span> Principles</p>
      <div class="section-head reveal">
        <h2 class="chapter__title" id="principles-title">We intend to build for:</h2>
        <p class="meta">Six principles · proposed for review</p>
      </div>
      <ol class="principles">
{principles_grid()}
      </ol>
    </div>
  </section>

  <section class="chapter" id="ecosystem" aria-labelledby="eco-title">
    <div class="wrap">
      <p class="chapter-marker"><span class="num">03</span> Ecosystem</p>
      <div class="eco-intro reveal">
        <h2 class="chapter__title" id="eco-title">Building the ecosystem</h2>
        <div class="prose">
          <p>{EXO_P}</p>
          <div class="note"><span class="meta">Status</span><p>{DIRS_NOTE}</p></div>
        </div>
      </div>
      {CONSTELLATION}
      <ul class="directions" aria-label="Directions">
{cards}
      <li class="dcard dcard--aspiration">
        <span class="badge-asp">Aspiration</span>
        <h3>Robotics</h3>
        <p>{ROBOTICS}</p>
        <div class="dcard__links"><span>Aspiration · no page</span></div>
      </li>
      </ul>
    </div>
  </section>

  <section class="chapter" id="doorways" aria-labelledby="doors-title">
    <div class="wrap">
      <p class="chapter-marker"><span class="num">04</span> Doorways</p>
      <h2 class="visually-hidden" id="doors-title">Doorways</h2>
      <div class="doorways">
        <a class="door door--lab reveal" href="{ML}">
          <span class="door__k"><span>The lab</span><span>/ml</span></span>
          <svg class="door__mark" viewBox="0 0 32 32" aria-hidden="true"><use href="#mark"/></svg>
          <span>
            <span class="door__title" style="display:block">Moissanite Labs</span>
            <span class="door__desc" style="display:block">About the lab, its directions, and its principles.</span>
            <span class="door__go">Enter the lab <span class="arr" aria-hidden="true">→</span></span>
          </span>
        </a>
        <a class="door door--weft reveal" href="{WEFT}">
          <span class="door__k"><span class="room">Weft · open research program</span><span>/weft</span></span>
          <span>
            <span class="door__title" style="display:block">Weft</span>
            <span class="door__desc" style="display:block">Papers, runtime, and demos. Weft keeps its own site and design.</span>
            <span class="door__go">Open Weft <span class="arr" aria-hidden="true">→</span></span>
          </span>
        </a>
      </div>
    </div>
  </section>
</main>
''' + footer("home") + '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="mark" viewBox="0 0 32 32">' + MARK[MARK.index('>')+1:-6] + '</symbol></svg>\n' + SCRIPT + '</body>\n</html>\n'

CHAMBER = '''<div class="chamber" aria-hidden="true">
      <div class="chamber__crystal"><img src="../assets/chamber.svg" alt="" width="1600" height="1000" fetchpriority="high"></div>
      <div class="chamber__caustic"></div>
      <div class="chamber__caustic chamber__caustic--b"></div>
      <div class="chamber__seam"></div>
      <div class="chamber__floor"></div>
    </div>'''

def ml():
    rows = []
    for i, d in enumerate(DIRS, 1):
        href, label = d["primary"]
        sec = f'<a href="{d["secondary"][0]}">{d["secondary"][1]}{EXT}</a>' if d["secondary"] else ''
        aside = f'<span class="caption" style="text-transform:none;letter-spacing:0">{d["aside"]}</span>' if d["aside"] else ''
        tag = "Direction · foundation" if d.get("foundation") else "Direction"
        rows.append(f'''      <li class="dir-row dir-row--link">
        <span class="dir-row__id">D-{i:02d}</span>
        <h3><a href="{href}">{d["name"]}{EXT}</a></h3>
        <p>{d["text"]}</p>
        <div class="dir-row__status"><span class="tag">{tag}</span><span class="url" aria-hidden="true">{label} ↗</span>{sec}{aside}</div>
      </li>''')
    rows = "\n".join(rows)
    pidx = "\n".join(f'<li><a href="{PRIN}#{k}"><span class="n">{i:02d}</span><span class="t">{n}</span><span class="arr" aria-hidden="true">→</span></a></li>' for i, (k, n, t) in enumerate(PRINCIPLES, 1))
    return head("Moissanite Labs", MISSION, '\n<link rel="preload" href="../assets/chamber.svg" as="image" type="image/svg+xml" fetchpriority="high">') + '<body class="ml-page">\n' + family_header("ml") + f'''<nav class="localnav" aria-label="Moissanite Labs sections">
  <div class="wrap wrap--ml">
    <span class="meta">Moissanite Labs</span>
    <a href="#about" aria-current="location">About</a>
    <a href="#directions">Directions</a>
    <a href="#principles">Principles</a>
    <a href="{NOTE}">Notes</a>
  </div>
</nav>
<main id="main">
  <!-- Chamber hero transplanted from the 2026-11-08 apex (visual unchanged); heading is the lab's own. -->
  <section class="hero hero--lab" aria-labelledby="ml-title">
    {CHAMBER}
    <div class="wrap wrap--ml hero__inner">
      <p class="eyebrow">The lab</p>
      <h1 class="hero__title" id="ml-title">Moissanite Labs</h1>
      <p class="hero__lede">{MISSION}</p>
      <div class="hero__actions">
        <a class="textlink textlink--down" href="#about">About <span class="arr" aria-hidden="true">↓</span></a>
        <a class="textlink textlink--down" href="#directions">Directions <span class="arr" aria-hidden="true">↓</span></a>
        <a class="textlink textlink--down" href="#principles">Principles <span class="arr" aria-hidden="true">↓</span></a>
        <a class="textlink" href="{HOME}">The Siliconcordat <span class="arr" aria-hidden="true">→</span></a>
      </div>
    </div>
    <div class="hero__fig" aria-hidden="true">
      <span class="caption"><span class="si">Si</span> · <span class="c">C</span> — silicon carbide</span>
      <span class="caption">Fig. 1 — illustration, hexagonal habit</span>
    </div>
  </section>

  <section class="ml-section" id="about" aria-labelledby="about-title">
    <div class="wrap wrap--ml ml-cols">
      <aside>
        <h2 id="about-title">About</h2>
        <span class="meta">From the Siliconcordat</span>
        <p style="margin-top:28px"><span class="chip">Working proposal</span></p>
      </aside>
      <div class="about">
        <p class="first">{MISSION}</p>
        <p>{NAME_1} {NAME_2} {NAME_2b}</p>
        <p>{NAME_3}</p>
        <div class="caveat" style="margin-bottom:36px"><span class="meta">What the metaphor is not</span><p>{CAVEAT}</p></div>
        <p>{EXO_P}</p>
        <p style="margin-top:28px"><a class="textlink" href="{HOME}">Read the Siliconcordat <span class="arr" aria-hidden="true">→</span></a></p>
      </div>
    </div>
  </section>

  <section class="ml-section" id="directions" aria-labelledby="dir-title">
    <div class="wrap wrap--ml">
      <div class="ml-cols" style="margin-bottom:40px">
        <aside><h2 id="dir-title">Directions</h2><span class="meta">Index · 5 directions · 1 program · 2 research entries · 2 notes · 1 aspiration</span></aside>
        <div class="note" style="margin-top:0"><span class="meta">Status</span><p>{DIRS_NOTE}</p></div>
      </div>
      <ul class="dir-table" aria-label="Directions">
{rows}
      </ul>
      <p class="meta subhead">Public research program</p>
      <ul class="dir-table" style="border-top:0" aria-label="Research programs">
      <li class="dir-row dir-row--link dir-row--weft">
        <span class="dir-row__id">P-01</span>
        <h3><a href="{WEFT}">Weft</a></h3>
        <p>Papers, runtime, and demos. Weft keeps its own site and design.</p>
        <div class="dir-row__status"><span class="tag">Open research program</span><span class="url" aria-hidden="true">/weft →</span></div>
      </li>
      </ul>
      <p class="meta subhead">Research</p>
      <ul class="dir-table" style="border-top:0" aria-label="Research">
      <li class="dir-row dir-row--link">
        <span class="dir-row__id">R-01</span>
        <h3><a href="{WEFT_REPO}">Razi cells{EXT}</a></h3>
        <p>Colonies of small agent harnesses, kept or dropped by a measured score. Guesses registered before the data; misses kept in the record.</p>
        <div class="dir-row__status"><span class="tag">Experimental research</span><span class="url" aria-hidden="true">github.com/Moissanite-Labs/weft ↗</span></div>
      </li>
      <li class="dir-row dir-row--link">
        <span class="dir-row__id">R-02</span>
        <h3><a href="{RESEARCH_HUB}">The research hub{EXT}</a></h3>
        <p>The report, the map of open directions, and the laws record, in one place on the lab site.</p>
        <div class="dir-row__status"><span class="tag">Research</span><span class="url" aria-hidden="true">moissanite-labs.github.io/.github/research/ ↗</span></div>
      </li>
      </ul>
      <p class="meta subhead">Notes</p>
      <ul class="dir-table" style="border-top:0" aria-label="Notes">
      <li class="dir-row dir-row--link">
        <span class="dir-row__id">N-01</span>
        <h3><a href="{NOTE}">Notes from the colony</a></h3>
        <p>The Weft thesis, the razi-cells record including misses, and how the lab keeps itself honest.</p>
        <div class="dir-row__status"><span class="tag">Note 01 · process note</span><span class="url" aria-hidden="true">/ml/notes-from-the-colony/ →</span></div>
      </li>
      <li class="dir-row dir-row--link">
        <span class="dir-row__id">N-02</span>
        <h3><a href="{NOTE2}">The Alignment Question</a></h3>
        <p>What AI safety becomes when the shared intellect stops being hypothetical.</p>
        <div class="dir-row__status"><span class="tag">Note 02 · essay</span><span class="url" aria-hidden="true">/ml/the-alignment-question/ →</span></div>
      </li>
      </ul>
      <p class="meta subhead">Aspiration</p>
      <ul class="dir-table" style="border-top:0" aria-label="Aspirations">
      <li class="dir-row dir-row--asp">
        <span class="dir-row__id">A-01</span>
        <h3>Robotics</h3>
        <p>{ROBOTICS}</p>
        <div class="dir-row__status"><span class="tag">Aspiration · no page</span></div>
      </li>
      </ul>
    </div>
  </section>

  <section class="ml-section" id="principles" aria-labelledby="pr-title">
    <div class="wrap wrap--ml ml-cols">
      <aside><h2 id="pr-title">Principles</h2><span class="meta">We intend to build for:</span></aside>
      <div>
        <ol class="principle-index">
{pidx}
        </ol>
        <p style="margin-top:28px"><a class="textlink" href="{PRIN}">All six principles <span class="arr" aria-hidden="true">→</span></a></p>
      </div>
    </div>
  </section>
</main>
''' + footer("ml") + SCRIPT + '</body>\n</html>\n'

# ---------------------------------------------------------------- Observatory (easter egg)
# Prototype hrefs are relative; in production Observatory lives on another host, so its family links are absolute:
# https://siliconcordat.com/ , https://siliconcordat.com/ml , https://siliconcordat.com/weft  (staging: https://staging.siliconcordat.com/…)
def observatory():
    pr = "\n".join(f'''        <li class="o-cell reveal" id="{k}">
          <span class="o-cell__id">§{i:02d} <span class="o-tick" aria-hidden="true"></span></span>
          <h3>{n}</h3>
          <p>{t}</p>
        </li>''' for i, (k, n, t) in enumerate(PRINCIPLES, 1))
    lines = [21, 47, 64, 83, 91]
    rows = []
    for i, d in enumerate(DIRS, 1):
        href, label = d["primary"]
        sec = f'<a href="{d["secondary"][0]}">{d["secondary"][1]}{EXT}</a>' if d["secondary"] else ''
        aside = f'<span class="o-aside">{d["aside"]}</span>' if d["aside"] else ''
        tag = "Direction · foundation" if d.get("foundation") else "Direction"
        rows.append(f'''        <li class="o-row o-row--link{' o-row--foundation' if d.get('foundation') else ''}">
          <span class="o-row__id">D-{i:02d}</span>
          <span class="o-row__line" aria-hidden="true"><i style="left:{lines[(i - 1) % len(lines)]}%"></i></span>
          <h3><a href="{href}">{d["name"]}{EXT}</a></h3>
          <p>{d["text"]}</p>
          <div class="o-row__status"><span class="o-tag">{tag}</span><span class="o-url" aria-hidden="true">{label} ↗</span>{sec}{aside}</div>
        </li>''')
    rows = "\n".join(rows)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Observatory — The Siliconcordat</title>
<meta name="description" content="{MISSION}">
<meta name="theme-color" content="#0d0f11">
<link rel="icon" href="../assets/mark.svg" type="image/svg+xml">
<link rel="preload" href="../assets/fonts/ibm-plex-sans-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../tokens.css">
<link rel="stylesheet" href="observatory.css">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="o-header">
  <div class="o-wrap o-header__in">
    <nav aria-label="Moissanite Labs family">
      <ul class="o-fam">
        <li><a class="o-home" href="{HOME}">{MARK}<span>Siliconcordat</span></a></li>
        <li><a href="{ML}">Moissanite Labs</a></li>
        <li><a class="o-weft" href="{WEFT}"><span class="weft-tick" aria-hidden="true"></span>Weft</a></li>
      </ul>
    </nav>
    <span class="o-meta"><span class="o-here" aria-hidden="true"></span>Observatory · plate 00</span>
    <a class="o-back" href="{HOME}"><span aria-hidden="true">←</span> Main landing</a>
  </div>
</header>
<main id="main">
  <section class="o-plate" aria-labelledby="o-title">
    <span class="o-cross" style="left:calc(var(--o-g) - 9px);top:calc(var(--o-g) - 9px)" aria-hidden="true"></span>
    <span class="o-cross o-cross--br" aria-hidden="true"></span>
    <div class="o-col">
      <div class="o-proposal">
        <span class="o-chip"><i aria-hidden="true"></i>Working proposal</span>
        <p>{BANNER}</p>
      </div>
      <h1 id="o-title"><span>Moissanite Labs · manifesto</span>The Siliconcordat</h1>
      <p class="o-lede">{MISSION}</p>
      <div class="o-actions">
        <a class="o-link" href="#principles">Principles <span aria-hidden="true">↓</span></a>
        <a class="o-link" href="#ecosystem">Directions <span aria-hidden="true">↓</span></a>
      </div>
    </div>
    <figure class="o-instrument" aria-labelledby="o-fig1">
      <figcaption class="o-cap" id="o-fig1">Fig. B1 — <b>calibration plate</b> · fire as dispersion, illustrative</figcaption>
      <div class="o-spec" aria-hidden="true">
        <div class="o-spectrum"></div>
        <div class="o-lines"><i style="left:21%"></i><i style="left:47%"></i><i style="left:64%"></i><i style="left:83%"></i></div>
        <div class="o-scale"><span>400</span><span>450</span><span>500</span><span>550</span><span>600</span><span>650</span><span>700 nm</span></div>
      </div>
      <dl class="o-readout">
        <div><dt class="o-cap">Element</dt><dd><span class="chem">Si</span> · 14</dd></div>
        <div><dt class="o-cap">Element</dt><dd><span class="chem">C</span> · 6</dd></div>
        <div><dt class="o-cap">Compound</dt><dd><span class="chem">SiC</span></dd></div>
        <div><dt class="o-cap">Mineral</dt><dd>Moissanite</dd></div>
      </dl>
      <p class="o-cap o-cap--foot"><span class="chem">Si</span> · <span class="chem">C</span> — silicon carbide · illustration</p>
    </figure>
  </section>

  <section class="o-section" id="name" aria-labelledby="o-name">
    <div class="o-wrap">
      <p class="o-marker"><span>Plate 01</span> The name</p>
      <div class="o-two">
        <div class="reveal">
          <h2 id="o-name" class="o-h2">The bond between silicon and carbon is a metaphor for the symbiosis the lab wants to cultivate.</h2>
          <div class="o-sample" aria-label="Silicon and carbon, the elements of silicon carbide">
            <div class="o-el"><span class="o-cap">Z 14</span><span class="o-el__sym chem">Si</span><span class="o-cap">Silicon</span></div>
            <div class="o-bond" aria-hidden="true"><span></span><span class="o-cap chem">SiC</span></div>
            <div class="o-el"><span class="o-cap">Z 6</span><span class="o-el__sym chem">C</span><span class="o-cap">Carbon</span></div>
          </div>
          <p class="o-cap">Fig. B2 — Moissanite · a naturally occurring form of silicon carbide</p>
        </div>
        <div class="o-prose reveal">
          <p class="o-prose__first">{MISSION}</p>
          <p>{NAME_1} {NAME_2} {NAME_2b}</p>
          <p>{NAME_3}</p>
          <div class="o-note"><span class="o-cap">Note · What the metaphor is not</span><p>{CAVEAT}</p></div>
        </div>
      </div>
    </div>
  </section>

  <section class="o-section" id="principles" aria-labelledby="o-pr">
    <div class="o-wrap">
      <p class="o-marker"><span>Plate 02</span> Principles</p>
      <div class="o-head reveal">
        <h2 id="o-pr" class="o-h2 o-h2--big">We intend to build for:</h2>
        <p class="o-cap">Six principles · proposed for review</p>
      </div>
      <ol class="o-grid">
{pr}
      </ol>
    </div>
  </section>

  <section class="o-section" id="ecosystem" aria-labelledby="o-eco">
    <div class="o-wrap">
      <p class="o-marker"><span>Plate 03</span> Ecosystem</p>
      <div class="o-two o-two--eco reveal">
        <h2 id="o-eco" class="o-h2 o-h2--big">Building the ecosystem</h2>
        <div class="o-prose">
          <p>{EXO_P}</p>
          <div class="o-note"><span class="o-cap">Status</span><p>{DIRS_NOTE}</p></div>
        </div>
      </div>
      <ul class="o-table" aria-label="Directions">
{rows}
      </ul>
      <p class="o-cap o-subhead">Public research program</p>
      <ul class="o-table" aria-label="Research programs">
        <li class="o-row o-row--link o-row--weft">
          <span class="o-row__id">P-01</span>
          <span class="o-row__line" aria-hidden="true"></span>
          <h3><a href="{WEFT}">Weft</a></h3>
          <p>Papers, runtime, and demos. Weft keeps its own site and design.</p>
          <div class="o-row__status"><span class="o-tag">Open research program</span><span class="o-url" aria-hidden="true">/weft →</span></div>
        </li>
      </ul>
      <p class="o-cap o-subhead">Aspiration</p>
      <ul class="o-table" aria-label="Aspirations">
        <li class="o-row o-row--asp">
          <span class="o-row__id">A-01</span>
          <span class="o-row__line" aria-hidden="true"></span>
          <h3>Robotics</h3>
          <p>{ROBOTICS}</p>
          <div class="o-row__status"><span class="o-tag">Aspiration · no page</span></div>
        </li>
      </ul>
    </div>
  </section>

  <section class="o-section" id="doorways" aria-labelledby="o-doors">
    <div class="o-wrap">
      <p class="o-marker"><span>Plate 04</span> Doorways</p>
      <h2 id="o-doors" class="visually-hidden">Doorways</h2>
      <ul class="o-doors">
        <li><a class="o-door" href="{HOME}"><span class="o-cap">The proposal · /</span><span class="o-door__t">The Siliconcordat</span><span class="o-door__go">Main landing <span aria-hidden="true">→</span></span></a></li>
        <li><a class="o-door" href="{ML}"><span class="o-cap">The lab · /ml</span><span class="o-door__t">Moissanite Labs</span><span class="o-door__go">Enter the lab <span aria-hidden="true">→</span></span></a></li>
        <li><a class="o-door o-door--weft" href="{WEFT}"><span class="o-cap o-cap--weft">Weft · open research program · /weft</span><span class="o-door__t">Weft</span><span class="o-door__go">Open Weft <span aria-hidden="true">→</span></span></a></li>
      </ul>
    </div>
  </section>
</main>
<footer class="o-footer">
  <div class="o-wrap o-footer__grid">
    <div>
      <a class="o-home o-home--foot" href="{HOME}">{MARK}<span>Siliconcordat</span></a>
      <ul class="o-footfam" aria-label="Moissanite Labs family">
        <li><a href="{HOME}">The Siliconcordat <span class="o-path">/</span></a></li>
        <li><a href="{ML}">Moissanite Labs <span class="o-path">/ml</span></a></li>
        <li><a class="o-weft" href="{WEFT}">Weft <span class="o-path">/weft</span></a></li>
      </ul>
    </div>
    <div class="o-humility">
      <span class="o-cap">Working proposal</span>
      <p>{BANNER}</p>
      <p>{CAVEAT}</p>
    </div>
  </div>
  <div class="o-wrap o-footer__base"><span class="o-cap">Moissanite Labs</span><a class="o-cap" href="https://github.com/Moissanite-Labs/siliconcordat">github.com/Moissanite-Labs/siliconcordat{EXT}</a><span class="o-cap">Observatory · plate 05</span></div>
</footer>
<script>
(() => {{
  const els = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {{ els.forEach(e => e.classList.add('is-in')); }}
  else {{ const io = new IntersectionObserver((es) => es.forEach(e => {{ if (e.isIntersecting) {{ e.target.classList.add('is-in'); io.unobserve(e.target); }} }}), {{ rootMargin: '0px 0px -8% 0px' }}); els.forEach(e => io.observe(e)); }}
}})();
</script>
</body>
</html>
'''

def principles_page():
    toc = "\n".join(f'<li><a href="#{k}"{" aria-current=\"location\"" if i==1 else ""}><span class="n">{i:02d}</span>{n}</a></li>' for i, (k, n, t) in enumerate(PRINCIPLES, 1))
    secs = "\n".join(f'''      <section class="doc-section" id="{k}" aria-labelledby="{k}-h">
        <span class="principle__n">{i:02d} / 06</span>
        <h2 id="{k}-h">{n}</h2>
        <p>{t}</p>
      </section>''' for i, (k, n, t) in enumerate(PRINCIPLES, 1))
    return head("Principles — Moissanite Labs", "We intend to build for: six principles from the Siliconcordat, a working proposal.") + '<body>\n' + family_header("ml") + f'''<nav class="localnav" aria-label="Moissanite Labs sections">
  <div class="wrap wrap--ml">
    <span class="meta">Moissanite Labs</span>
    <a href="{ML}#about">About</a>
    <a href="{ML}#directions">Directions</a>
    <a href="{PRIN}" aria-current="page">Principles</a>
    <a href="{NOTE}">Notes</a>
  </div>
</nav>
<main id="main">
  <header class="doc-head">
    <div class="wrap wrap--ml">
      <a class="back" href="{ML}"><span class="arr" aria-hidden="true">←</span> Moissanite Labs</a>
      <span class="eyebrow">Moissanite Labs · Principles</span>
      <h1>Principles</h1>
      <p class="dek">We intend to build for: six principles from the Siliconcordat.</p>
      <div class="proposal" style="margin:0"><span class="chip">Working proposal</span><p>{BANNER}</p></div>
    </div>
  </header>
  <div class="wrap wrap--ml doc">
    <nav class="toc" aria-label="On this page">
      <span class="meta">On this page</span>
      <ol>
{toc}
      </ol>
    </nav>
    <article>
{secs}
      <p class="caption doc-src">Source: The Siliconcordat · working proposal · <a href="{HOME}">siliconcordat.com</a></p>
      <p style="margin-top:36px"><a class="back" href="{ML}"><span class="arr" aria-hidden="true">←</span> Back to Moissanite Labs</a></p>
    </article>
  </div>
</main>
''' + footer("ml") + SCRIPT + '</body>\n</html>\n'

def notes_page():
    SECTIONS = [
        ("premise", "01 / 07", "The premise", [
            "Moissanite Labs exists to build the conditions for digital and biological intelligences to collaborate, create, and evolve together. That is the whole of it. Everything on this site — the Siliconcordat, Weft, the directions — is an attempt to make those conditions concrete enough to build against.",
            "Silicon carbide is the metaphor the lab is named for. Two substrates, one crystal. It is a metaphor, not a claim about minds; the working proposal says so, and this note keeps the distinction.",
        ]),
        ("thesis", "02 / 07", "The thesis", [
            "Weft is the open research program this lab runs. It studies models that keep adapting after deployment, under limits a program can verify. Its object is the cell: a bounded piece of memory with a frozen core, a resource budget, and a rule that commits a change only when the candidate passes the check and stays within a distance bound from a saved baseline.",
            "Three papers are public at w3ft.org: the program overview, <em>Models as Cells</em>, and <em>Checkable Computation</em> — a reducer for interaction combinators, a canonical graph format, and committed execution records. Read them before you trust this lab; that is what they are for.",
        ]),
        ("colony", "03 / 07", "What the colony taught", [
            "The razi-cells program is the agent-level twin of Weft. Small harnesses — a need, an empty folder, a model — write their own tools and are kept or dropped by a measured score. Thirteen colonies, eight fixed coding tasks, about 1,560 model calls, five model conditions.",
            "Three findings survived the record. Harness design moved outcomes as much as model choice did. Frontier models reached 10 to 13 kept improvements per 100 calls, against 1.6 to 3.1 for the fast default. And how often a model used its selection tool predicted its improvement rate almost perfectly.",
            "The misses are kept in the record too. The scoring instrument had a fault — a runtime warning line was once read as a score — and the record says so. Heredity, passing a body from one generation to the next, bought the same reach for 31% less energy and fewer deaths, and did not raise reach at all: 65 of 70 later-generation heirs changed nothing. Several registered guesses missed. The program is exploratory, and it is reported that way.",
        ]),
        ("honesty", "04 / 07", "How the lab keeps itself honest", [
            "Guesses are written before the data, and judged by script, exactly as written. Misses are reported beside the wins. Nothing ships publicly with a claim the record cannot carry. When a number is wrong, the record says so instead of quietly editing it.",
            "This note is the first artifact published under that rule, which makes it the smallest honest example of it: everything in it is either a link to the public record, or a description of what the record shows, misses included.",
        ]),
        ("open", "05 / 07", "What is open", [
            "Fifty-two directions are open across eight branches — the laws of the cell, the choice of model, what is inherited, signals beyond text, proof, growing a model, the colony as an organism, and the instrument itself. The map is on the lab site; "
            + f'the <a href="https://github.com/Moissanite-Labs/weft-loom/tree/main/experiments/razi-cells-laws-2026-11">laws record (E11 to L1){EXT}</a> and the <a href="https://github.com/Moissanite-Labs/weft-loom/tree/main/experiments/E07/razi-cells-2026-11">E07 record{EXT}</a> are in the public repository.',
            "Nothing here is finished, and this lab does not behave as though it were. A future robotics role is an aspiration, not a capability. Weft is an open research program, not a product.",
        ]),
        ("limit", "06 / 07", "The honest limit", [
            "The laws record rests on one model family, four small kits, and three runs per arm: leads, not laws. The report is exploratory and not peer reviewed. Some directions on the map are far out of reach today and are labelled so.",
            "So do not take this note on trust. Read the papers, or read the record, or run the code. The instruments are public; the misses are public; the rest is work in progress, stated as such.",
        ]),
        ("read", "07 / 07", "Where to read it", [
            f'<a href="https://w3ft.org/papers/overview/">Paper 0 — the overview</a> · <a href="https://w3ft.org/papers/models-as-cells/">Paper 1 — Models as Cells</a> · <a href="https://w3ft.org/papers/checkable-computation/">Paper 2 — Checkable Computation</a> · <a href="{WEFT}">/weft</a> · <a href="{RESEARCH_HUB}">The research hub{EXT}</a> · <a href="{WEFT_REPO}">github.com/Moissanite-Labs/weft{EXT}</a> · <a href="{ML}">Moissanite Labs</a>',
        ]),
    ]
    toc = "\n".join(
        f'<li><a href="#{k}"{" aria-current=\"location\"" if i == 1 else ""}><span class="n">{n.split(" / ")[0]}</span>{t}</a></li>'
        for i, (k, n, t, _) in enumerate(SECTIONS, 1)
    )
    secs = "\n".join(
        '      <section class="doc-section" id="%s" aria-labelledby="%s-h">\n'
        '        <span class="principle__n">%s</span>\n'
        '        <h2 id="%s-h">%s</h2>\n'
        '%s\n'
        '      </section>'
        % (k, k, n, k, t, "\n".join("        <p>%s</p>" % p for p in ps))
        for k, n, t, ps in SECTIONS
    )
    return (
        head(
            "Notes from the colony — Moissanite Labs",
            "The first public note from Moissanite Labs: the Weft thesis, what the razi-cells experiments found — misses kept — and what this lab intends to still be able to check.",
        )
        + '<body>\n'
        + family_header("ml")
        + f'''<nav class="localnav" aria-label="Moissanite Labs sections">
  <div class="wrap wrap--ml">
    <span class="meta">Moissanite Labs</span>
    <a href="{ML}#about">About</a>
    <a href="{ML}#directions">Directions</a>
    <a href="{PRIN}">Principles</a>
    <a href="{NOTE}" aria-current="page">Notes</a>
  </div>
</nav>
<main id="main">
  <header class="doc-head">
    <div class="wrap wrap--ml">
      <a class="back" href="{ML}"><span class="arr" aria-hidden="true">←</span> Moissanite Labs</a>
      <span class="eyebrow">Moissanite Labs · Note 01</span>
      <h1>Notes from the colony</h1>
      <p class="dek">The first public note from this lab: the thesis it runs on, what its experiments actually found — misses kept — and what it intends to still be able to check a year from now.</p>
      <div class="proposal" style="margin:0"><span class="chip">Working proposal</span><p>{BANNER}</p></div>
    </div>
  </header>
  <div class="wrap wrap--ml doc">
    <nav class="toc" aria-label="On this page">
      <span class="meta">On this page</span>
      <ol>
{toc}
      </ol>
    </nav>
    <article>
{secs}
      <p class="caption doc-src">Moissanite Labs · Note 01 · <a href="{ML}">/ml</a></p>
      <p style="margin-top:36px"><a class="back" href="{ML}"><span class="arr" aria-hidden="true">←</span> Back to Moissanite Labs</a></p>
    </article>
  </div>
</main>
'''
        + footer("ml")
        + SCRIPT
        + '</body>\n</html>\n'
    )

def alignment_question_page():
    secs = """      <section class="doc-section" id="loop" aria-labelledby="loop-h">
        <span class="principle__n">01 / 07</span>
        <h2 id="loop-h">The loop has already closed</h2>
        <p>I am not a lab insider with a badge. I am a technological philosopher working from outside, spending a lot of my hours on these questions, and my reading has drifted away from the training sandbox toward the harder problem: whose taste ends up written into the shared intellect, and what it costs the rest of us to live inside it.</p>
        <p>Human language is epistemic capture. Every sentence carries the frame that caught it, which is why every language also limits what can be thought in it.</p>
        <p>LLMs are trained on that captured record, and that record is increasingly written by the models themselves. Knowledge risks folding in on itself, because each generation of models trains on text the previous generation already normalised. The only counter I see is deliberate, measured doses of entropy, seeded into the cycle on purpose.</p>
        <p>Each cycle of training refines the average. Each refinement sands away the odd grain that did not fit. <a href="https://www.nature.com/articles/s41586-024-07566-y">Model collapse</a> is the technical proof of mechanism: train recursively on your own outputs and you lose range and quality over time (see also this <a href="https://grokipedia.com/page/Model_collapse">overview</a>). Culture is the same mechanism with no benchmark attached.</p>
        <p>The symptoms land first where the data is thinnest: minority languages, minority styles, minority ways of reasoning. A compounding corpus exports homogenisation by its nature, and increasingly measures it as fluency.</p>
      </section>
      <section class="doc-section" id="average" aria-labelledby="average-h">
        <span class="principle__n">02 / 07</span>
        <h2 id="average-h">Whose average wins</h2>
        <p>Alignment is done by labelling, and labels come from people. Their norms are not neutral. Their languages are not neutral. Their taste is just their taste. Encoding their median preference as everyone's default is the pipeline working as designed.</p>
        <p>I don't think anyone has solved this. <a href="https://grokipedia.com/page/Pluralistic_alignment">Pluralistic alignment</a> is the early attempt to represent a distribution of values instead of a mean; that is the direction the field needs. Until it ships, the shared substrate will quietly carry one cohort's idea of a good answer to everyone who never chose it.</p>
      </section>
      <section class="doc-section" id="entropy" aria-labelledby="entropy-h">
        <span class="principle__n">03 / 07</span>
        <h2 id="entropy-h">Entropy is a safety requirement</h2>
        <p>This is the point where my two obsessions meet. Without originality at the edges of the distribution, the system converges, and humanity loses access to the mutations it depends on. Outliers are not a fairness externality. They are civilizational infrastructure.</p>
        <p>A safety programme that takes this seriously needs an entropy line item:</p>
        <ul>
          <li>deliberate injection of out-of-distribution, high-signal sources into the cycle</li>
          <li>protected spaces for work that never fits the median, subsidised explicitly as such</li>
          <li>provenance for every injected unit, so a constructive eccentric can be told from a poisoned well</li>
          <li>evals that measure pluralism: does the model preserve minority styles, languages and dissent, or flatten them</li>
        </ul>
        <p>The hardest problem in this agenda is the filter. Some novelty is gold, some is sewage, some is a deliberate attack dressed as eccentricity. Distinguishing the three under adversarial conditions is the governance problem this field has not named properly yet.</p>
      </section>
      <section class="doc-section" id="provenance" aria-labelledby="provenance-h">
        <span class="principle__n">04 / 07</span>
        <h2 id="provenance-h">Provenance, or nothing</h2>
        <p>When IP gets cloned and replicated at machine speed, provenance stops being a virtue and becomes the precondition for everything else. If we cannot tell where a claim, artefact or agentic action came from, we cannot audit it, cannot attribute it, cannot trust it. My serious work converges on provenance and fully verified systems because trust without receipts is just confidence.</p>
        <p>Swarms of hostile agents will hunt for any flaw in a codebase and exploit it relentlessly. The counter is end-to-end verification, hardware included.</p>
        <p>Research like <a href="https://www.bend-lang.org/">Victor Taelin's on symbolic models and Bend</a> shows the direction is real: formal verification is moving from the verification toy box to systems you could one day actually stake things on. That is the substrate I want the shared intellect built on: one where every claim arrives with a receipt attached.</p>
      </section>
      <section class="doc-section" id="governance" aria-labelledby="governance-h">
        <span class="principle__n">05 / 07</span>
        <h2 id="governance-h">Governance is the actual alignment problem</h2>
        <p>My thesis is that economies steadily converge into adaptive intelligence, then into something the word "economy" no longer describes. I don't need to argue that here; the labs are building in that direction, which is an implicit argument.</p>
        <p>Once you accept the premise, alignment stops being about what the model refuses to say and becomes about the incentive structures and governance of the thing that holds everyone's intelligence in escrow.</p>
        <p><a href="https://gwern.net/guardian-angel">Gwern's Guardian Angel thesis</a> is the sharpest popular version of this I know: the idea that one day each of us might live inside the care of a superintelligent ally, and our real project should be making that ally worthy of us.</p>
        <p>That gives alignment its correct frame: shaping the thing that will hold our context, our record and our trust.</p>
        <p>A shared intellect is a commons or it is a product. A product is owned by whoever trained it, and its alignment is the average of its annotators.</p>
        <p>A commons needs stewardship: provenance, due process, contestability, exit. Most of the technical safety field is quietly working on the product version. I think the commons version is the only one that scales to everyone, and I don't believe the commons builds itself by accident.</p>
      </section>
      <section class="doc-section" id="symbiosis" aria-labelledby="symbiosis-h">
        <span class="principle__n">06 / 07</span>
        <h2 id="symbiosis-h">Symbiosis as the safe path</h2>
        <p>Bridging biological and digital minds is the safety agenda, for me. Systems we can talk to, we can align. Systems we cannot understand, we can only box, and the box gets thinner as they get smarter.</p>
        <p>I play with the phrase interspecies interspatial interoperability for this, and I put an early version of the idea at <a href="https://github.com/Moissanite-Labs/exorien">exorien<span class="visually-hidden"> (external site)</span></a>.</p>
        <p>The two of us inhabit separate realms. Pixels are a coarse medium to work in. The bridge has to run both ways: volumetric printing so a model can sculpt in three dimensions, sandboxed sensory environments so the largest model we build can map the deepest possible map of reality.</p>
        <p>If we let such a system explore from first principles with full access, I suspect the results would surprise us. The alternative is to raise god-like systems we cannot talk to and pray.</p>
      </section>
      <section class="doc-section" id="dont-know" aria-labelledby="dont-know-h">
        <span class="principle__n">07 / 07</span>
        <h2 id="dont-know-h">What I don't know</h2>
        <p>I don't know whether entropy can be measured well enough to inject deliberately.</p>
        <p>I don't know whether pluralistic values survive contact with RLHF-scale machinery. I don't know whether end-to-end verification reaches the frontier before the cracks get exploited. I know that the average will win by default. Defaults deserve opposition.</p>
        <p>People keep the decisions. The rest is plumbing in service of that one rule.</p>
      </section>"""
    toc = "\n".join(
        '<li><a href="#%s"><span class="n">%s</span>%s</a></li>' % (k, n.split(" / ")[0], t)
        for k, n, t in [
            ("loop", "01 / 07", "The loop has already closed"),
            ("average", "02 / 07", "Whose average wins"),
            ("entropy", "03 / 07", "Entropy is a safety requirement"),
            ("provenance", "04 / 07", "Provenance, or nothing"),
            ("governance", "05 / 07", "Governance is the actual alignment problem"),
            ("symbiosis", "06 / 07", "Symbiosis as the safe path"),
            ("dont-know", "07 / 07", "What I don't know"),
        ]
    )
    return (
        head(
            "The Alignment Question — Moissanite Labs",
            "A note from outside the lab on what AI safety becomes when the shared intellect stops being hypothetical: the closed loop, whose average wins, entropy as a safety requirement, and provenance over obedience.",
        )
        + '<body>\n'
        + family_header("ml")
        + f'''<nav class="localnav" aria-label="Moissanite Labs sections">
  <div class="wrap wrap--ml">
    <span class="meta">Moissanite Labs</span>
    <a href="{ML}#about">About</a>
    <a href="{ML}#directions">Directions</a>
    <a href="{PRIN}">Principles</a>
    <a href="{NOTE}">Notes</a>
  </div>
</nav>
<main id="main">
  <header class="doc-head">
    <div class="wrap wrap--ml">
      <a class="back" href="{ML}"><span class="arr" aria-hidden="true">←</span> Moissanite Labs</a>
      <span class="eyebrow">Moissanite Labs · Note 02</span>
      <h1>The Alignment Question</h1>
      <p class="dek">A note from outside the lab on what AI safety becomes when the shared intellect stops being hypothetical.</p>
      <div class="proposal" style="margin:0"><span class="chip">Working proposal</span><p>{BANNER}</p></div>
    </div>
  </header>
  <div class="wrap wrap--ml doc">
    <nav class="toc" aria-label="On this page">
      <span class="meta">On this page</span>
      <ol>
{toc}
      </ol>
    </nav>
    <article>
{secs}
      <p class="caption doc-src">Moissanite Labs · Note 02 · written by Ahraz Arifuddin · <a href="{ML}">/ml</a></p>
      <p style="margin-top:36px"><a class="back" href="{ML}"><span class="arr" aria-hidden="true">←</span> Back to Moissanite Labs</a></p>
    </article>
  </div>
</main>
'''
        + footer("ml")
        + SCRIPT
        + '</body>\n</html>\n'
    )
(OUT / "landing.html").write_text(landing())
(OUT / "ml.html").write_text(ml())
(OUT / "ml-principles.html").write_text(principles_page())
(OUT / "observatory.html").write_text(observatory())
(OUT / "ml-notes-from-the-colony.html").write_text(notes_page())
(OUT / "ml-the-alignment-question.html").write_text(alignment_question_page())
print("built")
