"""Builds docs/functional-map.raw.svg (the MVP functional map, English).

The raw SVG has no embedded font. To get the final docs/functional-map.svg and
docs/functional-map.png, embed Inter (base64 @font-face in <defs>) and render
the SVG to PNG at 2x in a browser. Source of the flow logic: Figma file "DE",
page "Нагадайка концепт" (frames 01 Welcome, 02 Authorization, 03 Permissions
and Child) + docs/product-spec.md (sections 5, 7, 10).
"""
import os
from xml.sax.saxutils import escape as esc

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'functional-map.raw.svg')

# design-system colours (src/styles/tokens.css)
N50, N100, N200, N300, N500, N600, N900 = '#F8F7F7', '#EEEDEC', '#DDDADA', '#C2BDBC', '#877B78', '#5C5451', '#2B2827'
P50, P100, P200, P500, P600, P900 = '#FCF4F2', '#FAE6E0', '#F8CFC4', '#FB4A1B', '#E73504', '#4F1708'
OK, OKBG, INFO, INFOBG, WARN, WARNBG = '#1C924F', '#F4FBF7', '#0331B0', '#F2F5FD', '#B2720A', '#FCF8F3'
WHITE, INK = '#FFFFFF', '#0A0B0F'

W, H = 1760, 2180
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
CW, CH = 220, 300            # phone size
X0 = 90
PITCH = 330
ROW_Y = [330, 930]
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

def phone(x, y, fill=N50, stroke=N300):
    rect(x, y, CW, CH, fill, stroke, 2, 24)

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
text(90, 176, 'Voice → AI → Task → Calendar → Reminder', 16, 600, P600)

lx = 1040
text(lx, 70, 'LEGEND', 13, 700, N500, 'start', 1)
for k, (tag, desc) in enumerate([('done', 'designed in Figma'), ('mvp', 'MVP core from the spec (Home, Create, Calendar)'), ('prop', 'proposal: no separate screen in the spec'), ('push', 'system notification, not an app screen')]):
    yy = 98 + k * 30
    badge(lx + 12, yy - 4, '', tag)
    text(lx + 40, yy, desc, 14, 400, N600)
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
phase(X0, 900, 3 * PITCH - 110, 'CREATING A TASK (CONTINUED): AI → CARD → CALENDAR', P500)
phase(X0 + 3 * PITCH, 900, 2 * PITCH - 110, 'CALENDAR AND REMINDERS', INFO)

# ------------------------------------------------------------------ 1 Welcome (Figma 01—Welcome)
x, y = screen_header(1, 0, 0, 'Welcome', 'done')
phone(x, y, P500, P600)
text(x + 20, y + 34, 'nahadayka', 14, 700, N50)
for dx, dy in [(0, -34), (32, -10), (20, 28), (-20, 28), (-32, -10)]:
    circle(x + 128 + dx, y + 100 + dy, 24, '#FA7A57')
circle(x + 128, y + 100, 30, '#FA7A57')
path(f'M{x+116},{y+98} q5,5 10,0 M{x+132},{y+98} q5,5 10,0', P900, 2)
text(x + 20, y + 178, 'Your routine,', 16, 700, N50); text(x + 20, y + 196, 'remembered', 16, 700, N50)
bar(x + 20, y + 208, 170, 5, P200)
rect(x + 20, y + 226, 180, 32, N900, 'none', 1, 16); text(x + 110, y + 247, 'Let’s make life easier', 12, 600, N50, 'middle')
text(x + 110, y + 280, 'I already have an account', 11, 600, N50, 'middle', None, 'underline')
caption(x, y + CH + 26, ['Mascot, one promise and one', 'primary action. Returning', 'users have a link below.'], ['Onboarding'])

# ------------------------------------------------------------------ 2 Authorization (Figma 02—Authorization)
x, y = screen_header(2, 1, 0, 'Authorization', 'done')
phone(x, y)
text(x + 20, y + 34, 'nahadayka', 14, 700, N900)
text(x + 20, y + 98, 'Create an account', 16, 700, N900)
bar(x + 20, y + 112, 150, 5, N200)
for k, (lab, primary) in enumerate([('Continue with Apple', False), ('Continue with Google', True), ('Continue with Email', False)]):
    yy = y + 138 + k * 44
    if primary:
        rect(x + 16, yy, 188, 36, P500, 'none', 1, 18); text(x + 110, yy + 23, lab, 12, 700, INK, 'middle')
    else:
        rect(x + 16, yy, 188, 36, WHITE, N300, 1, 18); text(x + 110, yy + 23, lab, 12, 600, N900, 'middle')
text(x + 110, y + 284, 'I already have an account · Log in', 11, 600, N600, 'middle')
caption(x, y + CH + 26, ['One tap: Apple, Google or', 'e-mail. No forms or passwords', 'on this screen.'], ['Apple', 'Google', 'E-mail (next step TBD)'])

# ------------------------------------------------------------------ 3 Permissions and Child (Figma 03)
x, y = screen_header(3, 2, 0, 'Permissions & child', 'done')
phone(x, y)
text(x + 16, y + 28, 'Your family’s routine', 13, 700, N900); text(x + 16, y + 44, 'starts here', 13, 700, N900)
for k, lab in enumerate(['Microphone', 'Notifications', 'Google Calendar']):
    yy = y + 58 + k * 38
    rect(x + 16, yy, 188, 32, WHITE, N200, 1, 16); text(x + 30, yy + 21, lab, 12, 500, N900)
    rect(x + 164, yy + 8, 30, 16, P500, 'none', 1, 8); circle(x + 186, yy + 16, 6, WHITE)
text(x + 16, y + 188, 'Who’s in the family', 12, 700, N500)
rect(x + 16, y + 198, 188, 30, WHITE, N300, 1, 15); text(x + 30, y + 217, 'Teo', 12, 600, N900)
rect(x + 16, y + 248, 188, 34, P500, 'none', 1, 17); text(x + 110, y + 269, 'Continue', 12, 700, INK, 'middle')
caption(x, y + CH + 26, ['Three permissions, all on by', 'default, and who is in the', 'family (e.g. “Teo”).'], ['Permissions', 'Child profile'])

# ------------------------------------------------------------------ 4 Home
x, y = screen_header(4, 3, 0, 'Home', 'mvp')
phone(x, y)
bar(x + 16, y + 20, 100, 10, N900, 5); circle(x + 190, y + 26, 12, P100)
text(x + 16, y + 58, 'UPCOMING', 11, 700, N500, 'start', 1)
for k, (t, s, c) in enumerate([('Football', 'Mon · 17:00', P500), ('Pediatrician', 'Mar 15', OK), ('Vitamins', 'daily', WARN)]):
    yy = y + 68 + k * 52
    rect(x + 16, yy, 188, 44, WHITE, N200, 1, 12); rect(x + 16, yy, 5, 44, c, 'none', 1, 2)
    text(x + 32, yy + 19, t, 12, 600, N900); text(x + 32, yy + 35, s, 11, 400, N500)
circle(x + 110, y + 262, 26, P500); rect(x + 104, y + 250, 12, 18, WHITE, 'none', 1, 6); path(f'M{x+99},{y+263} q11,14 22,0', WHITE, 2)
caption(x, y + CH + 26, ['Upcoming tasks and a big mic', 'button: the main action', 'of the app.'], ['Task list', 'Voice button'])

# ------------------------------------------------------------------ 5 Listening
x, y = screen_header(5, 4, 0, 'Create · Listening', 'mvp')
phone(x, y)
bar(x + 16, y + 20, 80, 8, N500, 4)
circle(x + 110, y + 100, 44, P100); circle(x + 110, y + 100, 30, P500)
rect(x + 104, y + 88, 12, 20, WHITE, 'none', 1, 6); path(f'M{x+98},{y+102} q12,16 24,0', WHITE, 2)
for k, hh in enumerate([10, 22, 34, 18, 28, 12, 24, 8, 16]):
    rect(x + 40 + k * 15, y + 168 - hh // 2, 6, hh, P500, 'none', 1, 3)
rect(x + 16, y + 196, 188, 52, WHITE, N200, 1, 12)
lines(x + 28, y + 216, ['“Teo has football every', 'Monday at 17:00”'], 11, 500, N900, 16)
text(x + 110, y + 278, 'Cancel', 12, 600, N600, 'middle')
caption(x, y + CH + 26, ['The mom speaks a command', 'and sees a live transcript.', 'Ukrainian and English.'], ['Voice Capture', 'Speech-to-text'])

# ------------------------------------------------------------------ 6 AI understands
x, y = screen_header(6, 0, 1, 'Create · AI understands', 'mvp')
phone(x, y)
bar(x + 16, y + 20, 110, 10, N900, 5)
circle(x + 30, y + 64, 8, P500); text(x + 46, y + 69, 'Parsing what you said…', 12, 600, N900)
for k, (a, b) in enumerate([('Type', 'Development'), ('Who', 'Teo'), ('When', 'Mon, 17:00'), ('Repeat', 'weekly')]):
    yy = y + 92 + k * 34
    rect(x + 16, yy, 188, 28, WHITE, N200, 1, 8); text(x + 26, yy + 18, a, 11, 500, N500); text(x + 80, yy + 18, b, 12, 600, N900)
    circle(x + 192, yy + 14, 7, OK); path(f'M{x+189},{yy+14} l2,3 l5,-6', WHITE, 2)
rect(x + 16, y + 236, 188, 44, WARNBG, WARN, 1, 12); text(x + 28, y + 255, 'Missing details?', 11, 700, WARN)
text(x + 28, y + 271, 'I’ll ask briefly → card', 11, 400, N900)
caption(x, y + CH + 26, ['AI detects the meaning, date,', 'category and repeat. Asks a', 'question if something is missing.'], ['Intent parsing', 'Categories'])

# ------------------------------------------------------------------ 7 Review
x, y = screen_header(7, 1, 1, 'Review · card', 'mvp')
phone(x, y)
rect(x + 12, y + 14, 196, 214, WHITE, N200, 1, 16)
pill(x + 24, y + 26, 74, 20, 'AI created', P100, P900, 11, 700)
text(x + 24, y + 66, 'Annual pediatric', 14, 700, N900); text(x + 24, y + 84, 'checkup', 14, 700, N900)
text(x + 24, y + 104, 'Health checkups · Teo', 11, 400, N500); text(x + 24, y + 122, 'March 15, 2027', 12, 600, N900)
line(x + 24, y + 136, x + 196, y + 136, N200, 1)
text(x + 24, y + 156, 'Reminder · 2 weeks before', 11, 400, N600); text(x + 24, y + 174, 'Repeat · annually', 11, 400, N600); text(x + 24, y + 192, 'Google Calendar sync', 11, 400, N600)
rect(x + 12, y + 244, 92, 34, WHITE, N300, 1, 10); text(x + 58, y + 266, 'Edit', 12, 600, N900, 'middle')
rect(x + 116, y + 244, 92, 34, P500, 'none', 1, 10); text(x + 162, y + 266, 'Confirm', 12, 700, INK, 'middle')
caption(x, y + CH + 26, ['A card to review: title,', 'category, child, date,', 'reminder, repeat.'], ['Smart Task Card', 'Edit / Confirm'])

# ------------------------------------------------------------------ 8 Done
x, y = screen_header(8, 2, 1, 'Done · added', 'prop')
phone(x, y, N50, N500)
rect(x, y, CW, CH, 'none', N500, 2, 24, '6 4')
circle(x + 110, y + 78, 34, OKBG, OK, 2); path(f'M{x+95},{y+78} l11,12 l20,-24', OK, 4)
text(x + 110, y + 146, 'Added to calendar', 14, 700, N900, 'middle')
text(x + 110, y + 168, 'I’ll remind you 2 weeks before', 12, 400, N600, 'middle')
rect(x + 16, y + 190, 188, 30, WHITE, N200, 1, 10); text(x + 110, y + 209, 'Google Calendar · synced', 11, 500, OK, 'middle')
rect(x + 16, y + 236, 88, 32, WHITE, N300, 1, 10); text(x + 60, y + 257, 'Add another', 12, 600, N900, 'middle')
rect(x + 116, y + 236, 88, 32, P500, 'none', 1, 10); text(x + 160, y + 257, 'To tasks', 12, 700, INK, 'middle')
caption(x, y + CH + 26, ['Sync confirmation, quick', 'repeat or return to Home.'], ['Sync', 'Reminder scheduled'])

# ------------------------------------------------------------------ 9 Calendar
x, y = screen_header(9, 3, 1, 'Calendar', 'mvp')
phone(x, y)
bar(x + 16, y + 20, 90, 10, N900, 5)
for r in range(4):
    for c in range(7):
        cx = x + 28 + c * 27; cy = y + 62 + r * 24
        has = (r, c) in [(0, 0), (1, 0), (2, 0), (3, 0), (1, 5)]
        if (r, c) == (1, 5):
            circle(cx, cy, 10, P500)
        else:
            circle(cx, cy, 3, P500 if has else N200)
text(x + 16, y + 168, 'RECURRING', 11, 700, N500, 'start', 1)
for k, (t, s) in enumerate([('Football', 'every Monday · 17:00'), ('Checkup', 'yearly · Mar 15')]):
    yy = y + 178 + k * 46
    rect(x + 16, yy, 188, 38, WHITE, N200, 1, 10); text(x + 28, yy + 17, t, 12, 600, N900); text(x + 28, yy + 31, s, 11, 400, N500)
    path(f'M{x+186},{yy+14} a6,6 0 1 1 -1,10', N500, 2)
caption(x, y + CH + 26, ['Events and recurring routines.', 'Conflict checks, shared', 'access (later).'], ['Smart Calendar', 'Conflicts'])

# ------------------------------------------------------------------ 10 Push
x, y = screen_header(10, 4, 1, 'Push reminder', 'push')
phone(x, y, N900, N900)
text(x + 110, y + 60, '09:41', 36, 300, N50, 'middle')
rect(x + 14, y + 100, 192, 74, N50, 'none', 1, 16)
circle(x + 34, y + 122, 10, P500); text(x + 52, y + 126, 'nahadayka', 11, 700, N900)
text(x + 26, y + 146, 'Pediatric checkup — March 15', 11, 600, N900); text(x + 26, y + 162, 'Time to book a visit', 11, 400, N600)
rect(x + 30, y + 234, 160, 6, N600, 'none', 1, 3)
caption(x, y + CH + 26, ['2 weeks before the event: what', 'to do in advance. Tap →', 'opens the task card.'], ['Proactive Reminder', 'Notification'])

# ------------------------------------------------------------------ main-path arrows
def edge(col, side):
    return X0 + col * PITCH + (CW if side == 'r' else 0)
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
for col, lab in [(0, ['Let’s make', 'life easier']), (1, ['Pick a', 'method']), (2, 'Continue'), (3, 'Mic')]:
    link(col, 0, lab)
for col, lab in [(0, 'AI parsed it'), (1, 'Confirm'), (2, 'Open')]:
    link(col, 1, lab)
# 5 -> 6 wrap through the left gutter
xa = X0 + 4 * PITCH + CW // 2; ya = ROW_Y[0] + 44 + CH + 152
gx = 44; yb = ROW_Y[1] + 18
path(f'M{xa},{ya} L{xa},{ya+30} L{gx},{ya+30} L{gx},{yb} L{X0-8},{yb}', N500, 2, marker=True)
rect((xa + gx) // 2 - 82, ya + 20, 164, 20, N50, 'none', 1, 6); text((xa + gx) // 2, ya + 34, 'You speak the command', 12, 600, N600, 'middle')
# 9 -> 10 (later)
x1 = edge(3, 'r') + 8; x2 = edge(4, 'l') - 8; yy = mid_y(1)
path(f'M{x1},{yy} L{x2},{yy}', N500, 2, dash='6 5', marker=True)
rect((x1 + x2) // 2 - 48, yy - 40, 96, 34, N50, 'none', 1, 6); text((x1 + x2) // 2, yy - 26, '2 weeks', 12, 600, N600, 'middle'); text((x1 + x2) // 2, yy - 12, 'before event', 12, 600, N600, 'middle')

# ------------------------------------------------------------------ branches
BY = 1500
text(90, BY - 30, 'BRANCHES AND EDGE CASES', 12, 700, N500, 'start', 1)
rect(90, BY - 20, W - 180, 4, N300, 'none', 1, 2)
branches = [
    ('1–2', 'Already have an account', ['“Log in” with Apple,', 'Google or e-mail.'], ['Skip the setup and', 'go to Home'], '→ step 4'),
    ('5', 'Voice not recognized', ['Noise, silence or a', 'cut-off recording.'], ['Try again or', 'type instead'], '→ step 5'),
    ('6', 'Missing details', ['No date, child or doctor.'], ['AI asks one', 'short question'], '→ step 7'),
    ('7', 'Edit the card', ['Category, child, date,', 'reminder, repeat.'], ['Edit form', 'and save'], '→ step 7'),
    ('8', 'Calendar conflict', ['The event overlaps', 'with another one.'], ['Show the overlap,', 'suggest another time'], '→ step 8'),
    ('8', 'Calendar not connected', ['Calendar was off in step 3', 'or a sync error.'], ['Connect Google', 'and retry'], '→ step 8'),
]
bw = 253
for k, (frm, title, why, what, back) in enumerate(branches):
    bx = 90 + k * (bw + 12)
    rect(bx, BY, bw, 206, WHITE, N300, 2, 16, '6 4')
    label = f'from step {frm}'
    pill(bx + 16, BY + 16, 14 + len(label) * 6, 22, label, N100, N600, 11, 700)
    text(bx + 16, BY + 62, title, 16, 700, N900)
    lines(bx + 16, BY + 84, why, 13, 400, N600, 18)
    line(bx + 16, BY + 118, bx + bw - 16, BY + 118, N200, 1)
    lines(bx + 16, BY + 140, what, 13, 600, N900, 18)
    text(bx + 16, BY + 190, back, 12, 700, P600)

# ------------------------------------------------------------------ module map
MY = 1800
text(90, MY - 30, 'FEATURES BY MODULE (spec, section 5) → SCREENS', 12, 700, N500, 'start', 1)
rect(90, MY - 20, W - 180, 4, N300, 'none', 1, 2)
mods = [
    ('01', 'Voice Capture', ['Create tasks by voice.', 'Ukrainian and English.'], ('Screens: 4, 5', 'Branch: voice not recognized')),
    ('02', 'Smart Task Cards', ['A card with category, date,', 'repeat and reminders.'], ('Screens: 6, 7', 'Branches: missing details, edit')),
    ('03', 'Smart Calendar', ['Google Calendar, recurrence,', 'conflicts, shared access.'], ('Screens: 8, 9', 'Branches: conflict, not connected')),
    ('04', 'Proactive Reminders', ['Hints on what to do before', 'an event: book, buy, prepare.'], ('Screen: 10 (push)', 'Later: “what to prepare” hints')),
]
mw = 386
for k, (n, t, d, scr) in enumerate(mods):
    mx = 90 + k * (mw + 12)
    rect(mx, MY, mw, 168, WHITE, N200, 2, 16)
    circle(mx + 34, MY + 36, 18, P500); text(mx + 34, MY + 42, n, 14, 700, INK, 'middle')
    text(mx + 62, MY + 42, t, 18, 700, N900)
    lines(mx + 20, MY + 76, d, 14, 400, N600, 20)
    rect(mx + 20, MY + 104, mw - 40, 48, P50, 'none', 1, 8); text(mx + 32, MY + 124, scr[0], 12, 700, P900); text(mx + 32, MY + 142, scr[1], 12, 500, P900)

PY = MY + 208
rect(90, PY, W - 180, 100, N100, 'none', 1, 16)
text(110, PY + 34, 'LATER (outside the MVP)', 12, 700, N500, 'start', 1)
later = ['Family shared calendar access', 'Managing child profiles', 'Vaccination schedule from confirmed records', '“What to prepare” hints before events']
cx = 110; cy = PY + 52
for s in later:
    w = 20 + len(s) * 7
    if cx + w > W - 110:
        cx = 110; cy += 34
    pill(cx, cy, w, 26, s, WHITE, N600, 13, 500, N300)
    cx += w + 10

add('</svg>')
with open(OUT, 'w') as f:
    f.write('\n'.join(out))
print('ok', os.path.relpath(OUT))
