#!/usr/bin/env python3
"""Builds the design system pages that GitHub shows, from the tokens and the prototype.

    python3 scripts/build-design-docs.py

Output:
  docs/design-system.md        tables of colours, components, typography and text styles
  docs/design-system/*.png     colour and type sheets (GitHub cannot show colour chips in Markdown)
  docs/screens/*.jpg           every screen state of screens/app.html

Run `npm run tokens` first if design/figma-variables.json changed. Needs Google Chrome and Pillow.
"""
import json, os, subprocess, tempfile
from PIL import Image, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOCS = os.path.join(ROOT, 'docs')
APP = os.path.join(ROOT, 'screens', 'app.html')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# file name, caption, route, script that brings the screen into the wanted state
SCREENS = [
    ('01-welcome', 'Welcome', '', ''),
    ('02-authorization', 'Create an account', '#auth', ''),
    ('03-setup', 'Permissions & child', '#setup', ''),
    ('04-home-empty', 'Home, empty', '#home', ''),
    ('05-home-tasks', 'Home, tasks', '#home-tasks', ''),
    ('06-quick-edit', 'Home, quick edit', '#home-tasks', "document.querySelector('#home-list .htask-row').click()"),
    ('07-listening', 'Listening', '#create',
     "stopListening(); document.getElementById('transcript').textContent = 'Teo has football every Monday\\nat 17:00'"),
    ('08-understands', 'AI understands', '#understand', ''),
    ('09-one-question', 'One question', '#understand-ask', ''),
    ('10-review', 'Review', '#review', ''),
    ('11-review-time', 'Start time', '#review', "document.querySelector('#review [data-field=when]').click()"),
    ('12-done', 'Done', '#done', ''),
    ('13-calendar', 'Calendar', '#calendar', ''),
    ('14-push', 'Push', '#push', ''),
    ('15-push-actions', 'Push, actions', '#push', 'toggleActions()'),
    ('16-log-in', 'Log in', '#login', ''),
]


def chrome(url, out, width, height, scale=1):
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([CHROME, '--headless=new', '--user-data-dir=' + profile, '--no-first-run', '--hide-scrollbars',
                        '--force-prefers-reduced-motion', f'--force-device-scale-factor={scale}',
                        f'--window-size={width},{height}', '--virtual-time-budget=8000', '--screenshot=' + out, url],
                       capture_output=True, timeout=120, check=True)


def screens():
    out = os.path.join(DOCS, 'screens')
    os.makedirs(out, exist_ok=True)
    app = open(APP, encoding='utf-8').read()
    app = app.replace('<head>', '<head>\n<base href="file://%s/">' % os.path.dirname(APP), 1)
    app = app.replace('const SILENCE_MS = 2500;', 'const SILENCE_MS = 999999;')
    for name, _, route, action in SCREENS:
        page = app.replace('</body>', '<script>location.hash = "%s"; route(); setTimeout(() => { %s }, 600);</script></body>' % (route, action))
        with tempfile.TemporaryDirectory() as tmp:
            html, png = os.path.join(tmp, 'page.html'), os.path.join(tmp, 'shot.png')
            open(html, 'w', encoding='utf-8').write(page)
            chrome('file://' + html, png, 600, 956)
            Image.open(png).convert('RGB').crop((80, 0, 520, 956)).save(os.path.join(out, name + '.jpg'), quality=84, optimize=True)
    return len(SCREENS)


def sheet(name, width, body):
    """renders an HTML sheet that uses the real tokens.css"""
    css = 'file://' + os.path.join(ROOT, 'src', 'styles', 'tokens.css')
    page = f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{css}">
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ width: {width}px; overflow: hidden; padding: 32px; font: var(--font-weight-medium) var(--font-size-12)/1.4 var(--font-family-sans); color: var(--neutral-900); background: var(--white); }}
  h2 {{ font: var(--font-weight-bold) var(--font-size-13)/1 var(--font-family-sans); text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px; }}
  .row {{ display: flex; gap: 8px; margin-bottom: 20px; }}
  .sw {{ width: 78px; }}
  .sw i {{ display: block; height: 56px; border-radius: var(--radius-md); border: 1px solid var(--neutral-200); }}
  .sw b {{ display: block; margin-top: 4px; font-weight: var(--font-weight-semibold); }}
  .sw span {{ color: var(--neutral-600); }}
  .blue {{ background: var(--screen-bg); color: var(--text-inverse); border-radius: var(--radius-xl); padding: 24px; }}
  .blue .sw {{ width: 108px; }} .blue .sw i {{ border: 0; }} .blue .sw span {{ color: var(--text-inverse-secondary); }}
  .type {{ display: flex; align-items: baseline; gap: 24px; padding: 10px 0; border-bottom: 1px solid var(--text-inverse-muted); }}
  .type small {{ width: 210px; flex: none; font-size: var(--font-size-12); }}
</style><body>{body}</body>'''
    with tempfile.TemporaryDirectory() as tmp:
        html = os.path.join(tmp, 'sheet.html')
        open(html, 'w', encoding='utf-8').write(page)
        out = os.path.join(DOCS, 'design-system', name)
        chrome('file://' + html, out, width, 2000, 2)
        # trim the empty space under the content, keeping the same margin as at the top
        im = Image.open(out).convert('RGB')
        box = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).getbbox()
        im.crop((0, 0, im.width, min(im.height, box[3] + 64))).save(out, optimize=True)


def swatch(var, label, value):
    return f'<div class="sw"><i style="background: var(--{var})"></i><b>{label}</b><span>{value}</span></div>'


def refs(node, prefix, out):
    """token path -> the value as written in the variables file (alias or literal)"""
    if isinstance(node, dict) and '$value' in node:
        out[prefix] = (node['$type'], node['$value'])
    if isinstance(node, dict):
        for key, child in node.items():
            if not key.startswith('$') and isinstance(child, dict):
                refs(child, f'{prefix}.{key}' if prefix else key, out)
    return out


def main():
    source = json.load(open(os.path.join(ROOT, 'design', 'figma-variables.json'), encoding='utf-8'))[0]
    tokens = json.load(open(os.path.join(ROOT, 'tokens.json'), encoding='utf-8'))
    primitives = tokens['primitives']
    theme = refs(tokens['theme']['light'], '', {})
    components = refs(tokens['component']['light'], '', {})
    written = refs(source['VooDoo · Components']['Default']['component'], '', {})
    typography = tokens['typography']
    os.makedirs(os.path.join(DOCS, 'design-system'), exist_ok=True)

    palettes = ['primary', 'info', 'neutral', 'success', 'warning', 'danger']
    body = ''.join(
        f'<h2>{name}</h2><div class="row">' + ''.join(swatch(f'{name}-{step}', step, t['$value']) for step, t in primitives[name].items()) + '</div>'
        for name in palettes)
    sheet('palette.png', 1000, body)

    surfaces = [k for k in theme if k.startswith('surface.')]
    texts = [k for k in theme if k.startswith('text.inverse')]
    body = '<div class="blue"><h2>Surfaces on the app blue</h2>'
    for start in range(0, len(surfaces), 6):
        body += '<div class="row">' + ''.join(swatch(k.replace('.', '-'), k.split('.')[1], theme[k][1]) for k in surfaces[start:start + 6]) + '</div>'
    body += '<h2>Light text</h2><div class="row">' + ''.join(swatch(k.replace('.', '-'), k.split('.')[1], theme[k][1]) for k in texts) + '</div>'
    body += '<h2>Task categories</h2><div class="row">' + ''.join(
        swatch(k.replace('.', '-'), k.split('.')[1], components[k][1]) for k in components if k.startswith('category.')) + '</div></div>'
    sheet('surfaces.png', 760, body)

    samples = {'display': 'You take care', 'title': 'Coming up', 'section': 'Who’s in the family', 'card-title': 'March 2027',
               'wordmark': 'nahadayka', 'tagline': 'Mom’s AI assistant for everyday routines', 'body': 'Tap the mic and tell me what to remember.',
               'body-loose': 'A few details about your child.', 'button': 'Get started', 'item-title': 'Pediatric checkup', 'value': 'Monday, 17:00',
               'label': 'Tap when you’re done', 'meta': 'Teo · every Monday', 'label-strong': 'AI created'}
    styles = tokens['textStyles']

    def part(ref):
        return ref.strip('{}').split('.')[-1]

    body = '<div class="blue">'
    for name, style in styles.items():
        v = style['$value']
        family, weight, size = part(v['fontFamily']), part(v['fontWeight']), part(v['fontSize'])
        spacing = 'letter-spacing: var(--letter-spacing-display);' if family == 'display' else ''
        case = 'text-transform: uppercase;' if v.get('textCase') else ''
        if name == 'tagline':
            case += 'color: var(--header-tagline);'
        body += (f'<div class="type"><small><b>{name}</b><br>{typography["font-family"][family]["$value"]} {weight} · {size} / {v["lineHeight"]}</small>'
                 f'<span style="font-family: var(--font-family-{family}); font-weight: var(--font-weight-{weight}); font-size: var(--font-size-{size}); {spacing}{case}">{samples[name]}</span></div>')
    sheet('typography.png', 880, body + '</div>')

    count = screens()

    # ---------------------------------------------------------------- the Markdown page
    md = ['# Нагадайка design system', '',
          '> Generated by `python3 scripts/build-design-docs.py` from [`design/figma-variables.json`](../design/figma-variables.json). Do not edit by hand.', '',
          'One source of truth, in this order: **Figma variables** → [`figma-variables.json`](../design/figma-variables.json) → `npm run tokens` → '
          '[`tokens.json`](../tokens.json) and [`tokens.css`](../src/styles/tokens.css) → [the prototype](../screens/app.html).', '',
          '## Rules', '',
          '- Solid blue background (`--screen-bg`); the flower photo appears only on the first screen.',
          '- Dark glass surfaces and orange primary actions. Labels on orange are always light.',
          '- Headings use Unbounded, everything else Inter.',
          '- Design values are whole numbers. Screens are mobile only, 440 × 956.',
          '- The mascot has no outline.', '',
          '## Colour', '', '![Colour palettes](design-system/palette.png)', '',
          '![Surfaces, light text and task categories](design-system/surfaces.png)', '',
          '## Typography', '', '![Text styles](design-system/typography.png)', '',
          '| Text style | Family | Weight | Size | Line height | Letter spacing | Used for |', '|---|---|---|---|---|---|---|']
    for name, style in styles.items():
        v = style['$value']
        family = part(v['fontFamily'])
        md.append(f'| `{name}` | {typography["font-family"][family]["$value"]} | {part(v["fontWeight"])} | {part(v["fontSize"])} | {v["lineHeight"]} | '
                  f'{v.get("letterSpacing", "0")} | {style.get("$description", "")} |')
    radius = ', '.join(f'`{k}` {t["$value"]}' for k, t in primitives['radius'].items())
    space = ', '.join(t['$value'] for t in primitives['space'].values())
    md += ['', '## Shape and spacing', '', f'- Radius: {radius}', f'- Space scale: {space}', '',
           '## Semantic colours added for the concept', '', '| Token | CSS variable | Value |', '|---|---|---|']
    for key, (_, value) in theme.items():
        if key.startswith('surface.') or key.startswith('text.inverse-') or key.startswith('border.on-'):
            md.append(f'| `{key}` | `--{key.replace(".", "-")}` | `{value}` |')
    md += ['', '## Component tokens', '', '| Token | CSS variable | Points to | Value |', '|---|---|---|---|']
    for key, (_, value) in components.items():
        alias = written[key][1]
        shown = f'`{alias.strip("{}")}`' if str(alias).startswith('{') else '—'
        md.append(f'| `{key}` | `--{key.replace(".", "-")}` | {shown} | `{value}` |')
    md += ['', '## Screens', '', '<table>']
    for start in range(0, len(SCREENS), 4):
        row = SCREENS[start:start + 4]
        md.append('<tr>' + ''.join(f'<td align="center"><img src="screens/{n}.jpg" width="200" alt="{c}"><br>{c}</td>' for n, c, _, _ in row) + '</tr>')
    md += ['</table>', '']
    open(os.path.join(DOCS, 'design-system.md'), 'w', encoding='utf-8').write('\n'.join(md))
    print(f'ok docs/design-system.md, 3 sheets, {count} screens')


if __name__ == '__main__':
    main()
