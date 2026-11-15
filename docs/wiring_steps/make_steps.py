"""Top-view wiring pictures for the user's real breadboard, one finger at a time.

Layout (checked against the user's photos, 2026-11-15):
  * breadboard: columns 30 (left) .. 1 (right) when rows a-e are at the top
  * rails next to row a: + (red line) outer, - (blue line) inner;  rails next to row j: + inner, - outer (under the ESP32)
  * ESP32: VIN-side pins in row j, USB end at column 30 -> VIN 30, GND 29, D13 28, D12 27, D14 26, D27 25, D26 24, D25 23 ...
           the other pin row hangs in the air past the edge (below the breadboard in the picture)
  * index (done): black jumper row i col 29 (GND) -> - rail; yellow row i col 28 (D13) -> index servo orange
Run: python make_steps.py   -> step_<finger>.html (+ .png via render in the session)
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = 26                                   # px per hole
X0, Y0 = 70, 150                          # top-left of the breadboard
COLS = 30
col_x = lambda c: X0 + 30 + (COLS - c) * P          # column 30 at the left
ROWS_TOP = {"P_a": 0, "N_a": 1}                     # rail rows next to row a: + outer (top), - inner
row_y = {"P_a": Y0 + 18, "N_a": Y0 + 18 + P}
for k, r in enumerate("abcde"): row_y[r] = Y0 + 18 + 3 * P + k * P
for k, r in enumerate("fghij"): row_y[r] = row_y["e"] + 2.4 * P + k * P
row_y["P_j"] = row_y["j"] + 2 * P; row_y["N_j"] = row_y["P_j"] + P
BB_W, BB_H = 30 * P + 50, row_y["N_j"] + 26 - Y0
PIN_ORDER = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
pin_col = {p: 30 - i for i, p in enumerate(PIN_ORDER)}   # VIN 30 ... EN 16

# firmware check: finger pins
ino = open(os.path.join(HERE, "../../firmware/finger_control/finger_control.ino")).read()
FW = {m[0]: int(m[1]) for m in re.findall(r'\{"(\w+)",\s*(\d+),', ino)}
FINGER_PIN = {"Index": "D13", "Middle": "D14", "Ring": "D27", "Little": "D26", "Thumb": "D25"}
for f, p in FINGER_PIN.items():
    assert FW[f] == int(p[1:]), (f, FW[f], p)
assert pin_col["VIN"] == 30 and pin_col["GND"] == 29 and pin_col["D13"] == 28 and pin_col["D12"] == 27
# rail holes used per servo (brown -, red +): own holes, away from the supply (cols 1-4) and the GND jumper
SERVO_RAIL = {"Index": 12, "Middle": 17, "Ring": 20, "Little": 8, "Thumb": 6}
ORDER = ["Index", "Middle", "Ring", "Little", "Thumb"]
used = [SERVO_RAIL[f] for f in ORDER] + [1, 2, 3, 4, 29]
assert len(set(used)) == len(used), used


def hole(r, c): return col_x(c), row_y[r]


def svg(finger):
    done = ORDER[:ORDER.index(finger)]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{X0*2+BB_W+60}" height="{Y0+BB_H+210}" font-family="DejaVu Sans, Arial">']
    # breadboard
    o.append(f'<rect x="{X0}" y="{Y0}" width="{BB_W}" height="{BB_H}" rx="10" fill="#f6f6f2" stroke="#c9cfd3"/>')
    o.append(f'<rect x="{X0+8}" y="{(row_y["e"]+row_y["f"])/2-7}" width="{BB_W-16}" height="14" fill="#e3e3dc"/>')
    for r, colr, yy in (("P_a", "#d01f2f", row_y["P_a"] - 13), ("N_a", "#2a62c9", row_y["N_a"] + 13),
                        ("P_j", "#d01f2f", row_y["P_j"] - 13), ("N_j", "#2a62c9", row_y["N_j"] + 13)):
        o.append(f'<line x1="{X0+14}" x2="{X0+BB_W-14}" y1="{yy}" y2="{yy}" stroke="{colr}" stroke-width="3"/>')
    o.append(f'<text x="{X0-26}" y="{row_y["P_a"]+5}" fill="#d01f2f" font-size="22" font-weight="bold">+</text>')
    o.append(f'<text x="{X0-26}" y="{row_y["N_a"]+6}" fill="#2a62c9" font-size="24" font-weight="bold">−</text>')
    for r in list(row_y):
        for c in range(1, 31):
            x, y = hole(r, c)
            o.append(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" fill="#3a3a3a"/>')
        if len(r) == 1:
            o.append(f'<text x="{X0+10}" y="{row_y[r]+5}" font-size="14" fill="#555">{r}</text>')
    for c in range(1, 31):
        o.append(f'<text x="{col_x(c)}" y="{row_y["a"]-16}" font-size="12" fill="#444" text-anchor="middle">{c}</text>')
    # highlight the finger's column (rows f-j)
    c = pin_col[FINGER_PIN[finger]]
    o.append(f'<rect x="{col_x(c)-10}" y="{row_y["f"]-11}" width="20" height="{row_y["j"]-row_y["f"]+22}" rx="5" fill="#21c065" opacity=".35"/>')
    # ESP32: pins in row j, board hanging below
    ex0, ex1 = col_x(30) - 70, col_x(16) + 60
    ey0, ey1 = row_y["j"] - 18, row_y["j"] + 3.2 * P + 110
    o.append(f'<rect x="{ex0}" y="{ey0}" width="{ex1-ex0}" height="{ey1-ey0}" rx="8" fill="#1b1d22" opacity=".93"/>')
    o.append(f'<rect x="{ex0-14}" y="{ey0+70}" width="44" height="60" rx="6" fill="#b8bec4"/><text x="{ex0+8}" y="{ey0+150}" font-size="12" fill="#cfd6db" text-anchor="middle">USB</text>')
    o.append(f'<rect x="{col_x(23)}" y="{ey0+55}" width="{col_x(17)-col_x(23)+20}" height="{ey1-ey0-75}" rx="4" fill="#9aa0a6"/>')
    for p in PIN_ORDER:
        x, y = hole("j", pin_col[p])
        use = p in ("GND", "D13", "D14", "D27", "D26", "D25")
        fill = "#ffd27a" if p == FINGER_PIN[finger] or p == "GND" else ("#c9a64a" if use else "#777")
        o.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{fill}" stroke="#000" stroke-width="1"/>')
        o.append(f'<text x="{x}" y="{y+22}" font-size="11" fill="{"#ff5a6a" if p in ("VIN","D12") else "#e6ecef"}" text-anchor="end" transform="rotate(-90 {x} {y+22})">{p}</text>')
    o.append(f'<text x="{(ex0+ex1)/2+60}" y="{ey1-14}" font-size="13" fill="#9aa7b0" text-anchor="middle">ESP32 (hangs out past the edge; its other pin row touches nothing)</text>')

    def wire(a, b, color, w=5, dash="", op=1.0, drop=False):
        (x1, y1), (x2, y2) = a, b
        mx, my = ((x1, (y1 + y2) / 2 + 30) if drop else ((x1 + x2) / 2, min(y1, y2) - 60))
        o.append(f'<path d="M{x1},{y1} Q{mx},{my} {x2},{y2}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" {dash} opacity="{op}"/>')
        for x, y in (a, b):
            o.append(f'<rect x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="#111" opacity="{op}"/>')

    # power (always there, faded)
    sup = (col_x(1) + 70, row_y["P_a"] - 95)
    o.append(f'<text x="{sup[0]}" y="{sup[1]-14}" font-size="13" fill="#666" text-anchor="middle">to the 5 V adapter</text>')
    for c, r, colr in ((1, "P_a", "#d01f2f"), (2, "P_a", "#d01f2f"), (1, "N_a", "#22272b"), (3, "N_a", "#22272b")):
        x, y = hole(r, c); o.append(f'<path d="M{x},{y} L{sup[0]},{sup[1]}" stroke="{colr}" stroke-width="3" opacity=".35"/>')
        o.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="#111" opacity=".5"/>')
    x1, y1 = hole("P_a", 4); x2, y2 = hole("N_a", 4)
    o.append(f'<circle cx="{x1}" cy="{(y1+y2)/2}" r="15" fill="#24324f" opacity=".5"/><text x="{x1+22}" y="{(y1+y2)/2+5}" font-size="12" fill="#666">capacitor</text>')
    # GND jumper (done)
    wire(hole("i", 29), hole("N_a", 29), "#22272b", 4, op=.45)
    # finished servos (faded), current one bold
    for f in done + [finger]:
        cur = f == finger
        op, w = (1.0, 6) if cur else (.35, 4)
        srv = (col_x(SERVO_RAIL[f]) - 10, Y0 - 105)
        o.append(f'<rect x="{srv[0]-26}" y="{srv[1]-22}" width="52" height="26" rx="4" fill="{"#1d3f73" if cur else "#8090a8"}"/>')
        o.append(f'<text x="{srv[0]}" y="{srv[1]-4}" font-size="12" fill="#fff" text-anchor="middle">{f}</text>')
        row = "i" if f in ("Index", "Middle") else "g"   # as actually plugged (photos 2026-11-15)
        wire((srv[0] - 8, srv[1] + 6), hole("N_a", SERVO_RAIL[f]), "#6b4a2b", w, op=op, drop=True)
        wire((srv[0], srv[1] + 6), hole("P_a", SERVO_RAIL[f] - 1), "#d01f2f", w, op=op, drop=True)
        wire((srv[0] + 8, srv[1] + 6), hole(row, pin_col[FINGER_PIN[f]]), "#f07c18" if cur else "#e5b800", w, op=op, drop=True)
    # callouts for the current finger
    c = pin_col[FINGER_PIN[finger]]
    def tag(x, y, text, colr):
        o.append(f'<rect x="{x}" y="{y-18}" width="{9*len(text)+16}" height="26" rx="5" fill="{colr}"/><text x="{x+8}" y="{y}" font-size="15" font-weight="bold" fill="#fff">{text}</text>')
    xg, yg = hole("g", c); tag(xg + 14, yg + 4, f"orange → row g, column {c} ({FINGER_PIN[finger]})", "#d4620f")
    xb, yb = hole("N_a", SERVO_RAIL[finger]); tag(xb + 14, yb + 30, f"brown → − rail (blue), column {SERVO_RAIL[finger]}", "#6b4a2b")
    xr, yr = hole("P_a", SERVO_RAIL[finger] - 1); tag(xr + 14, yr - 26, f"red → + rail (red), column {SERVO_RAIL[finger]-1}", "#c9182f")
    o.append("</svg>")
    return "\n".join(o), c


def page(finger):
    s, c = svg(finger)
    n = ORDER.index(finger) + 1
    steps = f"""<ol>
<li><b>Power off:</b> USB out, adapter out of the wall. String slack.</li>
<li>Push 3 male-male jumpers into the <b>{finger}</b> servo's plug (brown, red, orange), tape the joint, label the cable "{finger}".</li>
<li><b>Brown</b> → the <b>blue (−)</b> rail row next to row a (any free hole, e.g. column {SERVO_RAIL[finger]}).</li>
<li><b>Red</b> → the <b>red (+)</b> rail row (any free hole, e.g. column {SERVO_RAIL[finger]-1}).</li>
<li><b>Orange</b> → <b>row g, column {c}</b>. Check: follow the ESP32 label <b>{FINGER_PIN[finger]}</b> straight up its column (green): it must be the same column.</li>
<li>Columns <b>30 (VIN)</b> and <b>27 (D12)</b> stay empty.</li></ol>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{finger} wiring</title>
<style>body{{margin:0;background:#eef1f3;font-family:"DejaVu Sans",Arial;color:#172026;width:1060px}}
h1{{font-size:26px;margin:16px 24px 2px}} .sub{{margin:0 24px;color:#4a5a64}} .wrap{{display:flex;gap:10px;align-items:flex-start}}
ol{{font-size:16px;line-height:1.5;margin:8px 24px 18px 24px;padding-left:22px}} .tag{{color:#c25a17;font-weight:bold;letter-spacing:.12em;font-size:13px;margin:16px 24px 0}}</style></head>
<body><div class="tag">ROBOHAND · WIRING STEP {n} OF 5 · TOP VIEW OF YOUR BREADBOARD</div><h1>{finger} finger servo → pin {FINGER_PIN[finger]} (column {c})</h1>
<p class="sub">Bold wires = this step. Faded = already done. Columns as printed on your breadboard (30 on the left, USB end of the ESP32).</p>
{s}{steps}</body></html>"""


if __name__ == "__main__":
    for f in sys.argv[1:] or ["Middle"]:
        open(os.path.join(HERE, f"step_{f.lower()}.html"), "w").write(page(f))
        print("wrote", f)
