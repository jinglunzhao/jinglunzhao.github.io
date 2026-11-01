#!/usr/bin/env python3
"""Build a small, accessible research website and Markdown notebook."""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
CONFIG = json.loads((ROOT / "site.json").read_text())
PUBLICATIONS = json.loads((ROOT / "content" / "publications.json").read_text())
SITE_URL = CONFIG["url"].rstrip("/")
BASE = urlparse(SITE_URL).path.rstrip("/")
TODAY = datetime.now(timezone.utc).date()
MD = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable("table").enable("strikethrough")


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def path(value: str = "") -> str:
    return BASE + "/" + value.lstrip("/")


def external(url: str, label: str, css: str = "") -> str:
    return f'<a class="{css}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{label}<span class="external-arrow" aria-hidden="true">↗</span></a>'


def email_link(label: str, css: str = "") -> str:
    return f'<a class="{css}" href="mailto:{esc(CONFIG["email"])}">{label}<span class="external-arrow" aria-hidden="true">↗</span></a>'


def write(relative: str, content: str) -> None:
    destination = OUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def asset(name: str) -> str:
    digest = hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest()[:10]
    return path(f"assets/{name}") + "?v=" + digest


def page(title: str, body: str, route: str = "", active: str = "overview", description: str = "", article: dict | None = None) -> str:
    description = description or CONFIG["description"]
    canonical = SITE_URL + "/" + route.lstrip("/")
    full_title = "Jinglun Zhao — AI Evaluation, Agents & Spatial Intelligence" if not title else f"{title} — Jinglun Zhao"
    nav = []
    for key, label, href in [("overview", "Home", path()), ("focus", "Research", path("#focus")), ("research", "Publications", path("#research")), ("writing", "Writing", path("writing/")), ("about", "About", path("about/"))]:
        current = ' aria-current="page"' if active == key else ""
        nav.append(f'<a href="{href}"{current}>{label}</a>')
    structured = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": CONFIG["name"],
        "email": CONFIG["email"],
        "image": SITE_URL + "/assets/" + CONFIG["portrait"],
        "url": SITE_URL,
        "description": CONFIG["description"],
        "sameAs": [CONFIG["github"], CONFIG["linkedin"], CONFIG["scholar"]],
        "affiliation": {"@type": "Organization", "name": "Moonshot AI"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "Tsinghua University"},
        "knowsAbout": ["AI evaluation", "Open-ended evaluation", "Spatial intelligence"],
    }
    article_meta = ""
    if article:
        structured = {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": article["title"], "description": article["summary"],
            "author": {"@type": "Person", "name": CONFIG["name"], "url": SITE_URL},
            "datePublished": article["date"].isoformat(), "url": canonical,
        }
        article_meta = f'<meta property="article:published_time" content="{article["date"].isoformat()}">'
    schema = json.dumps(structured, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="theme-color" content="#f8f7f2">
  <title>{esc(full_title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:type" content="{'article' if article else 'website'}">
  <meta property="og:title" content="{esc(full_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(SITE_URL + '/assets/social.png')}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Jinglun Zhao — Evaluating AI beyond the benchmark">
  <meta name="twitter:card" content="summary_large_image">
  {article_meta}
  <link rel="icon" type="image/svg+xml" href="{path('assets/favicon.svg')}">
  <link rel="alternate" type="application/atom+xml" title="Jinglun Zhao — Writing" href="{path('feed.xml')}">
  <link rel="stylesheet" href="{asset('site.css')}">
  <script type="application/ld+json">{schema}</script>
  <script src="{asset('site.js')}" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header wrap">
    <a class="wordmark" href="{path()}" aria-label="Jinglun Zhao — home"><span class="monogram" aria-hidden="true">jz.</span><span>Jinglun Zhao</span></a>
    <button class="menu-button" type="button" aria-expanded="false" aria-controls="site-navigation" data-menu-button>Menu <span aria-hidden="true">☰</span></button>
    <nav class="site-navigation" id="site-navigation" aria-label="Main navigation">{''.join(nav)}{external(CONFIG['github'], 'GitHub', 'nav-github')}</nav>
  </header>
  <main class="wrap" id="main">{body}</main>
  <footer class="site-footer wrap">
    <div><a class="footer-name" href="{path()}">Jinglun Zhao</a><span class="footer-note">Evaluation. Agents. Spatial intelligence.</span></div>
    <div class="footer-links">{email_link('Email')}{external(CONFIG['scholar'], 'Scholar')}{external(CONFIG['github'], 'GitHub')}{external(CONFIG['linkedin'], 'LinkedIn')}<a href="{path('feed.xml')}">RSS <span aria-hidden="true">↗</span></a></div>
    <span class="copyright">© {TODAY.year} Jinglun Zhao</span>
  </footer>
</body>
</html>'''


def spatial_figure() -> str:
    # A conceptual geometric illustration, not benchmark results or measured data.
    lines = []
    radius = 105

    def project(x: float, y: float, z: float) -> tuple[float, float]:
        a = -0.42
        xx, zz = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        b = 0.32
        yy = y * math.cos(b) - zz * math.sin(b)
        return 224 + radius * xx, 205 + radius * yy

    for latitude in [-math.pi / 3, -math.pi / 6, 0, math.pi / 6, math.pi / 3]:
        points = [project(math.cos(latitude) * math.cos(t * math.pi / 40), math.sin(latitude), math.cos(latitude) * math.sin(t * math.pi / 40)) for t in range(81)]
        lines.append('<polyline points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in points) + '"/>')
    for longitude in [i * math.pi / 8 for i in range(8)]:
        points = [project(math.cos(t * math.pi / 40) * math.cos(longitude), math.sin(t * math.pi / 40), math.cos(t * math.pi / 40) * math.sin(longitude)) for t in range(81)]
        lines.append('<polyline points="' + " ".join(f"{x:.2f},{y:.2f}" for x, y in points) + '"/>')
    grid = []
    for i in range(-4, 5):
        grid.append(f'<path d="M{224 + i * 29} 271l116 67M{224 + i * 29} 405l116-67"/>')
    return f'''<figure class="spatial-figure">
      <div class="figure-top"><span class="small-label">A FIELD OF QUESTIONS</span><span class="figure-mark" aria-hidden="true">✳</span></div>
      <svg class="spatial-svg" viewBox="0 0 440 430" role="img" aria-labelledby="spatial-title spatial-desc">
        <title id="spatial-title">Exploring spatial intelligence</title>
        <desc id="spatial-desc">A wireframe sphere and cube above a coordinate grid, illustrating geometry, motion, and visual representation.</desc>
        <defs><radialGradient id="sphere-fill"><stop offset="0" stop-color="#a8bca7" stop-opacity=".25"/><stop offset="1" stop-color="#a8bca7" stop-opacity=".03"/></radialGradient></defs>
        <g fill="none" stroke="#c5cebf" stroke-width=".8">{''.join(grid)}</g>
        <path d="M224 338V66M90 338h285" fill="none" stroke="#b2bfad" stroke-dasharray="3 5"/>
        <ellipse cx="224" cy="205" rx="108" ry="106" fill="url(#sphere-fill)"/>
        <g class="sphere-wire" fill="none" stroke="#4e735a" stroke-width=".7" opacity=".8">{''.join(lines)}</g>
        <ellipse class="orbital-path" cx="224" cy="205" rx="162" ry="51" fill="none" stroke="#8a9c7e" stroke-width=".8" transform="rotate(-29 224 205)"/>
        <circle cx="84" cy="283" r="4" fill="#a35c3d"/>
        <path d="m321 256 44 26v52l-44 26-44-26v-52zM277 282l44 26 44-26M321 308v52M321 256v52" fill="#f0f1e7" fill-opacity=".75" stroke="#52715b" stroke-width="1"/>
        <path d="M85 178h38M321 137h39v-28M105 306v24h43" fill="none" stroke="#9caa91" stroke-width=".8"/>
        <g fill="#6b7a64" font-size="9" font-family="ui-monospace, monospace" letter-spacing="1.3"><text x="61" y="168">GEOMETRY</text><text x="315" y="99">REPRESENTATION</text><text x="77" y="347">MOTION</text><text x="230" y="66">z</text><text x="376" y="342">x</text></g>
      </svg>
      <figcaption><span>Understanding space.<br>Evaluating capability.</span><span class="figure-index">3D ↗</span></figcaption>
    </figure>'''


def article_card(post: dict) -> str:
    search = esc(" ".join([post["title"], post["summary"], *post["tags"]]).lower())
    return f'''<article class="post-card" data-search-text="{search}">
      <div class="post-meta"><time datetime="{post['date'].isoformat()}">{post['date'].strftime('%b %d, %Y')}</time><span>{post['minutes']} min read</span></div>
      <h2><a href="{path('writing/' + post['slug'] + '/')}">{esc(post['title'])}<span aria-hidden="true">↗</span></a></h2>
      <p>{esc(post['summary'])}</p><div class="tags">{''.join(f'<span>{esc(t)}</span>' for t in post['tags'])}</div>
    </article>'''


def research_section() -> str:
    papers = []
    for publication in PUBLICATIONS:
        authors = []
        for author in publication["authors"]:
            label = esc(author)
            if author == CONFIG["name"]:
                label = f"<strong>{label}</strong>"
            if author in publication["equal_contributors"]:
                label += '<sup>*</sup>'
            authors.append(label)
        contribution = '<span class="contribution-label">Co-first author</span>' if CONFIG["name"] in publication["equal_contributors"] else ''
        papers.append(f'''<article class="publication"><div class="publication-venue"><span>{esc(publication['venue'])}</span><span>{publication['year']}</span></div><div class="publication-body"><div class="publication-meta"><p class="small-label">REINFORCEMENT LEARNING / COMPUTATIONAL DESIGN</p>{contribution}</div><h3>{external(publication['paper'], esc(publication['title']))}</h3><p class="publication-authors">{', '.join(authors)}</p><p class="publication-summary">{esc(publication['summary'])}</p><div class="publication-links">{external(publication['paper'], 'Paper', 'text-link')}{external(publication['code'], 'Code', 'text-link')}<a class="text-link" href="{path('publications/' + publication['slug'] + '.bib')}" download>Cite <span aria-hidden="true">↓</span></a><span class="equal-note">* Equal contribution</span></div></div></article>''')
    return f'''<section class="section research-section" id="research" aria-labelledby="research-title"><div class="section-title-row"><h2 id="research-title">Selected publications</h2>{external(CONFIG['scholar'], 'Google Scholar', 'text-link')}</div>{''.join(papers)}</section>'''


def home(posts: list[dict]) -> str:
    if posts:
        writing = f'''<section class="section writing-section" aria-labelledby="writing-title"><div class="section-title-row"><h2 id="writing-title">Writing</h2><a class="text-link" href="{path('writing/')}">All writing <span aria-hidden="true">↗</span></a></div><div class="home-posts">{"".join(article_card(p) for p in posts[:2])}</div></section>'''
    else:
        writing = f'''<section class="writing-preview" aria-labelledby="writing-title"><h2 id="writing-title"><a href="{path('writing/')}">Writing <span aria-hidden="true">↗</span></a></h2><p>Notes on AI evaluation, agents, and spatial intelligence.</p></section>'''
    return f'''
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow hero-topic"><span class="status-dot" aria-hidden="true"></span>AutoEval</p>
        <h1 id="hero-title">Jinglun Zhao<span class="name-period">.</span></h1>
        <div class="hero-person"><img class="hero-avatar" src="{asset(CONFIG['portrait'])}" alt="Portrait of Jinglun Zhao" width="400" height="400" fetchpriority="high"><div class="hero-bio"><p class="hero-role">Agent Team at <strong>Moonshot AI</strong></p><p>PhD, <strong>Tsinghua IIIS</strong>, advised by <span class="hero-adviser">Prof. Yi Wu</span>.</p></div></div>
        <p class="hero-description">I build <strong>automated evaluation systems for Kimi</strong>, turning real user needs into capability metrics. My work focuses on <strong>open-ended and out-of-distribution evaluation</strong>, with a recent emphasis on <strong>3D spatial understanding and generation</strong>.</p>
        <div class="hero-links">{external(CONFIG['scholar'], 'Google Scholar', 'text-link')}{external(CONFIG['github'], 'GitHub', 'text-link')}{external(CONFIG['linkedin'], 'LinkedIn', 'text-link')}{email_link(esc(CONFIG['email']), 'text-link hero-email')}</div>
      </div>
      {spatial_figure()}
    </section>
    <section class="focus-section section" id="focus" aria-labelledby="focus-title">
      <div class="section-title-row"><h2 id="focus-title">Research & current work</h2><span class="section-note">At Kimi</span></div>
      <div class="focus-list">
        <article class="focus-item"><p class="small-label">EVALUATION SYSTEMS</p><h3>Automated evaluation</h3><p>Turn real user needs into evaluation systems, protocols, and capability metrics.</p></article>
        <article class="focus-item"><p class="small-label">BEYOND BENCHMARKS</p><h3>Open-ended & OOD tasks</h3><p>Assess tasks without directly verifiable answers and diagnose model behavior in out-of-distribution settings.</p></article>
        <article class="focus-item focus-current"><p class="small-label"><span class="status-dot" aria-hidden="true"></span>RECENT FOCUS</p><h3>3D spatial intelligence</h3><p>Evaluate 3D modeling, motion and skeletal rigging, rendering, and visual quality.</p></article>
      </div>
    </section>
    {research_section()}
    <section class="section code-section" id="code" aria-labelledby="code-title">
      <div class="section-title-row"><h2 id="code-title">Selected code</h2>{external(CONFIG['github'], 'All repositories', 'text-link')}</div>
      <div class="project-grid">
        <a class="project" href="https://github.com/jinglunzhao/ta-grading-system-for-algo" target="_blank" rel="noopener noreferrer"><div class="project-top"><span class="small-label">EVALUATION / EDUCATION</span><span aria-hidden="true">↗</span></div><h3>AI Grading System</h3><p>An automated grading system for algorithm design assignments, with AI-generated rubrics, question-level feedback, and batch processing.</p><div class="project-bottom"><span><i class="language-dot" aria-hidden="true"></i>Python</span><span>View repository</span></div></a>
      </div>
    </section>
    {writing}
    <section class="contact-section" aria-labelledby="contact-title"><div><h2 id="contact-title">Get in touch</h2><p>For conversations on AI evaluation, agents, and spatial intelligence.</p></div>{email_link(esc(CONFIG['email']), 'contact-email')}</section>'''


def about() -> str:
    return f'''<section class="page-heading"><p class="eyebrow">A LITTLE CONTEXT</p><h1>About me<span class="name-period">.</span></h1><p class="page-lead">Building a clearer picture of what AI can do.</p></section>
    <div class="about-layout"><div class="about-prose prose"><p>I’m <strong>Jinglun Zhao</strong>. I work on automated evaluation of AI capabilities on the Agent Team at <strong>Moonshot AI (Kimi)</strong>.</p><p>I lead the design and development of evaluation systems that turn real-world user needs into evaluation protocols and capability metrics. Much of this work concerns open-ended tasks, where a model’s success cannot be established through a simple correctness check.</p><p>I also work on automated evaluation and analysis of out-of-distribution tasks beyond standard benchmarks, to better understand model strengths and failure modes in real-world settings.</p><p>My recent focus is on <strong>3D spatial understanding and generation</strong>, including 3D modeling, motion, skeletal rigging, rendering, and visual quality.</p><p>I earned my PhD from <strong>Tsinghua University’s Institute for Interdisciplinary Information Sciences (IIIS)</strong>, advised by <strong>Prof. Yi Wu</strong>. My published research includes <a href="{path('#research')}">AutoTruss (IJCAI 2023)</a>, where we combine search and reinforcement learning for physically constrained structural design.</p><div class="about-socials">{email_link('Email', 'text-link')}{external(CONFIG['scholar'], 'Google Scholar', 'text-link')}{external(CONFIG['github'], 'GitHub', 'text-link')}{external(CONFIG['linkedin'], 'LinkedIn', 'text-link')}</div></div>
    <aside class="background-panel" aria-labelledby="background-title"><img class="about-portrait" src="{asset('jinglun-zhao-headshot.jpg')}" alt="Portrait of Jinglun Zhao" width="400" height="400" loading="lazy"><h2 class="small-label" id="background-title">AT A GLANCE</h2><div class="background-item"><span class="small-label">NOW</span><h3>Moonshot AI · Kimi</h3><p>Agent Team<br>Automated AI evaluation</p></div><div class="background-item"><span class="small-label">EDUCATION</span><h3>Tsinghua University</h3><p>PhD, IIIS<br>Advised by Prof. Yi Wu</p></div><div class="background-item"><span class="small-label">INTERESTS</span><p>AI capability evaluation<br>Open-ended tasks<br>Out-of-distribution generalization<br>3D spatial intelligence</p></div></aside></div>
    <div class="about-bottom"><span class="small-label">THE THREAD THAT CONNECTS MY WORK</span><p>From real-world questions<br>to meaningful measurements.</p><a class="text-link" href="{path('#focus')}">Explore my focus <span aria-hidden="true">↗</span></a></div>'''


def writing_page(posts: list[dict]) -> str:
    if posts:
        listing = f'''<label class="search-label" for="post-search">Search the notebook</label><input id="post-search" class="post-search" type="search" placeholder="Search titles, topics, or keywords…" data-post-search><div class="post-list">{''.join(article_card(p) for p in posts)}</div><p class="search-empty" data-search-empty role="status" hidden>No notes match your search.</p>'''
    else:
        listing = '''<div class="writing-empty"><div class="notebook-drawing" aria-hidden="true"><svg viewBox="0 0 110 100" fill="none"><path d="M20 19h64l7 67H27z" stroke="currentColor" stroke-width="1.5"/><path d="M29 12h64l7 67H91M38 36h30M40 47h36M41 58h24" stroke="currentColor" stroke-width="1.5"/><path d="m64 75 28-41 6 4-28 41-8 5z" fill="#f8f7f2" stroke="currentColor" stroke-width="1.5"/></svg></div><h2>A notebook, taking shape.</h2><p>This is where I’ll share notes on AI evaluation, agents, and spatial intelligence. New writing will appear here.</p></div>'''
    return f'''<section class="page-heading writing-heading"><p class="eyebrow">NOTES, QUESTIONS & WORKING IDEAS</p><h1>Writing<span class="name-period">.</span></h1><p class="page-lead">Thinking through how we measure AI.</p><p class="page-description">Research notes and longer-form essays on evaluation, agents, and spatial intelligence.</p></section><section class="notebook-content" aria-label="Research notes">{listing}</section><div class="writing-footer"><span>Prefer to follow along?</span><a class="text-link" href="{path('feed.xml')}">Subscribe via RSS <span aria-hidden="true">↗</span></a></div>'''


def read_posts() -> list[dict]:
    posts = []
    for source in sorted((ROOT / "content" / "posts").glob("*.md")):
        if source.stem.startswith("_"):
            continue
        text = source.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", text, re.S)
        if not match:
            raise ValueError(f"Missing metadata in {source.name}; copy content/posts/_template.md")
        meta = {}
        for line in match[1].splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, separator, value = line.partition(":")
                if not separator:
                    raise ValueError(f"Invalid metadata line in {source.name}: {line}")
                meta[key.strip()] = value.strip()
        draft = meta.get("draft", "true").lower()
        if draft not in {"true", "false"}:
            raise ValueError(f"draft must be true or false in {source.name}")
        if draft == "true":
            continue
        for required in ["title", "date", "summary"]:
            if not meta.get(required):
                raise ValueError(f"Missing {required} in {source.name}")
        published = date.fromisoformat(meta["date"])
        if published > TODAY:
            continue
        slug = source.stem
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Use lowercase words separated by hyphens for {source.name}")
        tokens = MD.parse(match[2])
        headings = []
        seen = {}
        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                if token.tag == "h1":
                    raise ValueError(f"Use ## for article sections in {source.name}; the title is already the h1")
                label = tokens[i + 1].content
                base = re.sub(r"[^\w-]+", "-", label.lower()).strip("-") or "section"
                seen[base] = seen.get(base, 0) + 1
                identifier = base if seen[base] == 1 else f"{base}-{seen[base]}"
                token.attrSet("id", identifier)
                if token.tag == "h2":
                    headings.append((identifier, label))
        plain_text = " ".join(token.content for token in tokens if token.type in {"inline", "fence"})
        posts.append({"title": meta["title"], "summary": meta["summary"], "date": published, "slug": slug,
                      "tags": [tag.strip() for tag in meta.get("tags", "").split(",") if tag.strip()],
                      "html": MD.renderer.render(tokens, MD.options, {}), "headings": headings,
                      "minutes": max(1, math.ceil(len(plain_text.split()) / 220))})
    return sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)


def post_page(post: dict) -> str:
    toc = "".join(f'<a href="#{esc(identifier)}">{esc(label)}</a>' for identifier, label in post["headings"])
    aside = f'<aside class="article-toc" aria-label="On this page"><p class="small-label">ON THIS PAGE</p>{toc}</aside>' if toc else ""
    return f'''<article class="article-page"><header class="article-heading"><a class="back-link" href="{path('writing/')}">← All writing</a><div class="post-meta"><time datetime="{post['date'].isoformat()}">{post['date'].strftime('%B %d, %Y')}</time><span>{post['minutes']} min read</span></div><h1>{esc(post['title'])}</h1><p class="page-lead">{esc(post['summary'])}</p><div class="tags">{''.join(f'<span>{esc(t)}</span>' for t in post['tags'])}</div></header><div class="article-layout"><div class="prose article-body">{post['html']}</div>{aside}</div><footer class="article-footer"><a class="text-link" href="{path('writing/')}">← Back to the notebook</a>{external(CONFIG['linkedin'], 'Discuss on LinkedIn', 'text-link')}</footer></article>'''


def feeds(posts: list[dict]) -> None:
    updated = posts[0]["date"].isoformat() + "T00:00:00Z" if posts else "2026-11-01T00:00:00Z"
    entries = []
    for post in posts:
        url = SITE_URL + "/writing/" + post["slug"] + "/"
        entries.append(f'''<entry><id>{xml_escape(url)}</id><title>{xml_escape(post['title'])}</title><link href="{esc(url)}"/><updated>{post['date'].isoformat()}T00:00:00Z</updated><summary>{xml_escape(post['summary'])}</summary><content type="html">{xml_escape(post['html'])}</content></entry>''')
    write("feed.xml", f'''<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><id>{xml_escape(SITE_URL)}/writing/</id><title>Jinglun Zhao — Writing</title><link href="{esc(SITE_URL)}/feed.xml" rel="self"/><link href="{esc(SITE_URL)}/writing/"/><updated>{updated}</updated><author><name>Jinglun Zhao</name></author>{''.join(entries)}</feed>''')
    routes = ["", "about/", "writing/"] + ["writing/" + p["slug"] + "/" for p in posts]
    write("sitemap.xml", '<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f'<url><loc>{xml_escape(SITE_URL + "/" + route)}</loc></url>' for route in routes) + "</urlset>")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")


def main() -> None:
    # Validate source before replacing the generated output.
    posts = read_posts()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    for publication in PUBLICATIONS:
        authors = " and ".join(publication["authors"])
        citation = f"@inproceedings{{{publication['slug']}{publication['year']},\n  title = {{{publication['title']}}},\n  author = {{{authors}}},\n  booktitle = {{Proceedings of {publication['venue']}}},\n  year = {{{publication['year']}}},\n  url = {{{publication['paper']}}}\n}}\n"
        write("publications/" + publication["slug"] + ".bib", citation)
    write("index.html", page("", home(posts)))
    write("about/index.html", page("About", about(), "about/", "about"))
    write("writing/index.html", page("Writing", writing_page(posts), "writing/", "writing"))
    for post in posts:
        route = "writing/" + post["slug"] + "/"
        write(route + "index.html", page(post["title"], post_page(post), route, "writing", post["summary"], post))
    write("404.html", page("Page not found", f'<section class="not-found"><p class="eyebrow">404 / A SMALL DETOUR</p><h1>This page wandered off.</h1><p>The address may have changed, or the page doesn’t exist yet.</p><a class="button button-primary" href="{path()}">Back to the homepage <span aria-hidden="true">↗</span></a></section>', "404.html", ""))
    write(".nojekyll", "")
    feeds(posts)
    print(f"Built {len(posts) + 4} pages with {len(posts)} published article(s) → {OUT}")


if __name__ == "__main__":
    main()
