#!/usr/bin/env python3
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / 'content' / 'projects'
OUT = ROOT / 'projects'


def inline_md(text: str) -> str:
    slots = []

    def stash(value: str) -> str:
        slots.append(value)
        return f'\x00{len(slots)-1}\x00'

    text = re.sub(
        r'!\[([^\]]*)\]\(([^)]+)\)',
        lambda m: stash(
            f'<img src="{html.escape(m.group(2), quote=True)}" '
            f'alt="{html.escape(m.group(1), quote=True)}">'
        ),
        text,
    )
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        lambda m: stash(
            f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'
        ),
        text,
    )
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', lambda m: stash(f'<code>{m.group(1)}</code>'), text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: slots[int(m.group(1))], text)


def markdown_to_html(md: str) -> str:
    lines = md.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out = []
    i = 0
    in_ul = False
    in_ol = False
    in_code = False
    code_lines = []
    code_lang = ''

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append('</ul>')
            in_ul = False
        if in_ol:
            out.append('</ol>')
            in_ol = False

    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            if in_code:
                lang = html.escape(code_lang, quote=True)
                klass = f' class="language-{lang}"' if code_lang else ''
                out.append(
                    f'<pre><code{klass}>'
                    f'{html.escape(chr(10).join(code_lines))}'
                    '</code></pre>'
                )
                code_lines = []
                code_lang = ''
                in_code = False
            else:
                close_lists()
                in_code = True
                code_lang = line[3:].strip()
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if not line.strip():
            close_lists()
            i += 1
            continue
        if line.startswith('### '):
            close_lists()
            out.append(f'<h3>{inline_md(line[4:])}</h3>')
        elif line.startswith('## '):
            close_lists()
            out.append(f'<h2>{inline_md(line[3:])}</h2>')
        elif line.startswith('# '):
            close_lists()
            out.append(f'<h1>{inline_md(line[2:])}</h1>')
        elif re.match(r'^\s*[-*] ', line):
            if not in_ul:
                close_lists()
                out.append('<ul>')
                in_ul = True
            item = re.sub(r'^\s*[-*] ', '', line)
            out.append(f'<li>{inline_md(item)}</li>')
        elif re.match(r'^\s*\d+\. ', line):
            if not in_ol:
                close_lists()
                out.append('<ol>')
                in_ol = True
            item = re.sub(r'^\s*\d+\. ', '', line)
            out.append(f'<li>{inline_md(item)}</li>')
        elif line.startswith('> '):
            close_lists()
            out.append(f'<blockquote><p>{inline_md(line[2:])}</p></blockquote>')
        elif line.startswith('---'):
            close_lists()
            out.append('<hr>')
        else:
            parts = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not re.match(
                r'^(# |## |### |```|> |\s*[-*] |\s*\d+\. |---)', lines[j]
            ):
                parts.append(lines[j])
                j += 1
            out.append(f'<p>{inline_md(" ".join(parts))}</p>')
            i = j - 1
        i += 1

    close_lists()
    if in_code:
        out.append(f'<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>')
    return '\n'.join(out)


def parse_frontmatter(raw: str):
    if not raw.startswith('---\n'):
        return {}, raw
    _, front, body = raw.split('---\n', 2)
    meta = {}
    for line in front.splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            meta[key.strip()] = value.strip()
    return meta, body


def page_for(meta: dict, markdown: str) -> str:
    title = meta.get('title', 'Project')
    slug = meta.get('slug', 'project')
    tag = meta.get('tag', 'Project')
    summary = meta.get('summary', '')
    repo = meta.get('repo', '')
    canonical = f'https://cooper-src.github.io/projects/{slug}.html'
    schema_data = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': f'{title} | Cooper', 'url': canonical, 'description': summary}
    if repo:
        schema_data['@type'] = 'SoftwareSourceCode'
        schema_data['codeRepository'] = repo
    schema = json.dumps(schema_data, ensure_ascii=False)
    actions = ''
    if repo:
        actions += (
            f'<a class="button button-primary" href="{html.escape(repo, quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">View source</a>'
        )
    actions += '<a class="button button-secondary" href="../projects.html">All projects</a>'

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | Cooper</title>
<meta name="description" content="{html.escape(summary, quote=True)}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/site.css">
<script type="application/ld+json">{schema}</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="../index.html">COOPER</a>
<nav class="site-nav" aria-label="Primary navigation">
<a href="../projects.html" aria-current="page">Projects</a>
<a href="../about.html">About</a>
<a href="../resume.html">Resume</a>
<a href="../contact.html">Contact</a>
</nav></div></header>
<main id="main">
<section class="page"><div class="container">
<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="../index.html">Home</a><span>/</span><a href="../projects.html">Projects</a><span>/</span><span aria-current="page">{html.escape(title)}</span>
</nav>
<header class="page-header">
<p class="eyebrow">{html.escape(tag)}</p>
<h1>{html.escape(title)}</h1>
<p>{html.escape(summary)}</p>
<div class="actions">{actions}</div>
</header>
<article class="prose">{markdown_to_html(markdown)}</article>
</div></section>
</main>
<footer class="site-footer"><div class="container footer-inner"><p>© 2026 Cooper.</p>
<nav class="footer-nav" aria-label="Footer navigation">
<a href="../privacy.html">Privacy</a><a href="../terms.html">Terms</a><a href="../cookies.html">Cookies</a><a href="../refunds.html">Refunds</a>
</nav></div></footer>
</body></html>
'''


def main() -> None:
    OUT.mkdir(exist_ok=True)
    count = 0
    for source in sorted(PROJECTS.glob('*.md')):
        meta, body = parse_frontmatter(source.read_text(encoding='utf-8'))
        meta.setdefault('slug', source.stem)
        (OUT / f"{meta['slug']}.html").write_text(page_for(meta, body), encoding='utf-8')
        count += 1
    print(f'Built {count} project page(s).')


if __name__ == '__main__':
    main()
