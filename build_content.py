# -*- coding: utf-8 -*-
"""Build blog/ and projects/ static pages from Markdown sources.

Reads content/blog/*.md and content/projects/*.md (each with ---frontmatter---),
converts the body to HTML via mistune, and renders through a shared template that
matches the hand-authored editorial pages (same nav, fonts, css/style.css).

Usage:  python build_content.py
Output: blog/index.html, blog/<slug>.html, projects/index.html, projects/<slug>.html
"""
import json
import os
import re
import html as html_mod

import mistune

ROOT = os.path.dirname(os.path.abspath(__file__))

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ----------------------------------------------------------------------------
# frontmatter + markdown
# ----------------------------------------------------------------------------

def parse_frontmatter(text):
    """Return (meta dict, body string) for a --- delimited frontmatter block."""
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    block, body = m.group(1), text[m.end():]
    meta = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    # comma lists -> lists
    for k in ("tags", "papers"):
        if k in meta:
            meta[k] = [x.strip() for x in meta[k].split(",") if x.strip()]
    return meta, body


def md_to_html(md_text):
    """Convert markdown body to HTML via mistune (GFM-ish)."""
    md = mistune.create_markdown(escape=False, hard_wrap=False)
    return md(md_text)


# ----------------------------------------------------------------------------
# small rendering helpers
# ----------------------------------------------------------------------------

def fmt_date(iso):
    """2026-04-07 -> '7 Apr 2026'."""
    try:
        y, m, d = iso.split("-")
        return f"{int(d)} {MONTHS[int(m) - 1]} {y}"
    except Exception:
        return iso


def month_label(iso):
    """2026-04 -> 'Apr 2026' for project periods."""
    try:
        y, m = iso.split("-")[:2]
        return f"{MONTHS[int(m) - 1]} {y}"
    except Exception:
        return iso


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s


# ----------------------------------------------------------------------------
# shared HTML skeleton (matches editorial style.css)
# ----------------------------------------------------------------------------

def nav_html(active):
    items = [
        ("../index.html", "Home", "Home"),
        ("../about.html", "About", "About"),
        ("../publications.html", "Publications", "Publications"),
        ("../projects/index.html", "Projects", "Projects"),
        ("../blog/index.html", "Blog", "Blog"),
        ("../news.html", "News", "News"),
    ]
    return "".join(
        f'<li><a href="{href}"' + (f' class="active"' if key == active else "") +
        f">{label}</a></li>\n      "
        for href, label, key in items
    ).rstrip(" \n")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600&family=Noto+Serif+SC:wght@400;500;600&family=Noto+Sans+SC:wght@400;500&display=swap" rel="stylesheet">')


def page(title, desc, body, active, prev=""):
    """Full HTML page. `active` = nav item to highlight ("" = none)."""
    nav = nav_html(active)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_mod.escape(title)} — Jianghao Wang</title>
<meta name="description" content="{html_mod.escape(desc)}">
<link rel="canonical" href="https://jianghao.wang/">
<link rel="icon" href="../img/icon.png">
<link rel="apple-touch-icon" href="../img/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="../css/style.css">
</head>
<body>

<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="../index.html">Jianghao Wang</a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span></button>
    <ul class="nav-links" id="navLinks">
{nav}
    </ul>
  </div>
</header>

{body}

<footer class="site-footer">
  <div class="wrap footer-bottom">
    <span>© <span id="yr"></span> Jianghao Wang. All rights reserved.</span>
    <span>Built with static HTML · Hosted on GitHub Pages</span>
  </div>
</footer>

<script src="../js/main.js"></script>
</body>
</html>
"""


def cover_img(meta, base="..", wrap=None):
    """Optional cover image markup if meta['image'] set. If `wrap` is a URL the
    whole image becomes a link (with an ↗ affordance) to that external URL."""
    slug = meta.get("image")
    if not slug:
        return ""
    inner = ('<div class="post-cover"><picture>'
             f'<source srcset="{base}/img/{slug}.webp" type="image/webp">'
             f'<img src="{base}/img/{slug}.png" alt="" loading="lazy" width="960" height="544">'
             "</picture></div>")
    if not wrap:
        return inner
    return (f'<a class="cover-link" href="{wrap}" target="_blank" rel="noopener">'
            + inner + '<span class="cover-open" aria-hidden="true">' + EXT_SVG + '</span></a>')


# ----------------------------------------------------------------------------
# blog
# ----------------------------------------------------------------------------

def build_blog():
    src_dir = os.path.join(ROOT, "content", "blog")
    out_dir = os.path.join(ROOT, "blog")
    os.makedirs(out_dir, exist_ok=True)
    posts = []

    for fn in sorted(os.listdir(src_dir)):
        if not fn.endswith(".md"):
            continue
        meta, body = parse_frontmatter(open(os.path.join(src_dir, fn), encoding="utf-8").read())
        if "slug" not in meta:
            meta["slug"] = slugify(fn[:-3].split("-", 1)[-1])
        posts.append((meta, body))

    posts.sort(key=lambda p: p[0].get("date", ""), reverse=True)

    # ---- individual post pages ----
    for meta, body in posts:
        html_body = md_to_html(body)
        title = meta.get("title", "Post")
        lang = "en"
        head = f"""<section class="section" style="padding-bottom:0">
  <div class="wrap" style="max-width:760px">
    <p class="eyebrow">Blog · {fmt_date(meta.get('date',''))}</p>
    <h1 class="post-title">{html_mod.escape(title)}</h1>
    {('<p class="post-title-zh">' + html_mod.escape(meta['title_zh']) + '</p>') if meta.get('title_zh') else ''}
    <p class="muted" style="margin-top:.4rem">{html_mod.escape(meta.get('summary',''))}
      {'<br>' + html_mod.escape(meta['summary_zh']) if meta.get('summary_zh') else ''}</p>
  </div>
</section>
<section class="section" style="padding-top:1.5rem">
  <div class="wrap" style="max-width:760px">
    {cover_img(meta)}
    <article class="prose post-body">{html_body}</article>
    <p class="muted" style="margin-top:3rem;font-size:.85rem"><a class="link-arrow" href="index.html">← Back to blog
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M11 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a></p>
  </div>
</section>"""
        open(os.path.join(out_dir, meta["slug"] + ".html"), "w", encoding="utf-8").write(
            page(title, meta.get("summary", title), head, "Blog"))

    # ---- blog index ----
    rows = []
    for meta, body in posts:
        rows.append(f"""<article class="toc-row">
  <span class="toc-num"></span>
  <div class="toc-thumb">{cover_img(meta, base="..").replace('<div class="post-cover">','').replace('</div>','') if meta.get('image') else '<span style="display:block;width:100%;height:100%;background:var(--teal-100)"></span>'}</div>
  <div class="toc-body">
    <h3><a href="{meta['slug']}.html">{html_mod.escape(meta.get('title',''))}</a></h3>
    <p class="authors">{html_mod.escape(meta.get('summary',''))}
      {' · ' + html_mod.escape(meta['summary_zh']) if meta.get('summary_zh') else ''}</p>
    <div class="toc-meta"><span class="venue">{fmt_date(meta.get('date',''))}</span>{''.join('<span>'+html_mod.escape(t)+'</span>' for t in meta.get('tags',[]))}</div>
  </div>
</article>""")
    body = f"""<section class="section" style="padding-bottom:0">
  <div class="wrap">
    <p class="eyebrow">Blog</p>
    <h1 style="font-family:var(--font-display);font-weight:500;font-size:clamp(2rem,5vw,3.2rem);margin:0 0 .6rem">Notes &amp; essays</h1>
    <p class="muted" style="max-width:60ch;margin:0">Occasional writing on geospatial big data, human behaviour, and geography of the digital age.</p>
  </div>
</section>
<section class="section" style="padding-top:1.5rem">
  <div class="wrap" style="max-width:860px">
    <div class="toc">{''.join(rows)}</div>
  </div>
</section>"""
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(
        page("Blog", "Notes and essays by Jianghao Wang", body, "Blog"))


# ----------------------------------------------------------------------------
# projects
# ----------------------------------------------------------------------------

STATUS_LABEL = {"completed": "Completed", "ongoing": "Ongoing"}

# small up-right-arrow icon reused for external-demo links (list cards + detail titles)
EXT_SVG = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
           '<path d="M7 17L17 7M17 7H7M17 7v10" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')
BIG_SVG = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
           '<path d="M7 17L17 7M17 7H7M17 7v10" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def paper_cards(dois):
    """Render representative-publication cards (thumbnail + title link + journal/year)
    for the DOIs listed in a project's frontmatter, using data/publications.json."""
    if not dois:
        return ""
    try:
        pubs = json.load(open(os.path.join(ROOT, "data", "publications.json"), encoding="utf-8"))
        by_doi = {p.get("doi"): p for p in pubs if p.get("doi")}
    except Exception:
        return ""
    rows = []
    for i, doi in enumerate(dois, 1):
        e = by_doi.get(doi)
        if not e:
            continue
        title = html_mod.escape(e.get("title", ""))
        url = "https://doi.org/" + e["doi"]
        journal = html_mod.escape(e.get("journal", ""))
        year = html_mod.escape(e.get("year", ""))
        img = e.get("image")
        if img:
            thumb = (f'<div class="toc-thumb"><picture>'
                     f'<source srcset="../img/{img}.webp" type="image/webp">'
                     f'<img src="../img/{img}.png" alt="" loading="lazy" width="180" height="113">'
                     f'</picture></div>')
        else:
            thumb = '<div class="toc-thumb"><span style="display:block;width:100%;height:100%;background:var(--teal-100)"></span></div>'
        rows.append(
            f'<article class="toc-row">'
            f'<span class="toc-num">{i:02d}</span>{thumb}'
            f'<div class="toc-body"><h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>'
            f'<div class="toc-meta"><span class="venue">{journal}</span><span>{year}</span></div>'
            f'</div></article>')
    if not rows:
        return ""
    return ('<h2 class="post-h2">Representative publications</h2>'
            f'<div class="toc" style="max-width:760px">{"".join(rows)}</div>')


def build_projects():
    src_dir = os.path.join(ROOT, "content", "projects")
    out_dir = os.path.join(ROOT, "projects")
    os.makedirs(out_dir, exist_ok=True)
    projects = []

    for fn in sorted(os.listdir(src_dir)):
        if not fn.endswith(".md"):
            continue
        meta, body = parse_frontmatter(open(os.path.join(src_dir, fn), encoding="utf-8").read())
        if "slug" not in meta:
            meta["slug"] = slugify(fn[:-3])
        projects.append((meta, body))

    projects.sort(key=lambda p: p[0].get("year", ""), reverse=True)

    # ---- detail pages ----
    for meta, body in projects:
        html_body = md_to_html(body)
        title = meta.get("title", "Project")
        status = STATUS_LABEL.get(meta.get("status", ""), meta.get("status", ""))
        link = meta.get("link")
        if link:
            link_esc = html_mod.escape(link)
            title_html = (f'<a class="title-ext" href="{link_esc}" target="_blank" rel="noopener">'
                          f'{html_mod.escape(title)} {BIG_SVG}</a>')
            cover = cover_img(meta, wrap=link_esc)
        else:
            title_html = html_mod.escape(title)
            cover = cover_img(meta)
        head = f"""<section class="section" style="padding-bottom:0">
  <div class="wrap" style="max-width:760px">
    <p class="eyebrow">Project · {html_mod.escape(meta.get('period') or meta.get('year') or '')}</p>
    <h1 class="post-title">{title_html}</h1>
    {('<p class="post-title-zh">' + html_mod.escape(meta['title_zh']) + '</p>') if meta.get('title_zh') else ''}
    <div class="project-meta">
      {f'<span class="toc-meta"><span class="venue">{status}</span><span>{html_mod.escape(meta.get("period",""))}</span></span>' if status else ''}
      {f'<a class="link-arrow" style="font-size:.9rem" href="{html_mod.escape(meta["link"])}" target="_blank" rel="noopener">Link ↗</a>' if meta.get("link") else ''}
    </div>
    <p class="muted" style="margin-top:.4rem">{html_mod.escape(meta.get('summary',''))}
      {'<br>' + html_mod.escape(meta['summary_zh']) if meta.get('summary_zh') else ''}</p>
  </div>
</section>
<section class="section" style="padding-top:1.5rem">
  <div class="wrap" style="max-width:760px">
    {cover}
    <article class="prose post-body">{html_body}</article>
    {paper_cards(meta.get("papers"))}
    <p class="muted" style="margin-top:3rem;font-size:.85rem"><a class="link-arrow" href="index.html">← Back to projects
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M11 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a></p>
  </div>
</section>"""
        open(os.path.join(out_dir, meta["slug"] + ".html"), "w", encoding="utf-8").write(
            page(title, meta.get("summary", title), head, "Projects"))

    # ---- projects index (grouped by category) ----
    def single_year(meta):
        """True if the project spans a single year (period is a bare 4-digit year)."""
        return bool(re.fullmatch(r"\d{4}", (meta.get("period", "") or "").strip()))

    def card_html(meta):
        """One project card. When the project has an external `link`, the cover
        and the title open that demo (new tab) and a 'Project details' link keeps
        access to the detail page; otherwise the whole card links to the detail page."""
        status = STATUS_LABEL.get(meta.get("status", ""), meta.get("status", ""))
        year_badge = (f'<span class="project-year">{html_mod.escape(meta.get("year",""))}</span>'
                      if single_year(meta) else '')
        title = html_mod.escape(meta.get('title', ''))
        slug = meta['slug']
        link = meta.get('link')
        zh = ((f'<p class="post-title-zh" style="font-size:1rem;margin:0 0 .4rem">'
               + html_mod.escape(meta['title_zh']) + '</p>') if meta.get('title_zh') else '')
        summary = (f'<p class="authors">{html_mod.escape(meta.get("summary",""))}'
                   + (f' · {html_mod.escape(meta["summary_zh"])}' if meta.get('summary_zh') else '')
                   + '</p>')
        meta_inner = ((f'<span class="venue">{status}</span>' if status else '')
                      + f'<span>{html_mod.escape(meta.get("period",""))}</span>')

        if not link:
            return (f'<a class="project-card" href="{slug}.html">{cover_img(meta)}'
                    f'<div class="project-card-body"><div class="project-card-top">'
                    f'<h3>{title}</h3>{year_badge}</div>{zh}{summary}'
                    f'<div class="toc-meta" style="margin-top:.5rem">{meta_inner}</div>'
                    f'</div></a>')

        link_esc = html_mod.escape(link)
        cover = cover_img(meta, wrap=link_esc)
        h3 = (f'<h3><a class="card-title-ext" href="{link_esc}" target="_blank" rel="noopener">'
              f'{title} {EXT_SVG}</a></h3>')
        details = f'<a class="card-details" href="{slug}.html">Project details {EXT_SVG}</a>'
        return (f'<div class="project-card">{cover}'
                f'<div class="project-card-body"><div class="project-card-top">{h3}{year_badge}</div>'
                f'{zh}{summary}'
                f'<div class="card-foot"><div class="toc-meta">{meta_inner}</div>{details}</div>'
                f'</div></div>')

    CATEGORY_ORDER = ["Ongoing", "Research", "Review", "Vibe Coding"]
    CATEGORY_TAGLINE = {
        "Ongoing": "Active research efforts",
        "Research": "Research programmes",
        "Review": "Large-scale reviews",
        "Vibe Coding": "Coding for the joy of it",
    }
    by_cat = {}
    for meta, body in projects:
        by_cat.setdefault(meta.get("category", "Research"), []).append(meta)

    blocks = []
    for cat in CATEGORY_ORDER:
        metas = by_cat.get(cat)
        if not metas:
            continue
        metas.sort(key=lambda m: (int(m.get("order", 999)), -(int(m.get("year") or 0))))
        cards = "".join(card_html(m) for m in metas)
        tag = CATEGORY_TAGLINE.get(cat, "")
        blocks.append(
            f'<h2 class="project-cat-head">{html_mod.escape(cat)}</h2>'
            f'{f"<p class=\"muted\" style=\"margin:0 0 1.2rem\">{html_mod.escape(tag)}</p>" if tag else ""}'
            f'<div class="project-grid">{cards}</div>'
            f'<div style="height:2.6rem"></div>')

    body = f"""<section class="section" style="padding-bottom:0">
  <div class="wrap">
    <p class="eyebrow">Projects</p>
    <h1 style="font-family:var(--font-display);font-weight:500;font-size:clamp(2rem,5vw,3.2rem);margin:0 0 .6rem">Selected projects</h1>
    <p class="muted" style="max-width:60ch;margin:0">Research projects, large-scale reviews, and code — grouped by what they are.</p>
  </div>
</section>
<section class="section" style="padding-top:1.5rem">
  <div class="wrap">
    {''.join(blocks)}
  </div>
</section>"""
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(
        page("Projects", "Selected projects by Jianghao Wang", body, "Projects"))


if __name__ == "__main__":
    build_blog()
    build_projects()
    print("blog/index.html + posts written")
    print("projects/index.html + detail pages written")
