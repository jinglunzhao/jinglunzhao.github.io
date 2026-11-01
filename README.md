# Jinglun Zhao — personal website

An English research homepage and Markdown notebook, designed for the GitHub Pages
repository **`jinglunzhao/jinglunzhao.github.io`**.

中文发布与更新指南：[DEPLOY.zh-CN.md](DEPLOY.zh-CN.md)。

The homepage and blog are one site. GitHub hosts the source and publishes the
generated HTML for free. The intended public address is
**https://jinglunzhao.github.io/**, once you deploy it.

## Preview locally

Requires Python 3.10 or later.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python build.py
python check.py
python -m http.server 8765 --bind 127.0.0.1 --directory _site
```

Open http://127.0.0.1:8765/. After editing content or CSS, run `python build.py`
again and refresh the browser.

## Deploy to GitHub Pages

1. Sign in to the **jinglunzhao** GitHub account.
2. Create a public repository named **jinglunzhao.github.io**. Do not initialize
   it with another README.
3. Upload the contents of this folder, including `.github/workflows/pages.yml`,
   to the `main` branch. You can use Git or GitHub's file uploader. If using Git:

   ```sh
   git init -b main
   git add .
   git commit -m "Add personal website and research notebook"
   git remote add origin https://github.com/jinglunzhao/jinglunzhao.github.io.git
   git push -u origin main
   ```

4. In the repository, open **Settings → Pages → Build and deployment → Source**
   and select **GitHub Actions**.
5. Open the **Actions** tab. If the initial workflow did not run successfully
   before Pages was enabled, select **Build and deploy website → Run workflow**.
6. After the deployment completes, visit https://jinglunzhao.github.io/.

This local project has not been published merely by creating these files.

## Publish an article

Copy `content/posts/_template.md` to a filename such as
`content/posts/evaluating-open-ended-tasks.md`. Edit its metadata and body:

```md
---
title: Evaluating open-ended tasks
date: 2026-11-01
summary: A concrete question and a useful takeaway for the reader.
tags: Evaluation, Agents
draft: false
---

Start your article here.

## A section heading

Write in Markdown. Use links, images, lists, tables, and fenced code blocks.
```

- Explicitly set `draft: false` to publish. Omitted or true values stay private
  from the generated website. Draft source files in a public repository are
  still public; keep confidential writing out of the repository entirely.
- Files beginning with `_` are always excluded.
- Future-dated posts appear only after a build on or after that date (UTC).
- Filenames become permanent URLs; use lowercase words and hyphens.
- The article title is automatically the `h1`; use `##` for main sections.
- Article metadata uses simple, single-line `key: value` fields, rather than
  full YAML. Do not wrap values in quotation marks or use multiline YAML.
- Put article images in `assets/` and reference them as `/assets/filename.png`.
- Drafts are excluded from HTML, search, the RSS feed, and the sitemap.
- Each published article gets a reading time and an automatic table of contents.
- Pushing a new article to `main` automatically rebuilds and deploys the site.

## Edit the site

- **Profile links, email, portrait filename, and site address:** `site.json`.
- **Homepage and About text:** `home()` and `about()` in `build.py`.
- **Selected publications:** `content/publications.json`.
- **Appearance and responsive layouts:** `assets/site.css`.
- **Mobile navigation and article search:** `assets/site.js`.
- **Browser icon and social artwork:** `assets/favicon.svg`, `assets/social.svg`, and `assets/social.png`.
- **Deployment:** `.github/workflows/pages.yml`.

The site uses no external fonts, analytics, cookies, or client-side framework.
Its core content and navigation work without JavaScript. JavaScript adds a
compact mobile navigation menu and search when articles have been published.

## Content notes

The first version uses the professional background provided by Jinglun and the
public description of the AI Grading System GitHub repository. The selected AutoTruss paper
(IJCAI 2023) and its equal-contribution statement were verified against
https://arxiv.org/abs/2306.15182 and https://arxiv.org/html/2306.15182v1.
The supplied Google Scholar profile is linked; the service blocked automated
access during preparation, so the selected research is not a complete publication
list. The site does not invent publications,
employment dates, benchmark scores, or blog posts. The portrait and public contact email were supplied by Jinglun. The photograph
is stored at `assets/jinglun-zhao.jpg`; the cropped, shoulder-up profile image is
at `assets/jinglun-zhao-headshot.jpg`. The homepage uses a small profile image
alongside the bio and retains the spatial geometry illustration as its main visual. No graduation date or CV was supplied.

The homepage puts the current role, PhD background, research summary, and profile
links first. Three concise research areas are followed by selected publications
(including an explicit co-first-author label), code, and writing. The writing
preview stays compact until articles are published.
