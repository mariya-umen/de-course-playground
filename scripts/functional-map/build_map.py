"""Builds docs/functional-map.svg and docs/functional-map.png: the MVP functional map (English).

    python3 scripts/functional-map/build_map.py

The phone thumbnails are screenshots of the prototype (screens/app.html), so the map always shows the
current design. Inter is embedded into the SVG and the PNG is rendered at 2x. Flow logic: Figma file "DE",
page "Нагадайка концепт" + docs/product-spec.md (sections 5, 7, 10). Needs Google Chrome and Pillow.
"""
import base64, importlib.util, io, os, subprocess, tempfile
from xml.sax.saxutils import escape as esc
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
APP = os.path.join(ROOT, 'screens', 'app.html')
SVG = os.path.join(ROOT, 'docs', 'functional-map.svg')
PNG = os.path.join(ROOT, 'docs', 'functional-map.png')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# design-system colours (src/styles/tokens.css)
N50, N100, N200, N300, N500, N600, N900 = '#F8F7F7', '#EEEDEC', '#DDDADA', '#C2BDBC', '#877B78', '#5C5451', '#2B2827'
P50, P100, P200, P500, P600, P900 = '#FCF5F2', '#F9E8E1', '#F7D3C6', '#F7611A', '#E35004', '#4D1D08'
OK, OKBG, INFO, INFOBG, WARN, WARNBG = '#1C924F', '#F4FBF7', '#0331B0', '#F2F5FD', '#B2720A', '#FCF8F3'
WHITE, INK = '#FFFFFF', '#0A0B0F'

W, H = 1760, 2572
out = []
def add(s): out.append(s)

def text(x, y, s, size=14, weight=400, fill=N900, anchor='start', ls=None, deco=None):
    extra = (f' letter-spacing="{ls}"' if ls else '') + (f' text-decoration="{deco}"' if deco else '')
    add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>{esc(s)}</text>')

def lines(x, y, arr, size=14, weight=400, fill=N600, lh=20, anchor='start'):
    for i, s in enumerate(arr):
        text(x, y + i * lh, s, size, weight, fill, anchor)

def rect(x, y, w, h, fill=WHITE, stroke='none', sw=1, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

def circle(cx, cy, r, fill, stroke='none', sw=1):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def line(x1, y1, x2, y2, stroke=N300, sw=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{d}/>')

def path(d, stroke=N500, sw=2, fill='none', dash=None, marker=False):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    m = ' marker-end="url(#arr)"' if marker else ''
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{da}{m}/>')

def pill(x, y, w, h, label, fill, fg, size=12, weight=600, stroke='none', dash=None):
    rect(x, y, w, h, fill, stroke, 1, h // 2, dash)
    text(x + w // 2, y + h // 2 + 4, label, size, weight, fg, 'middle')

def bar(x, y, w, h=8, fill=N200, rx=4):
    rect(x, y, w, h, fill, 'none', 1, rx)

# ------------------------------------------------------------------ layout
CW, CH = 175, 380            # phone thumbnail (440 x 956)
IN = 22                      # the thumbnail sits this far inside its 220 px column
X0 = 90
PITCH = 330
ROW_Y = [330, 1010]
TAGS = {
    'done': ('DONE', N900, N50, 'none', None),
    'mvp':  ('MVP', P500, INK, 'none', None),
    'prop': ('PROPOSAL', WHITE, N600, N500, '4 3'),
    'push': ('PUSH', INFOBG, INFO, 'none', None),
}
CUR_TAG = 'mvp'

def badge(cx, cy, n, tag):
    fill = {'done': N900, 'mvp': P500, 'prop': WHITE, 'push': INFO}[tag]
    fg = {'done': N50, 'mvp': INK, 'prop': N600, 'push': WHITE}[tag]
    st = N500 if tag == 'prop' else 'none'
    da = ' stroke-dasharray="4 3"' if tag == 'prop' else ''
    add(f'<circle cx="{cx}" cy="{cy}" r="18" fill="{fill}" stroke="{st}" stroke-width="2"{da}/>')
    text(cx, cy + 6, str(n), 16, 700, fg, 'middle')

def chrome(url, out, w, h, scale=1):
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([CHROME, '--headless=new', '--user-data-dir=' + profile, '--no-first-run', '--hide-scrollbars',
                        '--force-prefers-reduced-motion', f'--force-device-scale-factor={scale}', f'--window-size={w},{h}',
                        '--virtual-time-budget=8000', '--screenshot=' + out, url], capture_output=True, timeout=120, check=True)

def shot(route, action=''):
    """one screen of the prototype as a JPEG data URI"""
    app = open(APP, encoding='utf-8').read()
    app = app.replace('<head>', '<head>\n<base href="file://%s/">' % os.path.dirname(APP), 1)
    app = app.replace('const SILENCE_MS = 2500;', 'const SILENCE_MS = 999999;')   # stay on the listening screen
    app = app.replace('</body>', '<script>location.hash = "%s"; route(); setTimeout(() => { %s }, 600);</script></body>' % (route, action))
    with tempfile.TemporaryDirectory() as tmp:
        page, png = os.path.join(tmp, 'page.html'), os.path.join(tmp, 'shot.png')
        open(page, 'w', encoding='utf-8').write(app)
        chrome('file://' + page, png, 600, 956)
        im = Image.open(png).convert('RGB').crop((80, 0, 520, 956)).resize((CW * 2, CH * 2), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=86)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

def phone(x, y, route, action=''):
    key = f'clip{len(out)}'
    add(f'<clipPath id="{key}"><rect x="{x + IN}" y="{y}" width="{CW}" height="{CH}" rx="18"/></clipPath>')
    add(f'<image x="{x + IN}" y="{y}" width="{CW}" height="{CH}" clip-path="url(#{key})" href="{shot(route, action)}"/>')
    rect(x + IN, y, CW, CH, 'none', N300, 2, 18)

def screen_header(i, col, row, title, tag):
    global CUR_TAG
    CUR_TAG = tag
    x = X0 + col * PITCH
    y = ROW_Y[row]
    badge(x + 18, y + 18, i, tag)
    text(x + 46, y + 24, title, 18, 700, N900)
    return x, y + 44

def caption(x, y, does, funcs):
    label, bg, fg, st, da = TAGS[CUR_TAG]
    w = 14 + len(label) * 8
    pill(x, y - 14, w, 22, label, bg, fg, 11, 700, st, da)
    y += 30
    lines(x, y, does, 13, 400, N600, 18)
    y2 = y + len(does) * 18 + 6
    cx = x
    for f in funcs:
        w = 14 + len(f) * 7
        if cx + w > x + CW + 20:
            cx = x; y2 += 26
        pill(cx, y2, w, 22, f, P50, P900, 11, 600, P200)
        cx += w + 6

# ------------------------------------------------------------------ canvas
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, system-ui, sans-serif">')
add('<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M1,1 L9,5 L1,9" fill="none" stroke="#5C5451" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')
rect(0, 0, W, H, N50)

text(90, 96, 'Nahadayka', 48, 700, N900)
text(90, 140, 'MVP functional map · the user journey step by step', 22, 500, N600)
text(90, 176, 'Voice → AI → Task → Calendar → Reminder · all 10 screens approved in the prototype', 16, 600, P600)

lx = 1040
text(lx, 70, 'LEGEND', 13, 700, N500, 'start', 1)
for k, (tag, desc) in enumerate([('done', 'designed in Figma and approved in the prototype'), ('push', 'system notification (lock screen), approved')]):
    yy = 98 + k * 30
    badge(lx + 12, yy - 4, '', tag)
    text(lx + 40, yy, desc, 14, 400, N600)
text(lx, 166, 'BRANCH CARDS', 11, 700, N500, 'start', 1)
pill(lx + 110, 152, 52, 20, 'BUILT', OKBG, OK, 11, 700, OK)
pill(lx + 168, 152, 56, 20, 'TO DO', N100, N600, 11, 700, N500, '4 3')
path(f'M{lx},210 L{lx+40},210', N500, 2, marker=True)
text(lx + 52, 215, 'main path', 14, 400, N600)
path(f'M{lx+190},210 L{lx+230},210', N500, 2, dash='6 5', marker=True)
text(lx + 242, 215, 'branch / later', 14, 400, N600)

rect(90, 214, 880, 56, P50, P200, 1, 12)
text(110, 238, 'MVP SUCCESS CRITERION', 12, 700, P600, 'start', 1)
text(110, 258, '15–20 seconds from tapping the mic (step 4) to a confirmed card (step 7).', 16, 600, N900)

def phase(x, y, w, label, color):
    rect(x, y, w, 4, color, 'none', 1, 2)
    text(x, y - 10, label, 12, 700, N500, 'start', 1)
phase(X0, 300, 3 * PITCH - 110, 'SIGN-UP AND SETUP', N900)
phase(X0 + 3 * PITCH, 300, 2 * PITCH - 110, 'CREATING A TASK', P500)
phase(X0, 980, 3 * PITCH - 110, 'CREATING A TASK (CONTINUED): AI → CARD → CALENDAR', P500)
phase(X0 + 3 * PITCH, 980, 2 * PITCH - 110, 'CALENDAR AND REMINDERS', INFO)

# ------------------------------------------------------------------ the screens
def screen(n, col, row, title, route, text_, funcs, tag='done', action=''):
    x, y = screen_header(n, col, row, title, tag)
    phone(x, y, route, action)
    caption(x, y + CH + 26, text_, funcs)

screen(1, 0, 0, 'Welcome', '', ['Mascot, one promise and one', 'primary action. Returning', 'users have a link below.'], ['Onboarding'])
screen(2, 1, 0, 'Authorization', '#auth', ['One tap: Apple, Google or', 'e-mail, no passwords here.', 'Returning users: “Log in”.'], ['Apple', 'Google', 'E-mail'])
screen(3, 2, 0, 'Permissions & child', '#setup', ['Mic and notifications on. Calendar', 'is on after a Google sign-in, off', 'with a hint after Apple / e-mail.'], ['Permissions', 'Child profile'])
screen(4, 3, 0, 'Home', '#home-tasks', ['First run: empty (“All clear for', 'now”). Then cards with a category', 'line; a tap opens a quick edit.'], ['Task list', 'Quick edit', 'Empty state'])
screen(5, 4, 0, 'Create · Listening', '#create', ['Live transcript. The stop button', 'ends it, or 2.5 s of silence.', 'A tab leaves without saving.'], ['Voice Capture', 'Auto-finish'],
       action="stopListening(); document.getElementById('transcript').textContent = 'Teo has football every Monday\\nat 17:00';")
screen(6, 0, 1, 'Create · AI understands', '#understand', ['Who, type, when, repeat. A missing', 'detail is marked, then asked as', 'one short question by voice.'], ['Intent parsing', '2 states'])
screen(7, 1, 1, 'Review · card', '#review', ['Tap a line to change it: a time', 'wheel, or a list for reminder and', 'repeat. Also “Event details”.'], ['Smart Task Card', 'Quick edit'])
screen(8, 2, 1, 'Done · added', '#done', ['Repeats the reminder, with Undo.', '“Connect Google Calendar” if it', 'is off. New task shows on Home.'], ['Sync', 'Undo'])
screen(9, 3, 1, 'Calendar', '#calendar', ['Month and the day’s tasks as a', 'deck; a tap opens an event.', 'Overlaps are marked.'], ['Smart Calendar', 'Conflicts'])
screen(10, 4, 1, 'Push reminder', '#push', ['Text per task type. Hold for', 'actions; other reminders wait', 'underneath. Tap opens the card.'], ['Proactive Reminder', 'Actions', 'Group'], 'push', 'toggleActions();')

# ------------------------------------------------------------------ main-path arrows
def edge(col, side):
    return X0 + col * PITCH + IN + (CW if side == 'r' else 0)
def mid_y(row): return ROW_Y[row] + 44 + CH // 2
def link(col, row, label):
    x1 = edge(col, 'r') + 8; x2 = edge(col + 1, 'l') - 8; yy = mid_y(row)
    path(f'M{x1},{yy} L{x2},{yy}', N500, 2, marker=True)
    parts = label if isinstance(label, list) else [label]
    w = 10 + max(len(p) for p in parts) * 6
    h = 8 + len(parts) * 14
    cx = (x1 + x2) // 2
    rect(cx - w // 2, yy - 6 - h, w, h, N50, 'none', 1, 6)
    for i, p in enumerate(parts):
        text(cx, yy - 6 - h + 14 + i * 14, p, 12, 600, N600, 'middle')
for col, lab in [(0, 'Get started'), (1, ['Pick a', 'method']), (2, 'Continue'), (3, 'Mic')]:
    link(col, 0, lab)
for col, lab in [(0, 'Continue'), (1, 'Confirm'), (2, 'Calendar tab')]:
    link(col, 1, lab)
# 5 -> 6 wrap through the left gutter
xa = X0 + 4 * PITCH + IN + CW // 2; ya = ROW_Y[0] + 44 + CH + 152
gx = 44; yb = ROW_Y[1] + 18
path(f'M{xa},{ya} L{xa},{ya+30} L{gx},{ya+30} L{gx},{yb} L{X0-8},{yb}', N500, 2, marker=True)
rect((xa + gx) // 2 - 82, ya + 20, 164, 20, N50, 'none', 1, 6); text((xa + gx) // 2, ya + 34, 'Stop, or 2.5 s of silence', 12, 600, N600, 'middle')
# 9 -> 10 (later)
x1 = edge(3, 'r') + 8; x2 = edge(4, 'l') - 8; yy = mid_y(1)
path(f'M{x1},{yy} L{x2},{yy}', N500, 2, dash='6 5', marker=True)
rect((x1 + x2) // 2 - 48, yy - 40, 96, 34, N50, 'none', 1, 6); text((x1 + x2) // 2, yy - 26, '2 weeks', 12, 600, N600, 'middle'); text((x1 + x2) // 2, yy - 12, 'before event', 12, 600, N600, 'middle')

# ------------------------------------------------------------------ branches
BY = 1680
text(90, BY - 30, 'BRANCHES AND EDGE CASES', 12, 700, N500, 'start', 1)
rect(90, BY - 20, W - 180, 4, N300, 'none', 1, 2)
branches = [
    ('1–2', 'Already have an account', ['“Log in” with Apple,', 'Google or e-mail.'], ['A log-in screen with the', 'same three buttons'], '→ step 4', 'built'),
    ('2', 'E-mail sign-in', ['“Continue with Email”', 'has no next screen.'], ['E-mail step is', 'not designed yet'], '→ step 3', 'todo'),
    ('3', 'Add another child', ['The link is only a', 'placeholder for now.'], ['Second child field', 'is not built yet'], '→ step 3', 'todo'),
    ('5', 'Voice not recognized', ['Noise, silence or a', 'cut-off recording.'], ['Try again or', 'type instead'], '→ step 5', 'todo'),
    ('6', 'Missing details', ['No time, date or child.'], ['AI asks one short', 'question, then continues'], '→ step 6', 'built'),
    ('7', 'Edit the card', ['Any line can change.'], ['Tap a line: a time wheel,', 'or a list of options'], '→ step 7', 'built'),
    ('8', 'Calendar not connected', ['Off in step 3, or Apple /', 'e-mail sign-in.'], ['“Connect Google Calendar”', 'on Done and on the card'], '→ step 8', 'built'),
    ('9', 'Calendar conflict', ['Two events overlap', 'in time.'], ['The card says which', 'event it overlaps'], '→ step 9', 'built'),
    ('9, 10', 'Open an event', ['Tap an event or a push', 'notification.'], ['Opens “Event details”;', 'Save returns to Calendar'], '→ step 9', 'built'),
]
bw = 306
for k, (frm, title, why, what, back, status) in enumerate(branches):
    row, col = divmod(k, 5)
    bx = 90 + col * (bw + 12); by = BY + row * 226
    built = status == 'built'
    rect(bx, by, bw, 206, WHITE, N300, 2, 16, '6 4')
    label = f'from step {frm}'
    pill(bx + 16, by + 16, 14 + len(label) * 6, 22, label, N100, N600, 11, 700)
    if built:
        pill(bx + bw - 16 - 52, by + 16, 52, 22, 'BUILT', OKBG, OK, 11, 700, OK)
    else:
        pill(bx + bw - 16 - 56, by + 16, 56, 22, 'TO DO', N100, N600, 11, 700, N500, '4 3')
    text(bx + 16, by + 62, title, 16, 700, N900)
    lines(bx + 16, by + 84, why, 13, 400, N600, 18)
    line(bx + 16, by + 118, bx + bw - 16, by + 118, N200, 1)
    lines(bx + 16, by + 140, what, 13, 600, N900, 18)
    text(bx + 16, by + 190, back, 12, 700, P600)

# ------------------------------------------------------------------ module map
MY = BY + 432 + 80
text(90, MY - 30, 'FEATURES BY MODULE (spec, section 5) → SCREENS', 12, 700, N500, 'start', 1)
rect(90, MY - 20, W - 180, 4, N300, 'none', 1, 2)
mods = [
    ('01', 'Voice Capture', ['Create tasks by voice.', 'Ukrainian and English.'], ('Screens: 4, 5', 'Built: live transcript, auto-finish')),
    ('02', 'Smart Task Cards', ['A card with category, date,', 'repeat and reminders.'], ('Screens: 6, 7', 'Built: missing details, quick edit')),
    ('03', 'Smart Calendar', ['Google Calendar, recurrence,', 'conflicts, shared access.'], ('Screens: 8, 9', 'Built: conflicts, Undo, connect')),
    ('04', 'Proactive Reminders', ['Hints on what to do before', 'an event: book, buy, prepare.'], ('Screen: 10 (push)', 'Built: per-type text, actions, groups')),
]
mw = 386
for k, (n, t, d, scr) in enumerate(mods):
    mx = 90 + k * (mw + 12)
    rect(mx, MY, mw, 168, WHITE, N200, 2, 16)
    circle(mx + 34, MY + 36, 18, P500); text(mx + 34, MY + 42, n, 14, 700, N50, 'middle')
    text(mx + 62, MY + 42, t, 18, 700, N900)
    lines(mx + 20, MY + 76, d, 14, 400, N600, 20)
    rect(mx + 20, MY + 104, mw - 40, 48, P50, 'none', 1, 8); text(mx + 32, MY + 124, scr[0], 12, 700, P900); text(mx + 32, MY + 142, scr[1], 12, 500, P900)

PY = MY + 208
rect(90, PY, W - 180, 100, N100, 'none', 1, 16)
text(110, PY + 34, 'LATER (outside the MVP)', 12, 700, N500, 'start', 1)
later = ['Family shared calendar access', 'Managing child profiles', 'Vaccination schedule from confirmed records', 'Deeper “what to prepare” hints (documents, shopping list)']
cx = 110; cy = PY + 52
for s_ in later:
    w = 20 + len(s_) * 7
    if cx + w > W - 110:
        cx = 110; cy += 34
    pill(cx, cy, w, 26, s_, WHITE, N600, 13, 500, N300)
    cx += w + 10

add('</svg>')

# embed Inter (the same helper the screen export uses), then render the PNG at 2x
spec = importlib.util.spec_from_file_location('export_screen', os.path.join(ROOT, 'scripts', 'export-screen.py'))
export_screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_screen)
inter = '\n'.join(block for block in export_screen.font_faces().split('@font-face') if "'Inter'" in block)
svg = '\n'.join(out).replace('<defs>', '<defs><style>@font-face' + inter + '</style>', 1)
with open(SVG, 'w', encoding='utf-8') as f:
    f.write(svg)
with tempfile.TemporaryDirectory() as tmp:
    page = os.path.join(tmp, 'map.html')
    open(page, 'w', encoding='utf-8').write('<!doctype html><meta charset="utf-8"><style>html,body{margin:0}svg{display:block}</style>' + svg)
    chrome('file://' + page, PNG, W, H, 2)
print('ok', os.path.relpath(SVG, ROOT), os.path.relpath(PNG, ROOT))
