#!/usr/bin/env python3
"""Render Zemen Bariagabr's GitHub profile README cards as animated SVGs.

Reads data/contributions.json, data/repos.json, data/user.json (produced by
fetch_data.py) and writes cards/*.svg. Every card is a self-contained SVG:
embedded subset fonts, CSS keyframes + SMIL only (what survives GitHub's
<img> sandbox). Set STATIC=1 to disable animation (final frame) for
screenshots.
"""
import base64
import calendar as calmod
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data")
FONTS = os.path.join(ROOT, "fonts")
CARDS = os.path.join(ROOT, "cards")
STATIC = os.environ.get("STATIC") == "1"

INK = "#e6edf3"
BODY = "#c9d1d9"
MUT = "#8b949e"
DIM = "#6e7681"
BG = "#0d1117"
PANEL = "#11161f"
BORDER = "#30363d"
HAIR = "#21262d"
BLUE = "#7aa2f7"
GREEN = "#9ece6a"
PURPLE = "#bb9af7"
LEVELS = ["#1b2432", "#0e3a6e", "#1560b8", "#3b9eff", "#9ecbff"]


def b64_font(fname):
    with open(os.path.join(FONTS, fname), "rb") as f:
        return base64.b64encode(f.read()).decode()


def font_css(faces):
    """faces: list of (family, weight, file)"""
    out = []
    for fam, weight, fname in faces:
        out.append(
            "@font-face{font-family:'%s';font-weight:%d;src:url(data:font/woff;base64,%s) format('woff')}"
            % (fam, weight, b64_font(fname))
        )
    return "".join(out)


INTER = [
    ("Inter", 400, "inter-latin-400-normal.woff"),
    ("Inter", 600, "inter-latin-600-normal.woff"),
    ("Inter", 800, "inter-latin-800-normal.woff"),
]
MONO = [
    ("JetBrains Mono", 400, "jetbrains-mono-latin-400-normal.woff"),
    ("JetBrains Mono", 700, "jetbrains-mono-latin-700-normal.woff"),
]

KEYFRAMES = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes swing{0%{opacity:0;transform:translateY(46px) rotate(2.5deg)}60%{opacity:1;transform:translateY(-6px) rotate(-.6deg)}100%{opacity:1;transform:translateY(0) rotate(0deg)}}
@keyframes fadein{from{opacity:0}to{opacity:1}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes sweep{0%{transform:translateX(0)}32%,100%{transform:translateX(470px)}}
.fi{font-family:Inter,sans-serif}.fm{font-family:'JetBrains Mono',monospace}
.tbc{transform-box:fill-box;transform-origin:center}
.tbb{transform-box:fill-box;transform-origin:bottom}
@media (prefers-reduced-motion: reduce){*{animation:none !important}}
"""


def style_block(faces, extra=""):
    css = font_css(faces) + KEYFRAMES + extra
    if STATIC:
        css += "*{animation:none !important}"
    return "<style>%s</style>" % css


def anim(name, dur, delay, extra=""):
    return 'style="animation:%s %ss cubic-bezier(.2,.7,.3,1) both;animation-delay:%ss;%s"' % (
        name, dur, delay, extra)


def svg_open(w, h):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d" fill="none">' % (w, h, w, h))


def card_bg(w, h):
    return ('<rect x="0.5" y="0.5" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>'
            % (w - 1, h - 1, BG, BORDER))


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def stats(contrib):
    days = contrib["days"]
    total = contrib["total"]
    active = sum(1 for d in days if d["count"] > 0)
    busiest = max(days, key=lambda d: d["count"])
    streak = best = 0
    for d in days:
        streak = streak + 1 if d["count"] > 0 else 0
        best = max(best, streak)
    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    months = sorted(monthly.items())[-12:]
    return {"total": total, "active": active, "busiest": busiest,
            "streak": best, "months": months}


def fmt_date(iso):
    y, m, d = iso.split("-")
    return "%s %d, %s" % (calmod.month_abbr[int(m)], int(d), y)


def month_label(key):
    y, m = key.split("-")
    return calmod.month_abbr[int(m)]


# ---------------------------------------------------------------- hero
def hero(user, st):
    w, h = 830, 252
    total = st["total"]
    repos = user["public_repos"]
    s = [svg_open(w, h), style_block(INTER + MONO), card_bg(w, h)]
    s.append('<defs><linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">'
             '<stop offset="0" stop-color="%s"/><stop offset=".40" stop-color="%s"/>'
             '<stop offset=".50" stop-color="#ffffff"/><stop offset=".60" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s"/>'
             '<animateTransform attributeName="gradientTransform" type="translate" '
             'values="-600 0;600 0;600 0" keyTimes="0;.38;1" dur="5.5s" begin="1.4s" repeatCount="indefinite"/>'
             '</linearGradient></defs>' % (BLUE, BLUE, BLUE, BLUE))
    s.append('<text x="40" y="46" class="fm" font-size="12" letter-spacing="2.5" fill="%s" %s>ZEMEN14 &#183; GITHUB</text>'
             % (MUT, anim("rise", .6, .0)))
    s.append('<g %s><circle cx="536" cy="42" r="4" fill="%s" style="animation:pulse 2.2s ease-in-out infinite"/>'
             '<text x="790" y="46" text-anchor="end" class="fm" font-size="11" letter-spacing="1" fill="%s">OPEN TO SUMMER 2027 INTERNSHIPS</text></g>'
             % (anim("fadein", .8, .5), GREEN, GREEN))
    s.append('<text x="38" y="122" class="fi" font-weight="800" font-size="58" letter-spacing="-1" %s>'
             '<tspan fill="%s">Zemen </tspan><tspan fill="url(#shine)">Bariagabr</tspan></text>'
             % (anim("rise", .7, .08), INK))
    s.append('<text x="40" y="162" class="fi" font-size="21" fill="%s" %s>'
             'I build systems that bridge hardware and software.</text>' % (BODY, anim("rise", .7, .28)))
    s.append('<text x="40" y="190" class="fm" font-size="12.5" letter-spacing="1.2" fill="%s" %s>'
             'B.S. COMPUTER ENGINEERING &#183; UC SANTA CRUZ &#183; EXPECTED JUNE 2028</text>'
             % (MUT, anim("rise", .7, .44)))
    s.append('<line x1="40" y1="210" x2="790" y2="210" stroke="%s" %s/>' % (HAIR, anim("fadein", .8, .55)))
    s.append('<text x="40" y="235" class="fm" font-size="12.5" %s>'
             '<tspan fill="%s" font-weight="700">%d</tspan><tspan fill="%s"> PUBLIC REPOS</tspan>'
             '<tspan dx="26" fill="%s" font-weight="700">%d</tspan><tspan fill="%s"> CONTRIBUTIONS LAST YEAR</tspan>'
             '<tspan dx="26" fill="%s">C &#183; C++ &#183; PYTHON &#183; ESP32 &#183; FPGA</tspan></text>'
             % (anim("rise", .7, .6), INK, repos, MUT, INK, total, MUT, BLUE))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- graph
def level_for(count, nonzero):
    if count == 0:
        return 0
    if not nonzero:
        return 1
    qs = sorted(nonzero)
    import bisect
    frac = bisect.bisect_right(qs, count) / len(qs)
    return 1 + min(3, int(frac * 4))


def graph(contrib, st):
    w, h = 830, 200
    weeks = contrib["weeks"]
    days_flat = contrib["days"]
    nonzero = [d["count"] for d in days_flat if d["count"] > 0]
    cell, gap = 11, 3
    step = cell + gap
    x0, y0 = 46, 68
    s = [svg_open(w, h), style_block(INTER + MONO), card_bg(w, h)]
    s.append('<text x="40" y="38" class="fm" font-size="12" letter-spacing="2" fill="%s">CONTRIBUTION GRAPH</text>' % MUT)
    s.append('<text x="752" y="38" text-anchor="end" class="fm" font-size="12" fill="%s">IN THE LAST YEAR</text>' % MUT)
    s.append('<text x="790" y="38" text-anchor="end" class="fm" font-size="12" font-weight="700" fill="%s">%d</text>'
             % (INK, st["total"]))
    # month labels
    prev_month = None
    for ci, wk in enumerate(weeks):
        if not wk:
            continue
        m = wk[0]["date"][5:7]
        if m != prev_month:
            prev_month = m
            s.append('<text x="%d" y="58" class="fm" font-size="10" fill="%s">%s</text>'
                     % (x0 + ci * step, DIM, calmod.month_abbr[int(m)]))
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        s.append('<text x="38" y="%d" text-anchor="end" class="fm" font-size="10" fill="%s">%s</text>'
                 % (y0 + row * step + cell - 2, DIM, label))
    for ci, wk in enumerate(weeks):
        for ri, d in enumerate(wk):
            lvl = level_for(d["count"], nonzero)
            delay = round(ci * 0.026 + ri * 0.004, 3)
            s.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s" class="tbc" %s/>'
                     % (x0 + ci * step, y0 + ri * step, cell, cell, LEVELS[lvl],
                        anim("pop", .35, delay)))
    lx = x0 + len(weeks) * step - 5 * (cell + 2) - 34
    s.append('<text x="%d" y="%d" class="fm" font-size="10" fill="%s">Less</text>' % (lx, h - 12, DIM))
    for i, c in enumerate(LEVELS):
        s.append('<rect x="%d" y="%d" width="10" height="10" rx="2" fill="%s"/>'
                 % (lx + 30 + i * 13, h - 22, c))
    s.append('<text x="%d" y="%d" class="fm" font-size="10" fill="%s">More</text>' % (lx + 30 + 5 * 13 + 4, h - 12, DIM))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- activity
def activity(st):
    w, h = 830, 238
    months = st["months"]
    maxv = max(v for _, v in months) or 1
    best_key, best_val = max(months, key=lambda kv: kv[1])
    base_y, top_y = 196, 70
    chart_w = 520
    step = chart_w / len(months)
    bar_w = 30
    s = [svg_open(w, h), style_block(INTER + MONO), card_bg(w, h)]
    s.append('<text x="40" y="38" class="fm" font-size="12" letter-spacing="2" fill="%s">MONTHLY ACTIVITY</text>' % MUT)
    s.append('<text x="560" y="38" text-anchor="end" class="fm" font-size="12" fill="%s">BEST: %s %s &#183; %d</text>'
             % (MUT, month_label(best_key).upper(), best_key[:4], best_val))
    s.append('<line x1="40" y1="%d" x2="560" y2="%d" stroke="%s"/>' % (base_y, base_y, HAIR))
    for i, (key, v) in enumerate(months):
        bh = max(3, (base_y - top_y) * v / maxv) if v else 2
        x = 40 + i * step + (step - bar_w) / 2
        fill = BLUE if key == best_key else "#26507e"
        s.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" rx="3" fill="%s" class="tbb" %s/>'
                 % (x, base_y - bh, bar_w, bh, fill, anim("grow", .7, .15 + i * .06)))
        if v:
            s.append('<text x="%.1f" y="%.1f" text-anchor="middle" class="fm" font-size="11" font-weight="700" fill="%s" %s>%d</text>'
                     % (x + bar_w / 2, base_y - bh - 8, INK if key == best_key else MUT,
                        anim("fadein", .5, .6 + i * .06), v))
        s.append('<text x="%.1f" y="%d" text-anchor="middle" class="fm" font-size="10" fill="%s">%s</text>'
                 % (x + bar_w / 2, base_y + 18, DIM, month_label(key)))
    rows = [
        (str(st["total"]), "TOTAL CONTRIBUTIONS"),
        (str(st["active"]), "ACTIVE DAYS"),
        ("%d days" % st["streak"], "LONGEST STREAK"),
        ("%d" % st["busiest"]["count"], "BUSIEST DAY &#183; %s" % fmt_date(st["busiest"]["date"]).upper()),
    ]
    y = 84
    for i, (num, label) in enumerate(rows):
        s.append('<g %s><text x="596" y="%d" class="fi" font-weight="800" font-size="24" fill="%s">%s</text>'
                 '<text x="596" y="%d" class="fm" font-size="10" letter-spacing="1.5" fill="%s">%s</text></g>'
                 % (anim("rise", .6, .3 + i * .12), y, INK, num, y + 18, MUT, label))
        y += 42
    s.append('<line x1="584" y1="58" x2="584" y2="206" stroke="%s"/>' % HAIR)
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- tiles
def countup(x, y, size, fill, values, begin, prefix=""):
    """SMIL count-up. The final value is visible by default (with a set that
    hides it until its turn), so the end state renders even without SMIL."""
    out = []
    step = 0.07
    for i, v in enumerate(values):
        last = i == len(values) - 1
        if last:
            sets = ('<set attributeName="visibility" to="hidden" begin="0s" dur="%.2fs"/>'
                    '<set attributeName="visibility" to="visible" begin="%.2fs"/>'
                    % (begin + i * step, begin + i * step))
            out.append('<text x="%s" y="%s" class="fi" font-weight="800" font-size="%s" fill="%s">%s%s%s</text>'
                       % (x, y, size, fill, prefix, v, sets))
        else:
            set_el = ('<set attributeName="visibility" to="visible" begin="%.2fs" dur="%.2fs"/>'
                      % (begin + i * step, step))
            out.append('<text x="%s" y="%s" class="fi" font-weight="800" font-size="%s" fill="%s" visibility="hidden">%s%s%s</text>'
                       % (x, y, size, fill, prefix, v, set_el))
    return "".join(out)


def tile(fname, idx, color, label, stat_values, stat_prefix, stat_label, lines, projects, delay):
    w, h = 270, 216
    s = [svg_open(w, h), style_block(INTER + MONO), card_bg(w, h)]
    s.append('<defs><clipPath id="clip"><rect width="%d" height="%d" rx="10"/></clipPath></defs>' % (w, h))
    s.append('<g %s>' % anim("swing", .85, delay))
    s.append('<rect x="-90" y="-20" width="64" height="280" fill="#ffffff" opacity="0.05" '
             'style="animation:sweep 5.5s ease-in-out infinite;animation-delay:%.1fs"/>' % (2.2 + delay))
    s.append('<text x="24" y="42" class="fm" font-size="12" font-weight="700" letter-spacing="2.5" fill="%s">%s</text>' % (color, label))
    s.append('<text x="246" y="42" text-anchor="end" class="fm" font-size="12" fill="%s">%s</text>' % (DIM, idx))
    s.append(countup(24, 108, 46, INK, stat_values, 0.55 + delay, prefix=stat_prefix))
    s.append('<text x="24" y="130" class="fm" font-size="10" letter-spacing="1.2" fill="%s">%s</text>' % (MUT, stat_label))
    s.append('<line x1="24" y1="146" x2="246" y2="146" stroke="%s"/>' % HAIR)
    for i, ln in enumerate(lines):
        s.append('<text x="24" y="%d" class="fi" font-size="13.5" fill="%s">%s</text>' % (168 + i * 20, BODY, ln))
    s.append('<text x="24" y="206" class="fm" font-size="10" fill="%s">%s</text>' % (DIM, projects))
    s.append('</g></svg>')
    return "".join(s)


# ---------------------------------------------------------------- projects
PROJECTS = [
    ("concurrent-http-server", "C", "#9e9e9e",
     ["HTTP/1.1 server from raw sockets in C: thread pool with a bounded work queue,",
      "128 striped per-file locks, strict request parsing, thread-safe audit log."]),
    ("air-mouse", "C", "#9e9e9e",
     ["Tilt-controlled Bluetooth mouse: an ESP32-C3 reads an ICM-42670 accelerometer",
      "over I2C and turns hand tilt into cursor movement."]),
    ("lightlink", "C", "#9e9e9e",
     ["Text messages over a beam of light: Morse code blinked on an LED, read by an",
      "ESP32-C3 light sensor and rebuilt by a timing state machine."]),
    ("Agent-Forge-AI-Hackathon", "Python", "#4b8bbe",
     ["AgentCheck, a multi-agent hiring pipeline (Python, FastAPI). Placed Top 20 of",
      "330+ participants at Agent Forge 2026 (Sunnyvale)."]),
]


def projects():
    w = 830
    row_h = 58
    h = 56 + sum(row_h + (len(p[3]) - 1) * 17 for p in PROJECTS) + 16
    s = [svg_open(w, h), style_block(INTER + MONO), card_bg(w, h)]
    s.append('<text x="40" y="38" class="fm" font-size="12" letter-spacing="2" fill="%s">FEATURED PROJECTS</text>' % MUT)
    s.append('<text x="790" y="38" text-anchor="end" class="fm" font-size="12" fill="%s">GITHUB.COM/ZEMEN14</text>' % DIM)
    y = 56
    for i, (name, lang, lang_color, desc) in enumerate(PROJECTS):
        s.append('<g %s>' % anim("rise", .6, .15 + i * .13))
        s.append('<circle cx="47" cy="%d" r="4" fill="%s"/>' % (y + 13, lang_color))
        s.append('<text x="60" y="%d" class="fi" font-weight="600" font-size="16.5" fill="%s">%s</text>'
                 % (y + 18, BLUE, name))
        name_w = 60 + len(name) * 8.9
        s.append('<text x="%.0f" y="%d" class="fm" font-size="11" fill="%s">%s</text>' % (name_w + 12, y + 18, MUT, lang))
        for j, ln in enumerate(desc):
            s.append('<text x="60" y="%d" class="fi" font-size="13.5" fill="%s">%s</text>' % (y + 38 + j * 17, BODY, ln))
        s.append('</g>')
        y += row_h + (len(desc) - 1) * 17
    s.append("</svg>")
    return "".join(s)


def main():
    os.makedirs(CARDS, exist_ok=True)
    contrib = load("contributions.json")
    user = load("user.json")
    st = stats(contrib)
    out = {
        "hero.svg": hero(user, st),
        "graph.svg": graph(contrib, st),
        "activity.svg": activity(st),
        "tile-embedded.svg": tile("tile-embedded.svg", "01", GREEN, "EMBEDDED",
                                  [0, 1, 2, 3, 4, 5], "", "FEATURED EMBEDDED BUILDS",
                                  ["ESP32-C3 &#183; ESP-IDF &#183; Arduino", "I2C &#183; SPI &#183; BLE &#183; sensors"],
                                  "AIR-MOUSE &#183; LIGHTLINK &#183; SONIC-RULER", 0.9),
        "tile-systems.svg": tile("tile-systems.svg", "02", BLUE, "SYSTEMS",
                                 [0, 18, 40, 64, 86, 104, 117, 124, 128], "", "STRIPED LOCKS &#183; HTTP/1.1 SERVER",
                                 ["C &#183; POSIX sockets &#183; pthreads", "Linux &#183; FPGA &#183; Vivado &#183; Basys 3"],
                                 "CONCURRENT-HTTP-SERVER", 1.05),
        "tile-software.svg": tile("tile-software.svg", "03", PURPLE, "SOFTWARE",
                                  [0, 4, 8, 12, 15, 18, 19, 20], "Top ", "OF 330+ &#183; AGENT FORGE 2026",
                                  ["Python &#183; FastAPI &#183; Java", "Multi-agent systems &#183; tooling"],
                                  "AGENTCHECK &#183; NOURI CARE", 1.2),
        "projects.svg": projects(),
    }
    for name, content in out.items():
        path = os.path.join(CARDS, name)
        with open(path, "w") as f:
            f.write(content)
        print(name, len(content), "bytes")
    print("stats:", {k: st[k] for k in ("total", "active", "streak")}, "busiest:", st["busiest"])
    print("months:", st["months"])


if __name__ == "__main__":
    main()
