#!/usr/bin/env python3
"""Exports every screen of the prototype (screens/app.html) as static HTML that can be imported into Figma.

    python3 scripts/export-figma.py

Output (screens/figma/): one 440 x 956 file per screen and state, all-screens.html with all of them on
one page, and nahadayka-screens.zip with the separate files. The files have no scripts and no style
sheet: every element carries its computed styles, pseudo-elements are real elements, inputs are plain
text and images are embedded. Import with a plugin such as html.to.design (File tab).

Needs Google Chrome and Pillow.
"""
import base64, io, json, os, re, subprocess, sys, tempfile, zipfile
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP = os.path.join(ROOT, 'screens', 'app.html')
OUT = os.path.join(ROOT, 'screens', 'figma')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Inter:wght@400;500;600;700;800;900&family=Unbounded:wght@400;500;700;800&display=swap">')

PHRASE = 'Teo has football every Monday\nat 17:00'
# file name, caption, route, script that brings the screen into the wanted state
SCREENS = [
    ('01-welcome', '1 · Welcome', '', ''),
    ('02-authorization', '2 · Authorization', '#auth', ''),
    ('03-permissions-child', '3 · Permissions & child', '#setup', ''),
    ('04a-home-empty', '4 · Home, empty', '#home', ''),
    ('04b-home-tasks', '4 · Home, with tasks', '#home-tasks', ''),
    ('04c-home-quick-edit', '4 · Home, quick edit', '#home-tasks', "document.querySelector('#home-list .htask-row').click()"),
    ('05-listening', '5 · Listening', '#create',
     "stopListening(); document.getElementById('transcript').textContent = %s;" % json.dumps(PHRASE)),
    ('06a-ai-understands', '6 · AI understands', '#understand', ''),
    ('06b-one-question', '6 · One question', '#understand-ask', ''),
    ('07a-review', '7 · Review', '#review', ''),
    ('07b-review-time', '7 · Review, time', '#review', "document.querySelector('#review [data-field=when]').click()"),
    ('08-done', '8 · Done', '#done', ''),
    ('09-calendar', '9 · Calendar', '#calendar', ''),
    ('10a-push', '10 · Push', '#push', ''),
    ('10b-push-actions', '10 · Push, actions', '#push', "toggleActions()"),
    ('10c-push-group', '10 · Push, group', '#push-demo', "document.querySelector('#proto-chips [data-group]').click()"),
    ('11-log-in', '11 · Log in', '#login', ''),
]

# Runs inside the prototype: copies the visible screen with its computed styles inlined.
SERIALIZER = r"""
const PROPS = ['display','position','box-sizing','width','height','min-height','max-height','margin-top','margin-right','margin-bottom','margin-left',
  'padding-top','padding-right','padding-bottom','padding-left','flex-direction','flex-wrap','justify-content','align-items','align-self',
  'flex-grow','flex-shrink','flex-basis','row-gap','column-gap','grid-template-columns','background-color','color','font-family','font-size',
  'font-weight','line-height','letter-spacing','text-transform','text-align','text-decoration-line','text-underline-position','white-space',
  'border-top-width','border-right-width','border-bottom-width','border-left-width','border-top-style','border-right-style','border-bottom-style',
  'border-left-style','border-top-color','border-right-color','border-bottom-color','border-left-color','border-top-left-radius',
  'border-top-right-radius','border-bottom-right-radius','border-bottom-left-radius','box-shadow','opacity','transform','transform-origin',
  'overflow-x','overflow-y','backdrop-filter','z-index','vertical-align','text-wrap-style'];
const SKIP = { 'display': 'inline', 'position': 'static', 'min-height': 'auto', 'max-height': 'none', 'transform': 'none', 'box-shadow': 'none',
  'opacity': '1', 'backdrop-filter': 'none', 'z-index': 'auto', 'text-transform': 'none', 'text-decoration-line': 'none',
  'background-color': 'rgba(0, 0, 0, 0)', 'grid-template-columns': 'none', 'vertical-align': 'baseline', 'letter-spacing': 'normal', 'text-wrap-style': 'auto' };
// color(srgb r g b / a) -> rgba(), which design tools understand
const rgba = (v) => v.replace(/color\(srgb ([\d.e-]+) ([\d.e-]+) ([\d.e-]+)(?: \/ ([\d.]+))?\)/g,
  (m, r, g, b, a) => 'rgba(' + [r, g, b].map((c) => Math.round(c * 255)).join(', ') + ', ' + (a === undefined ? 1 : Math.round(a * 100) / 100) + ')');
function styleOf(cs) {
  let out = '';
  for (const p of PROPS) {
    let v = cs.getPropertyValue(p);
    if (!v || SKIP[p] === v) continue;
    if (p.startsWith('border-') && p.endsWith('-width') && v === '0px') continue;
    if (p.startsWith('border-') && (p.endsWith('-style') || p.endsWith('-color')) && cs.getPropertyValue(p.replace(/-(style|color)$/, '-width')) === '0px') continue;
    if ((p.startsWith('margin') || p.startsWith('padding') || p.endsWith('radius')) && v === '0px') continue;
    out += p + ':' + rgba(v) + ';';
  }
  if (cs.position === 'absolute') out += 'left:' + cs.left + ';top:' + cs.top + ';';
  if (cs.position === 'relative' && (cs.left !== 'auto' && cs.left !== '0px')) out += 'left:' + cs.left + ';';
  return out;
}
function copy(el) {
  const cs = getComputedStyle(el);
  if (el.hidden || cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0' || el.classList.contains('proto')) return null;
  const tag = el.tagName.toLowerCase();
  if (tag === 'svg') {
    const svg = el.cloneNode(true);
    const color = rgba(cs.color);
    svg.setAttribute('width', parseFloat(cs.width)); svg.setAttribute('height', parseFloat(cs.height));
    svg.setAttribute('style', styleOf(cs));
    [svg, ...svg.querySelectorAll('*')].forEach((n) => ['stroke', 'fill'].forEach((a) => { if (n.getAttribute(a) === 'currentColor') n.setAttribute(a, color); }));
    // the time wheel and the countdown circle get their paint from the style sheet
    if (el.closest('.wheel')) {
      const from = el.querySelectorAll('rect, text'), to = svg.querySelectorAll('rect, text');
      from.forEach((n, i) => to[i].setAttribute('fill', rgba(getComputedStyle(n).fill)));
      svg.setAttribute('font-family', getComputedStyle(el).fontFamily);
      svg.setAttribute('font-size', parseFloat(getComputedStyle(el).fontSize));
    }
    el.querySelectorAll('circle').forEach((c, i) => { const s = getComputedStyle(c); const n = svg.querySelectorAll('circle')[i];
      n.setAttribute('fill', 'none'); n.setAttribute('stroke', rgba(s.stroke)); n.setAttribute('stroke-width', parseFloat(s.strokeWidth)); });
    return svg;
  }
  if (tag === 'input') {
    if (el.type === 'time') return null;
    const box = document.createElement('div');
    box.setAttribute('class', el.className);
    box.setAttribute('style', styleOf(cs) + 'display:flex;align-items:center;');
    box.textContent = el.value;
    return box;
  }
  const keep = ['span', 'img', 'br', 'i', 'small'];
  const node = document.createElement(keep.includes(tag) ? tag : 'div');
  if (el.className) node.setAttribute('class', el.className);
  if (tag === 'br') return node;
  let style = styleOf(cs);
  if (tag === 'img') node.setAttribute('src', el.getAttribute('src'));
  // a one-line text must stay one line even if the design tool measures the font a bit differently
  const onlyText = el.childElementCount === 0 && el.textContent.trim();
  if (onlyText && cs.whiteSpace !== 'nowrap' && el.offsetHeight <= parseFloat(cs.fontSize) * 1.5 + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom)) style += 'white-space:nowrap;';
  // centring that a div does not get for free: grid "place-items: center" and the native centring of a button
  if (cs.display === 'grid' && cs.justifyItems === 'center' && cs.alignItems === 'center') style += 'display:flex;align-items:center;justify-content:center;';
  else if (tag === 'button' && (cs.display === 'inline-block' || cs.display === 'block') && !el.classList.contains('switch'))
    style += 'display:' + (cs.display === 'block' ? 'flex' : 'inline-flex') + ';align-items:center;justify-content:' + (cs.textAlign === 'left' ? 'flex-start' : 'center') + ';';
  node.setAttribute('style', style);
  el.childNodes.forEach((child) => {
    if (child.nodeType === 3) { if (child.textContent.trim()) node.appendChild(document.createTextNode(child.textContent)); }
    else if (child.nodeType === 1) { const c = copy(child); if (c) node.appendChild(c); }
  });
  // pseudo-element used by the switch knob -> a real element
  const after = getComputedStyle(el, '::after');
  if (el.classList.contains('switch')) {
    const knob = document.createElement('div');
    const on = el.getAttribute('aria-checked') === 'true';
    knob.setAttribute('class', 'knob');
    knob.setAttribute('style', 'position:absolute;left:' + (on ? 18 : 2) + 'px;top:2px;width:' + after.width + ';height:' + after.height +
      ';border-radius:999px;background-color:' + rgba(after.backgroundColor) + ';box-shadow:' + rgba(after.boxShadow) + ';');
    node.appendChild(knob);
  }
  return node;
}
function serialize() {
  const screen = document.querySelector('.screen:not([hidden])');
  const stage = screen.querySelector('.stage');
  const root = copy(stage);
  const bg = rgba(getComputedStyle(screen).backgroundColor);
  root.setAttribute('class', 'screen ' + screen.id);
  root.setAttribute('style', root.getAttribute('style').replace(/(position|left|top|transform|transform-origin|background-color):[^;]*;/g, '') +
    'position:relative;overflow:hidden;background-color:' + bg + ';');
  return root.outerHTML;
}
"""


def capture(route, action, tmp):
    app = open(APP, encoding='utf-8').read()
    base = 'file://' + os.path.dirname(APP) + '/'
    app = app.replace('<head>', '<head>\n<base href="%s">' % base, 1)
    script = """<script>%s
location.hash = %s; route();
setTimeout(() => { %s;
  setTimeout(() => {
    const pre = document.createElement('pre'); pre.id = 'export';
    pre.textContent = btoa(unescape(encodeURIComponent(serialize())));
    document.body.appendChild(pre);
  }, 300);
}, 800);
</script></body>""" % (SERIALIZER, json.dumps(route), action)
    page = os.path.join(tmp, 'page.html')
    with open(page, 'w', encoding='utf-8') as f:
        f.write(app.replace('</body>', script))
    dom = subprocess.run(
        [CHROME, '--headless=new', '--user-data-dir=' + os.path.join(tmp, 'profile'), '--no-first-run', '--force-prefers-reduced-motion',
         '--window-size=500,1200', '--virtual-time-budget=4000', '--dump-dom', 'file://' + page],
        capture_output=True, text=True, timeout=120).stdout
    m = re.search(r'<pre id="export">([^<]+)</pre>', dom)
    if not m:
        sys.exit('Could not capture ' + route)
    return base64.b64decode(m.group(1)).decode('utf-8')


_cache = {}


def data_uri(src):
    if src not in _cache:
        path = os.path.normpath(os.path.join(os.path.dirname(APP), src))
        if path.endswith('.png'):                      # the flower: enough for its usual sizes, keeps the files light
            im = Image.open(path)
            im.thumbnail((900, 900), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', optimize=True)
            _cache[src] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        else:
            with open(path, 'rb') as f:
                _cache[src] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()
    return _cache[src]


def document(title, width, height, body, extra=''):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width={width}">
<title>{title}</title>
{FONTS}
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: {width}px; min-height: {height}px; -webkit-font-smoothing: antialiased; }}
{extra}</style>
</head>
<body>
{body}
</body>
</html>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    cells, files = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for name, caption, route, action in SCREENS:
            html = capture(route, action, tmp)
            html = re.sub(r'src="(\.\./assets/[^"]+)"', lambda m: 'src="%s"' % data_uri(m.group(1)), html)
            path = os.path.join(OUT, name + '.html')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(document('nahadayka ' + caption, 440, 956, html))
            files.append(path)
            cells.append(f'<div class="cell"><div class="caption">{caption}</div>{html}</div>')
            print('wrote', os.path.relpath(path, ROOT))
    # all screens on one 1920 px page: 4 columns
    grid = '<div class="grid">' + ''.join(cells) + '</div>'
    css = ('.grid { display: flex; flex-wrap: wrap; gap: 40px; width: 1920px; padding: 20px; background: #FFFFFF; }\n'
           '.cell { display: flex; flex-direction: column; gap: 12px; width: 440px; }\n'
           '.caption { font: 600 22px/28px Inter, sans-serif; color: #2B2827; }\n')
    rows = (len(SCREENS) + 3) // 4
    with open(os.path.join(OUT, 'all-screens.html'), 'w', encoding='utf-8') as f:
        f.write(document('nahadayka all screens', 1920, rows * 1036, grid, css))
    with zipfile.ZipFile(os.path.join(OUT, 'nahadayka-screens.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, os.path.basename(path))
    print('wrote screens/figma/all-screens.html and nahadayka-screens.zip')


if __name__ == '__main__':
    main()
