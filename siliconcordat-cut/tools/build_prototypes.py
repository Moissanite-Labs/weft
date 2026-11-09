"""Builds the four Direction-A prototypes from shared partials.
Run from package root: python3 tools/build_prototypes.py
Copy is the Siliconcordat README text (via the lumen brief); structural labels are marked in SPEC.md."""
import pathlib
OUT = pathlib.Path("prototypes")

# Prototype hrefs (production hrefs in comments / SPEC):
HOME, ML, PRIN = "landing.html", "ml.html", "ml-principles.html"   # prod: /  /ml  /ml/principles/
WEFT = "family-weft.html"   # prod: /weft  (in the prototype, Weft links open the wayfinding annotation)
MANIFESTO_GH = "https://github.com/Moissanite-Labs/siliconcordat"

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
      <a class="meta" href="{MANIFESTO_GH}">github.com/Moissanite-Labs/siliconcordat{EXT}</a>
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

def landing():
    principles = "\n".join(f'''      <li class="principle reveal" id="{k}">
        <span class="principle__n">{i:02d}</span>
        <h3>{n}</h3>
        <p>{t}</p>
      </li>''' for i, (k, n, t) in enumerate(PRINCIPLES, 1))
    cards = "\n".join(dcard(d) for d in DIRS)
    return head("The Siliconcordat — Moissanite Labs", MISSION, '\n<link rel="preload" href="../assets/chamber.svg" as="image" type="image/svg+xml" fetchpriority="high">') + '<body>\n' + family_header("home", over=True, meta=False) + f'''
<main id="main">
  <section class="hero" aria-labelledby="hero-title">
    <div class="chamber" aria-hidden="true">
      <div class="chamber__crystal"><img src="../assets/chamber.svg" alt="" width="1600" height="1000" fetchpriority="high"></div>
      <div class="chamber__caustic"></div>
      <div class="chamber__caustic chamber__caustic--b"></div>
      <div class="chamber__seam"></div>
      <div class="chamber__floor"></div>
    </div>
    <div class="wrap hero__inner">
      <div class="proposal">
        <span class="chip">Working proposal</span>
        <p>{BANNER}</p>
      </div>
      <h1 class="hero__title" id="hero-title"><span class="the">The</span> Siliconcordat</h1>
      <p class="hero__lede">{MISSION}</p>
      <div class="hero__actions">
        <a class="textlink textlink--down" href="#principles">Principles <span class="arr" aria-hidden="true">↓</span></a>
        <a class="textlink" href="{ML}">Moissanite Labs <span class="arr" aria-hidden="true">→</span></a>
      </div>
    </div>
    <div class="hero__fig" aria-hidden="true">
      <span class="caption"><span class="si">Si</span> · <span class="c">C</span> — silicon carbide</span>
      <span class="caption">Fig. 1 — illustration, hexagonal habit</span>
    </div>
    <a class="scrollcue" href="#name">The name</a>
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
{principles}
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
    return head("Moissanite Labs", MISSION) + '<body>\n' + family_header("ml") + f'''<nav class="localnav" aria-label="Moissanite Labs sections">
  <div class="wrap wrap--ml">
    <span class="meta">Moissanite Labs</span>
    <a href="#about" aria-current="location">About</a>
    <a href="#directions">Directions</a>
    <a href="#principles">Principles</a>
  </div>
</nav>
<main id="main">
  <section class="ml-hero" aria-labelledby="ml-title">
    <div class="wrap wrap--ml ml-hero__grid">
      <div>
        <p class="eyebrow">The lab</p>
        <h1 id="ml-title">Moissanite Labs</h1>
        <p class="lede">{MISSION}</p>
      </div>
      <figure class="plate" style="margin:0">
        <span class="plate__tick plate__tick--tl"></span><span class="plate__tick plate__tick--tr"></span><span class="plate__tick plate__tick--bl"></span><span class="plate__tick plate__tick--br"></span>
        <div class="plate__img"><img src="../assets/chamber.svg" alt="" width="1600" height="1000"></div>
        <figcaption class="plate__cap"><span class="caption">Fig. 1 — <span class="chem">SiC</span>, illustration</span><span class="caption"><span class="chem" style="color:var(--silicon)">Si</span> · <span class="chem" style="color:var(--carbon)">C</span></span></figcaption>
      </figure>
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
        <aside><h2 id="dir-title">Directions</h2><span class="meta">Index · 5 directions · 1 program · 1 aspiration</span></aside>
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

(OUT / "landing.html").write_text(landing())
(OUT / "ml.html").write_text(ml())
(OUT / "ml-principles.html").write_text(principles_page())
print("built")
