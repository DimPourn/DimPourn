#!/usr/bin/env python3
"""Render the GitHub contribution calendar as an animated SVG.

Cells fade in column-by-column (left to right) when the profile loads.
Runs inside GitHub Actions with GITHUB_TOKEN; with no token it renders
an empty placeholder grid so the README image is never broken.
Stdlib only — no dependencies.
"""
import datetime
import json
import os
import urllib.request

LOGIN = "DimPourn"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "contributions.svg")

# cyan scale on dark, matching the CV site palette
LEVEL_COLORS = ["#101a2e", "#0b4a55", "#0e7490", "#22d3ee", "#7ff3ff"]
LEVEL_NAMES = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
               "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionLevel date } }
      }
    }
  }
}
"""


def fetch_calendar(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": "bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": LOGIN},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[LEVEL_NAMES.get(d["contributionLevel"], 0)
              for d in w["contributionDays"]] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def placeholder_calendar():
    return [[0] * 7 for _ in range(53)], 0


def render(weeks, total):
    cell, gap, pad_x, pad_top, pad_bottom = 10, 3, 14, 34, 30
    cols = len(weeks)
    width = pad_x * 2 + cols * (cell + gap) - gap
    height = pad_top + 7 * (cell + gap) - gap + pad_bottom

    rects = []
    for wi, week in enumerate(weeks):
        delay = 0.25 + wi * 0.022
        for di, level in enumerate(week):
            x = pad_x + wi * (cell + gap)
            y = pad_top + di * (cell + gap)
            rects.append(
                f'<rect class="c" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{LEVEL_COLORS[level]}" style="animation-delay:{delay:.3f}s"/>'
            )
    sweep_end = 0.25 + cols * 0.022 + 0.5
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{total} contributions in the last year">
  <style>
    .c{{opacity:0;animation:fadein .55s ease forwards}}
    .t{{opacity:0;animation:fadein .8s ease forwards;font:600 12px ui-monospace,SFMono-Regular,Menlo,monospace}}
    @keyframes fadein{{to{{opacity:1}}}}
    @media (prefers-reduced-motion: reduce){{.c,.t{{opacity:1;animation:none}}}}
  </style>
  <rect width="{width}" height="{height}" rx="8" fill="#070a18"/>
  <text class="t" x="{pad_x}" y="21" fill="#22d3ee">dimitris@sec:~$ ./contributions.sh</text>
  {''.join(rects)}
  <text class="t" x="{width - pad_x}" y="{height - 11}" text-anchor="end" fill="#7e89ab" style="animation-delay:{sweep_end:.2f}s">{total} contributions in the last year</text>
</svg>
"""


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            weeks, total = fetch_calendar(token)
        except Exception as exc:  # keep the README image alive on API hiccups
            print(f"fetch failed ({exc}); rendering placeholder grid")
            weeks, total = placeholder_calendar()
    else:
        weeks, total = placeholder_calendar()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(weeks, total))
    print(f"wrote {OUT} ({len(weeks)} weeks, {total} contributions)")


if __name__ == "__main__":
    main()
