#!/usr/bin/env python3
"""Exports ONE screen of the prototype (screens/app.html) as a standalone, self-contained HTML file.

    python3 scripts/export-screen.py welcome 01-welcome

The file embeds the design tokens, the screen's CSS, the Inter font and every image as data URIs,
so it opens on its own (no server, no internet). Output: screens/html/<name>.html

Only static screens are supported for now; screens that are built by the prototype script
(Home list, Calendar, Review, Push) need their own static render and are added one at a time.
"""
import base64, mimetypes, os, re, sys, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP = os.path.join(ROOT, 'screens', 'app.html')
TOKENS = os.path.join(ROOT, 'src', 'styles', 'tokens.css')
OUT_DIR = os.path.join(ROOT, 'screens', 'html')
FONT_CSS = 'https://fonts.googleapis.com/css2?family=Inter:wght@400..900&display=swap'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def inter_font_face():
    """Latin subset of Inter (variable, weights 400-900) as an embedded @font-face."""
    req = urllib.request.Request(FONT_CSS, headers={'User-Agent': UA})
    css = urllib.request.urlopen(req).read().decode()
    block = re.search(r'/\* latin \*/\s*(@font-face\s*\{.*?\})', css, re.S).group(1)
    url = re.search(r'url\((https:[^)]+)\)', block).group(1)
    woff = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA})).read()
    block = block.replace(url, 'data:font/woff2;base64,' + base64.b64encode(woff).decode())
    return block


def main(screen_id, name):
    app = open(APP, encoding='utf-8').read()
    css = re.search(r'<style>(.*?)</style>', app, re.S).group(1)
    m = re.search(r'<main class="screen" id="%s"[^>]*>.*?</main>' % re.escape(screen_id), app, re.S)
    if not m:
        sys.exit(f'No screen with id "{screen_id}" in screens/app.html')
    main_html = re.sub(r'\s+hidden(?=[\s>])', '', m.group(0), count=1)

    # images -> data URIs
    def embed(match):
        rel = match.group(1)
        path = os.path.normpath(os.path.join(os.path.dirname(APP), rel))
        return 'src="%s"' % data_uri(path)
    main_html = re.sub(r'src="(\.\./assets/[^"]+)"', embed, main_html)
    if '../' in main_html:
        sys.exit('A relative path is left in the screen markup; embed it first.')

    tokens = open(TOKENS, encoding='utf-8').read()
    tokens = re.sub(r"@import url\([^)]*\);\n?", '', tokens)          # the font is embedded instead

    title = {'welcome': 'Welcome'}.get(screen_id, screen_id)
    html = f'''<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>nahadayka — {title}</title>
<style>
{inter_font_face()}
{tokens}
{css}
</style>
</head>
<body>

{main_html}

<script>
  // Scale the 440 x 956 design to the real screen width.
  function fit() {{
    document.querySelectorAll('.screen').forEach(function (screen) {{
      screen.querySelector('.stage').style.setProperty('--s', screen.clientWidth / 440);
    }});
  }}
  addEventListener('resize', fit);
  fit();
</script>
</body>
</html>
'''
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, name + '.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('wrote', os.path.relpath(out, ROOT), f'({len(html) // 1024} KB)')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
