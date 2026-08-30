---
title: Building a research website that ages well
title_zh: 打造一个历久弥新的个人学术网站
date: 2026-08-30
summary: Why I rebuilt this site as a zero-build, hand-authored static site — and how the blog pipeline works.
summary_zh: 为什么我选择用零构建的静态页面来重建个人网站，以及这套博客工作流是如何运转的。
tags: web, science
image: theme-ai
---

This site runs on a deliberately simple stack: hand-written HTML, one stylesheet, and
a small Python script that turns Markdown into pages. No framework, no build step, no
JavaScript at runtime beyond a menu toggle.

For an academic website, that trade is a good one. The site has to stay online for years
with minimal maintenance, load fast for readers everywhere, and survive whatever happens
to the underlying tools. Static HTML checks all three boxes.

## How the blog works

Every post lives as a Markdown file in `content/blog/`, with a small frontmatter block
for the title, date and summary:

```
---
title: Building a research website that ages well
date: 2026-08-30
tags: web, science
---
```

Running one command rebuilds the blog listing and each article page:

```bash
python build_content.py
```

The generated pages embed the same editorial layout as the rest of the site — serif
display type, teal and terracotta accents, generous whitespace — so articles feel like
part of the same publication rather than an afterthought.

## Why bother

Academic work is full of fast-changing tooling, but a personal site is closer to a
book than to an app. Books don't need to be recompiled every time the ecosystem moves;
they need to keep being readable. A static site built on Markdown gets you the same
kind of durability, plus the ability to write in plain text anywhere and keep every
version in Git.

The result is something I can maintain in an afternoon and that will still render
correctly ten years from now.
