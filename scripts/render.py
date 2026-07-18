#!/usr/bin/env python3
"""Render the profile's SVGs: terminal window, contributions chart, stats.

Everything is drawn as self-contained SVGs (GitHub does not render ANSI
colors in README code fences, and external card services are flaky).
Runs in GitHub Actions with GITHUB_TOKEN; without a token it renders
placeholders so no image is ever broken. Stdlib only.
"""
import json
import os
import urllib.request
from xml.sax.saxutils import escape

LOGIN = "DimPourn"
ASSETS = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))

# ── palette (GitHub dark, so the images blend into the profile page) ──
BG = "#0d1117"
BORDER = "#30363d"
FG = "#e6edf3"
DIM = "#8b949e"
CYAN = "#4dd8e6"
GREEN = "#3fb950"
BRIGHT = "#f0f6fc"
CAL = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]  # GitHub's own greens

FONT = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"
FS = 13          # font size
LH = 19          # line height
CW = 7.85        # approx monospace char width at FS

LEVEL_NAMES = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
               "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def gql(token, query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": "bearer " + token,
                 "Content-Type": "application/json", "User-Agent": LOGIN})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["data"]


# ══ shared chrome ═══════════════════════════════════════════════════

def window(width, height, title, body, extra_css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(title)}">
  <style>
    text{{font-family:{FONT};font-size:{FS}px;fill:{FG}}}
    .f{{opacity:0;animation:fi .5s ease forwards}}
    @keyframes fi{{to{{opacity:1}}}}
    .cur{{animation:bl 1.1s steps(1) infinite}}
    @keyframes bl{{50%{{opacity:0}}}}
    @media (prefers-reduced-motion:reduce){{.f{{opacity:1;animation:none}}.cur{{animation:none}}}}
    {extra_css}
  </style>
  <rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <circle cx="22" cy="19" r="5.5" fill="#f85149"/>
  <circle cx="42" cy="19" r="5.5" fill="#d29922"/>
  <circle cx="62" cy="19" r="5.5" fill="#3fb950"/>
  <text x="{width / 2}" y="23" text-anchor="middle" fill="{DIM}" style="font-size:12px">{escape(title)}</text>
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="{BORDER}"/>
  {body}
</svg>
"""


def tline(x, y, segments, delay, cls="f"):
    """One terminal line at (x, y). segments = [(text, color, bold), ...]"""
    bold_attr = ' font-weight="600"'
    spans = "".join(
        f'<tspan fill="{c}"{bold_attr if b else ""}>{escape(t)}</tspan>'
        for t, c, b in segments)
    return f'<text class="{cls}" x="{x}" y="{y}" style="animation-delay:{delay:.2f}s" xml:space="preserve">{spans}</text>'


def prompt(cmd):
    return [("dimitris@sec", CYAN, True), (":", FG, False), ("~", CYAN, False),
            ("$ ", FG, False), (cmd, BRIGHT, False)]


# ══ terminal.svg — neofetch + mission + nmap ═══════════════════════

ART = [
    "        ▄▄██████▄▄        ",
    "      ███▀▀    ▀▀███      ",
    "     ███          ███     ",
    "     ███          ███     ",
    "     ███          ███     ",
    "  ▄████████████████████▄  ",
    "  ██████████████████████  ",
    "  ████████▀▀▀▀▀▀████████  ",
    "  ███████  ▄██▄  ███████  ",
    "  ████████ ▀██▀ ████████  ",
    "  █████████ ██ █████████  ",
    "  ██████████████████████  ",
    "  ▀████████████████████▀  ",
    "",
    "     [ DP//SEC v2.0 ]",
]

def kv(key, val):
    return [(key.ljust(11), GREEN, True), (val, FG, False)]

INFO = [
    [("dimitris", CYAN, True), ("@", FG, False), ("DimPourn", CYAN, True)],
    [("─" * 18, DIM, False)],
    kv("Now", "Information Science @ AUEB — cybersecurity path"),
    kv("Focus", "Network security · GRC · pentest labs"),
    kv("Base", "Athens, GR"),
    [],
    [("Stack", BRIGHT, True)],
    kv("Security", "Nmap · Metasploit · Hydra · Wireshark · fail2ban"),
    kv("Infra", "Docker · Tailscale / WireGuard · Pi-hole · Unbound"),
    kv("Code", "Python · Java · Bash"),
    kv("Env", "Kali Linux · VirtualBox · Raspberry Pi 5"),
    [],
    [("Highlights", BRIGHT, True)],
    [("• ", GREEN, True), ("Built & hardened a self-hosted homelab, then attacked it", FG, False)],
    [("• ", GREEN, True), ("Exploitation range: vsftpd 2.3.4 backdoor → root ", FG, False), ("(sandboxed)", DIM, False)],
    [("• ", GREEN, True), ("CV runs like a secure phone OS", FG, False)],
    [],
    kv("Langs", "GR ●●●●● · EN ●●●●● · JP ●●●○○"),
]

MISSION = [
    "Building secure infrastructure and then attacking it —",
    "the two halves of understanding how things actually break.",
    "Open to security internships & junior roles · Athens / remote.",
]


def render_terminal():
    width, x0 = 880, 24
    art_x, info_x = x0, x0 + int(26 * CW) + 30
    body, y, d = [], 38 + 30, 0.0

    def emit(x, segs, step=True):
        nonlocal y, d
        body.append(tline(x, y, segs, d))
        if step:
            y += LH
        d += 0.055

    emit(x0, prompt("neofetch"))
    y += 6
    top = y
    for i, line in enumerate(ART):
        if line:
            body.append(tline(art_x, top + i * LH, [(line, CYAN, False)], 0.3 + i * 0.05))
    for i, segs in enumerate(INFO):
        if segs:
            body.append(tline(info_x, top + i * LH, segs, 0.35 + i * 0.05))
    rows = max(len(ART), len(INFO))
    y = top + rows * LH + 8
    d = 0.35 + rows * 0.05

    emit(x0, prompt("cat mission.txt"))
    for m in MISSION:
        emit(x0, [(m, DIM, False)])
    y += 6
    emit(x0, prompt("nmap -sV dimitris"))
    emit(x0, [("PORT     STATE  SERVICE", DIM, False)])
    emit(x0, [("443/tcp  ", FG, False), ("open", GREEN, True), ("   always-learning", FG, False)])
    y += 6
    emit(x0, prompt(""), step=False)
    body.append(f'<rect class="f cur" x="{x0 + 15 * CW + 8:.0f}" y="{y - FS + 1}" '
                f'width="8" height="{FS + 2}" fill="{CYAN}" style="animation-delay:{d:.2f}s"/>')
    height = y + 26
    return window(width, height, "dimitris@sec — zsh", "\n  ".join(body))


# ══ contributions.svg — GitHub-green fading calendar ═══════════════

CAL_QUERY = """
query($login: String!) { user(login: $login) { contributionsCollection {
  contributionCalendar { totalContributions
    weeks { contributionDays { contributionLevel } } } } } }
"""

def render_contributions(token):
    weeks, total = [[0] * 7 for _ in range(53)], None
    if token:
        try:
            cal = gql(token, CAL_QUERY, {"login": LOGIN})["user"]["contributionsCollection"]["contributionCalendar"]
            weeks = [[LEVEL_NAMES.get(day["contributionLevel"], 0)
                      for day in w["contributionDays"]] for w in cal["weeks"]]
            total = cal["totalContributions"]
        except Exception as exc:
            print(f"calendar fetch failed ({exc}); placeholder")
    cell, gap, x0, top = 11, 3, 24, 38 + 30
    cols = len(weeks)
    width = max(880, x0 * 2 + cols * (cell + gap) - gap)
    x0 = (width - (cols * (cell + gap) - gap)) // 2
    body = [tline(24, 38 + 24, prompt("./contributions.sh"), 0)]
    for wi, week in enumerate(weeks):
        delay = 0.25 + wi * 0.02
        for di, level in enumerate(week):
            body.append(f'<rect class="f" x="{x0 + wi * (cell + gap)}" y="{top + 14 + di * (cell + gap)}" '
                        f'width="{cell}" height="{cell}" rx="2.5" fill="{CAL[level]}" '
                        f'style="animation-delay:{delay:.2f}s"/>')
    y = top + 14 + 7 * (cell + gap) + 18
    label = f"{total} contributions in the last year" if total is not None else "contributions sync pending…"
    body.append(tline(width - x0 - len(label) * CW, y, [(label, DIM, False)], 0.25 + cols * 0.02 + 0.4))
    return window(width, y + 18, "dimitris@sec — contributions", "\n  ".join(body))


# ══ stats.svg — repos / stars / followers / language bar ═══════════

STATS_QUERY = """
query($login: String!) { user(login: $login) {
  contributionsCollection { contributionCalendar { totalContributions } }
  repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) {
    totalCount
    nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
      edges { size node { name color } } } } } } }
"""

def render_stats(token):
    repos = contribs = 0
    langs = {}
    if token:
        try:
            u = gql(token, STATS_QUERY, {"login": LOGIN})["user"]
            contribs = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            repos = u["repositories"]["totalCount"]
            for node in u["repositories"]["nodes"]:
                for e in node["languages"]["edges"]:
                    name, color = e["node"]["name"], e["node"]["color"] or DIM
                    size, _ = langs.get(name, (0, color))
                    langs[name] = (size + e["size"], color)
        except Exception as exc:
            print(f"stats fetch failed ({exc}); placeholder")

    width, x0 = 880, 24
    body, y = [], 38 + 24
    body.append(tline(x0, y, prompt("./stats.sh --all"), 0))
    y += LH + 8
    body.append(tline(x0, y, [
        ("Public repos ", DIM, False), (str(repos), BRIGHT, True),
        ("   Contributions (last year) ", DIM, False), (str(contribs), BRIGHT, True),
        ("   Base ", DIM, False), ("Athens, GR", BRIGHT, True),
    ], 0.15))
    y += LH + 10

    top5 = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]
    total_size = sum(s for s, _ in (v for _, v in top5)) or 1
    body.append(tline(x0, y, [("Top languages", BRIGHT, True)], 0.3))
    y += 12
    bar_w, bx = width - 2 * x0, x0
    if top5:
        for i, (name, (size, color)) in enumerate(top5):
            w = bar_w * size / total_size
            body.append(f'<rect class="f" x="{bx:.1f}" y="{y}" width="{max(w - 2, 2):.1f}" height="10" rx="3" '
                        f'fill="{color}" style="animation-delay:{0.4 + i * 0.12:.2f}s"/>')
            bx += w
        y += 26
        legend = []
        for name, (size, color) in top5:
            legend += [("● ", color, False), (f"{name} {100 * size / total_size:.0f}%  ", DIM, False)]
        body.append(tline(x0, y, legend, 0.9))
    else:
        body.append(tline(x0, y + 8, [("language sync pending…", DIM, False)], 0.4))
        y += 26
    return window(width, y + 26, "dimitris@sec — stats", "\n  ".join(body))


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    os.makedirs(ASSETS, exist_ok=True)
    for name, svg in (("terminal.svg", render_terminal()),
                      ("contributions.svg", render_contributions(token)),
                      ("stats.svg", render_stats(token))):
        path = os.path.join(ASSETS, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
