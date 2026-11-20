"""Builds docs/functional-map.raw.svg (the MVP functional map, English; matches the prototype screens/app.html).

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

W, H = 1760, 2392
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
text(90, 176, 'Voice → AI → Task → Calendar → Reminder · all 10 screens approved in the prototype', 16, 600, P600)

lx = 1040
text(lx, 70, 'LEGEND', 13, 700, N500, 'start', 1)
for k, (tag, desc) in enumerate([('done', 'designed and approved (1–3 in Figma, 4–10 in the prototype)'), ('push', 'system notification (lock screen), approved')]):
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

# ------------------------------------------------------------------ 2 Authorization (Figma 02)
def dots(x, y, active, light=False):
    """progress dots 'step n of 2'"""
    fg = N900 if not light else N50
    for k in range(2):
        if k == active:
            rect(x + k * 14, y, 18, 6, fg, 'none', 1, 3)
        else:
            circle(x + k * 14 + (12 if active == 0 else 3), y + 3, 3, N300)

x, y = screen_header(2, 1, 0, 'Authorization', 'done')
phone(x, y)
rect(x + 20, y + 14, 18, 6, N900, 'none', 1, 3); circle(x + 46, y + 17, 3, N300)
text(x + 20, y + 40, 'nahadayka', 14, 700, N900)
text(x + 20, y + 98, 'Create an account', 16, 700, N900)
bar(x + 20, y + 112, 150, 5, N200)
for k, (lab, primary) in enumerate([('Continue with Apple', False), ('Continue with Google', True), ('Continue with Email', False)]):
    yy = y + 138 + k * 44
    if primary:
        rect(x + 16, yy, 188, 36, P500, 'none', 1, 18); text(x + 110, yy + 23, lab, 12, 700, N50, 'middle')
    else:
        rect(x + 16, yy, 188, 36, WHITE, N300, 1, 18); text(x + 110, yy + 23, lab, 12, 600, N900, 'middle')
text(x + 110, y + 284, 'I already have an account · Log in', 11, 600, N600, 'middle')
caption(x, y + CH + 26, ['One tap: Apple, Google or', 'e-mail, no passwords here.', 'Progress dots: step 1 of 2.'], ['Apple', 'Google', 'E-mail'])

# ------------------------------------------------------------------ 3 Permissions and Child
x, y = screen_header(3, 2, 0, 'Permissions & child', 'done')
phone(x, y)
circle(x + 23, y + 17, 3, N300); rect(x + 31, y + 14, 18, 6, N900, 'none', 1, 3)
text(x + 16, y + 40, 'Your family’s routine', 13, 700, N900); text(x + 16, y + 56, 'starts here', 13, 700, N900)
for k, lab in enumerate(['Microphone', 'Notifications', 'Google Calendar']):
    yy = y + 68 + k * 38
    rect(x + 16, yy, 188, 32, WHITE, N200, 1, 16); text(x + 30, yy + 15 if k == 2 else yy + 21, lab, 12, 500, N900)
    on = k < 2
    rect(x + 164, yy + 8, 30, 16, P500 if on else N200, 'none', 1, 8); circle(x + (186 if on else 172), yy + 16, 6, WHITE)
text(x + 30, y + 68 + 2 * 38 + 27, 'Connect it later', 9, 500, N500)
text(x + 16, y + 196, 'Who’s in the family', 12, 700, N500)
rect(x + 16, y + 204, 188, 28, WHITE, N300, 1, 14); text(x + 30, y + 222, 'Teo', 12, 600, N900)
text(x + 30, y + 248, '+ Add another child', 11, 600, N600)
rect(x + 16, y + 258, 188, 30, P500, 'none', 1, 15); text(x + 110, y + 277, 'Continue', 12, 700, N50, 'middle')
caption(x, y + CH + 26, ['Mic and notifications on. Calendar', 'is on after a Google sign-in, off', 'with a hint after Apple / e-mail.'], ['Permissions', 'Child profile'])

# ------------------------------------------------------------------ 4 Home
x, y = screen_header(4, 3, 0, 'Home', 'done')
phone(x, y)
text(x + 16, y + 32, 'Coming up', 14, 700, N900)
for k, (t, s_, c) in enumerate([('Football', 'Teo · every Monday', INFO), ('Pediatric checkup', 'Teo · Health checkup', OK), ('Vitamins', 'Teo · every day', WARN)]):
    yy = y + 46 + k * 50
    rect(x + 16, yy, 188, 42, WHITE, N200, 1, 21); circle(x + 32, yy + 21, 5, c)
    text(x + 46, yy + 18, t, 12, 700, N900); text(x + 46, yy + 33, s_, 10, 400, N500)
pill(x + 112, y + 53, 30, 16, 'New', P500, N50, 9, 700)
rect(x + 16, y + 238, 188, 44, N200, 'none', 1, 22)
circle(x + 110, y + 242, 24, P500); rect(x + 104, y + 230, 12, 18, N50, 'none', 1, 6); path(f'M{x+99},{y+243} q11,14 22,0', N50, 2)
text(x + 52, y + 266, 'Home', 10, 700, N900, 'middle'); text(x + 168, y + 266, 'Calendar', 10, 600, N500, 'middle')
caption(x, y + CH + 26, ['First run: empty (“All clear for', 'now”). Then a task list; a new', 'task is highlighted once.'], ['Task list', 'Tab bar', 'Empty state'])

# ------------------------------------------------------------------ 5 Listening
x, y = screen_header(5, 4, 0, 'Create · Listening', 'done')
phone(x, y)
circle(x + 110, y + 70, 44, P100); circle(x + 110, y + 70, 30, P500)
rect(x + 102, y + 62, 16, 16, N50, 'none', 1, 4)
path(f'M{x+110},{y+36} A34,34 0 1 1 {x+76},{y+70}', N900, 3)
for k, hh in enumerate([10, 22, 34, 18, 28, 12, 24, 8, 16]):
    rect(x + 40 + k * 15, y + 146 - hh // 2, 6, hh, P500, 'none', 1, 3)
rect(x + 16, y + 176, 188, 46, WHITE, N200, 1, 23)
lines(x + 30, y + 196, ['“Teo has football every', 'Monday at 17:00”'], 11, 500, N900, 15)
text(x + 110, y + 252, 'Tap when you’re done', 11, 600, N600, 'middle')
text(x + 110, y + 276, 'Cancel', 11, 600, N600, 'middle', None, 'underline')
caption(x, y + CH + 26, ['Live transcript. Stop icon; it ends', 'on its own after 2.5 s of silence', '(the ring fills). Cancel goes back.'], ['Voice Capture', 'Auto-finish'])

# ------------------------------------------------------------------ 6 AI understands
x, y = screen_header(6, 0, 1, 'Create · AI understands', 'done')
phone(x, y)
text(x + 16, y + 30, 'Got it', 14, 700, N900)
rect(x + 16, y + 40, 188, 30, WHITE, N200, 1, 15); text(x + 28, y + 59, 'Teo has football every Monday…', 10, 500, N600)
for k, (a_, b_) in enumerate([('Type', 'Development'), ('Who', 'Teo'), ('When', 'Mon, 17:00'), ('Repeat', 'Weekly')]):
    yy = y + 80 + k * 34
    rect(x + 16, yy, 188, 28, WHITE, N200, 1, 14); circle(x + 32, yy + 14, 7, OK); path(f'M{x+29},{yy+14} l2,3 l5,-6', WHITE, 2)
    text(x + 46, yy + 18, a_, 11, 500, N500); text(x + 196, yy + 18, b_, 12, 700, N900, 'end')
rect(x + 16, y + 224, 188, 56, WARNBG, WARN, 1, 14)
text(x + 28, y + 243, 'Missing details? “When: time?”', 10, 700, WARN)
text(x + 28, y + 259, '“What time does football start?”', 10, 500, N900)
text(x + 28, y + 273, 'Answer by voice → back to “Got it”', 9, 600, N600)
caption(x, y + CH + 26, ['AI shows type, who, when, repeat.', 'If a detail is missing it asks one', 'short question and returns here.'], ['Intent parsing', '2 states'])

# ------------------------------------------------------------------ 7 Review
x, y = screen_header(7, 1, 1, 'Review · card', 'done')
phone(x, y)
rect(x + 12, y + 14, 196, 224, WHITE, N200, 1, 20)
pill(x + 24, y + 26, 74, 20, 'AI created', P100, P900, 11, 700)
text(x + 24, y + 70, 'Football', 16, 700, N900)
text(x + 24, y + 88, 'Development · Teo', 11, 400, N500)
line(x + 24, y + 98, x + 196, y + 98, N200, 1)
text(x + 24, y + 120, 'When', 11, 500, N500); text(x + 176, y + 120, 'Monday, 17:00', 11, 600, N900, 'end'); text(x + 192, y + 120, '›', 12, 600, N500)
text(x + 24, y + 150, 'Reminder', 11, 500, N500)
for k, (lab, on) in enumerate([('30 min', False), ('1 hour', True), ('1 day', False)]):
    pill(x + 80 + k * 42, y + 138, 38, 16, lab, P500 if on else N100, N50 if on else N600, 9, 700)
text(x + 24, y + 180, 'Repeat', 11, 500, N500); text(x + 176, y + 180, 'Weekly', 11, 600, N900, 'end'); text(x + 192, y + 180, '›', 12, 600, N500)
circle(x + 97, y + 207, 4, OK); text(x + 192, y + 211, 'Google Calendar', 11, 600, N900, 'end'); text(x + 24, y + 211, 'Calendar', 11, 500, N500)
rect(x + 16, y + 250, 188, 34, P500, 'none', 1, 17); text(x + 110, y + 271, 'Confirm', 12, 700, N50, 'middle')
caption(x, y + CH + 26, ['Tap a line to change it: When and', 'Repeat in a sheet, Reminder in one', 'tap. Also opens as “Event details”.'], ['Smart Task Card', 'Quick edit'])

# ------------------------------------------------------------------ 8 Done
x, y = screen_header(8, 2, 1, 'Done · added', 'done')
phone(x, y)
rect(x + 16, y + 10, 188, 26, N900, 'none', 1, 13); text(x + 30, y + 27, 'Task added', 10, 600, N50); text(x + 190, y + 27, 'Undo', 10, 700, N50, 'end', None, 'underline')
circle(x + 110, y + 76, 30, OKBG, OK, 2); path(f'M{x+97},{y+76} l9,10 l17,-20', OK, 4)
text(x + 110, y + 134, 'All set', 14, 700, N900, 'middle')
text(x + 110, y + 152, 'Football is in your calendar.', 11, 400, N600, 'middle')
text(x + 110, y + 166, 'I’ll remind you 1 hour before.', 11, 400, N600, 'middle')
rect(x + 16, y + 180, 188, 28, WHITE, OK if False else N300, 1, 14, '4 3'); text(x + 110, y + 198, 'Connect Google Calendar · if off', 10, 600, N600, 'middle')
rect(x + 16, y + 218, 188, 32, P500, 'none', 1, 16); text(x + 110, y + 238, 'To my tasks', 12, 700, N50, 'middle')
text(x + 110, y + 272, 'Add another', 11, 600, N600, 'middle', None, 'underline')
caption(x, y + CH + 26, ['Repeats the reminder. Undo for 5 s;', '“Connect Google Calendar” if it is', 'off. The task is highlighted on Home.'], ['Sync', 'Undo'])

# ------------------------------------------------------------------ 9 Calendar
x, y = screen_header(9, 3, 1, 'Calendar', 'done')
phone(x, y)
text(x + 16, y + 30, 'Calendar', 14, 700, N900)
rect(x + 12, y + 40, 196, 112, WHITE, N200, 1, 18)
text(x + 24, y + 58, 'March 2027', 11, 700, N900)
for r in range(4):
    for c in range(7):
        cx = x + 30 + c * 26; cy = y + 76 + r * 20
        if (r, c) == (2, 0):
            circle(cx, cy, 8, P500)
        else:
            circle(cx, cy, 2, INFO if c == 0 else N200)
circle(x + 30 + 3, y + 76 + 2 * 20 + 11, 2, WARN)
text(x + 16, y + 172, 'Monday, Mar 15', 11, 700, N900); pill(x + 160, y + 160, 44, 18, 'Today', N100, N600, 10, 700)
for k, (t, conflict) in enumerate([('Pediatric checkup · 17:00', True), ('Football · 17:00', True)]):
    yy = y + 184 + k * 50
    rect(x + 16, yy, 188, 42, WHITE, WARN if conflict else N200, 2 if conflict else 1, 21)
    text(x + 30, yy + 18, t, 11, 700, N900); pill(x + 30, yy + 24, 86, 14, 'Overlaps with ' + ('football' if k == 0 else 'checkup'), WARNBG, WARN, 8, 700)
caption(x, y + CH + 26, ['Month, events of the day, overlap', 'warnings and “Today”. Tap an event', 'to edit it (“Event details”).'], ['Smart Calendar', 'Conflicts'])

# ------------------------------------------------------------------ 10 Push
x, y = screen_header(10, 4, 1, 'Push reminder', 'push')
phone(x, y, N900, N900)
text(x + 110, y + 32, 'Monday, March 1', 11, 600, N50, 'middle')
text(x + 110, y + 70, '09:00', 34, 700, N50, 'middle')
rect(x + 14, y + 96, 192, 76, N600, 'none', 1, 18)
circle(x + 34, y + 116, 9, P500); text(x + 50, y + 120, 'nahadayka', 10, 700, N50); text(x + 196, y + 120, 'now', 10, 500, N300, 'end')
text(x + 28, y + 140, 'Pediatric checkup in 2 weeks', 11, 700, N50); text(x + 28, y + 156, 'Time to book a visit.', 10, 400, N200)
pill(x + 14, y + 180, 92, 22, 'Remind me tomorrow', N600, N50, 8, 600); pill(x + 112, y + 180, 94, 22, 'Mark as booked', N600, N50, 8, 600)
rect(x + 24, y + 222, 172, 12, N500, 'none', 1, 6); rect(x + 36, y + 238, 148, 10, N600, 'none', 1, 5)
text(x + 110, y + 266, '3 reminders for Teo', 10, 600, N300, 'middle')
caption(x, y + CH + 26, ['Text per task type. Hold for actions;', 'several reminders stack into a group.', 'Tap opens the card.'], ['Proactive Reminder', 'Actions', 'Group'])

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
for col, lab in [(0, 'Continue'), (1, 'Confirm'), (2, 'Calendar tab')]:
    link(col, 1, lab)
# 5 -> 6 wrap through the left gutter
xa = X0 + 4 * PITCH + CW // 2; ya = ROW_Y[0] + 44 + CH + 152
gx = 44; yb = ROW_Y[1] + 18
path(f'M{xa},{ya} L{xa},{ya+30} L{gx},{ya+30} L{gx},{yb} L{X0-8},{yb}', N500, 2, marker=True)
rect((xa + gx) // 2 - 82, ya + 20, 164, 20, N50, 'none', 1, 6); text((xa + gx) // 2, ya + 34, 'Stop, or 2.5 s of silence', 12, 600, N600, 'middle')
# 9 -> 10 (later)
x1 = edge(3, 'r') + 8; x2 = edge(4, 'l') - 8; yy = mid_y(1)
path(f'M{x1},{yy} L{x2},{yy}', N500, 2, dash='6 5', marker=True)
rect((x1 + x2) // 2 - 48, yy - 40, 96, 34, N50, 'none', 1, 6); text((x1 + x2) // 2, yy - 26, '2 weeks', 12, 600, N600, 'middle'); text((x1 + x2) // 2, yy - 12, 'before event', 12, 600, N600, 'middle')

# ------------------------------------------------------------------ branches
BY = 1500
text(90, BY - 30, 'BRANCHES AND EDGE CASES', 12, 700, N500, 'start', 1)
rect(90, BY - 20, W - 180, 4, N300, 'none', 1, 2)
branches = [
    ('1–2', 'Already have an account', ['“Log in” with Apple,', 'Google or e-mail.'], ['Log-in screen is', 'not designed yet'], '→ step 4', 'todo'),
    ('2', 'E-mail sign-in', ['“Continue with Email”', 'has no next screen.'], ['E-mail step is', 'not designed yet'], '→ step 3', 'todo'),
    ('3', 'Add another child', ['The link is only a', 'placeholder for now.'], ['Second child field', 'is not built yet'], '→ step 3', 'todo'),
    ('5', 'Voice not recognized', ['Noise, silence or a', 'cut-off recording.'], ['Try again or', 'type instead'], '→ step 5', 'todo'),
    ('6', 'Missing details', ['No time, date or child.'], ['AI asks one short', 'question, then continues'], '→ step 6', 'built'),
    ('7', 'Edit the card', ['Any line can change.'], ['Tap a line: a sheet for', 'When and Repeat'], '→ step 7', 'built'),
    ('8', 'Calendar not connected', ['Off in step 3, or Apple /', 'e-mail sign-in.'], ['“Connect Google Calendar”', 'on Done and on the card'], '→ step 8', 'built'),
    ('9', 'Calendar conflict', ['Two events overlap', 'in time.'], ['Yellow warning on the', 'day and on both cards'], '→ step 9', 'built'),
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
    ('03', 'Smart Calendar', ['Google Calendar, recurrence,', 'conflicts, shared access.'], ('Screens: 8, 9', 'Built: conflicts, Undo, connect, Today')),
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
with open(OUT, 'w') as f:
    f.write('\n'.join(out))
print('ok', os.path.relpath(OUT))
