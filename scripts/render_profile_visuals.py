#!/usr/bin/env python3
"""Render local animated SVG visuals for Arpit Jham's GitHub profile README.

Run from any directory with:
    python scripts/render_profile_visuals.py

Expected project layout:
    data/contributions.json
    scripts/render_profile_visuals.py

Outputs:
    activity-graph.svg
    assets/profile-hero.svg
    assets/profile-tagline.svg
    assets/section-about.svg
    assets/section-leadership.svg
    assets/section-skills.svg
    assets/section-projects.svg
    assets/section-achievements.svg
    assets/section-contributions.svg

Uses only Python's standard library. The line chart is generated locally, so
it does not depend on a third-party activity-graph hosting service.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "contributions.json"
ASSETS = ROOT / "assets"

NAVY = "#08111F"
PANEL = "#0E1B2D"
PANEL_2 = "#10243B"
BLUE = "#60A5FA"
CYAN = "#22D3EE"
TEAL = "#2DD4BF"
VIOLET = "#A78BFA"
GOLD = "#FBBF24"
TEXT = "#E6F1FF"
MUTED = "#9FB3C8"
BORDER = "#29415A"


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def hero_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="244" viewBox="0 0 1200 244" role="img" aria-labelledby="title desc">
<title id="title">Arpit Jham — Team Lead, Full-Stack Developer, AI Product Engineering</title>
<desc id="desc">A premium animated midnight-navy banner with a visibly cursive gradient name, elegant serif subtitle, and flowing light trails.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#080D1B"/><stop offset=".46" stop-color="#102C48"/><stop offset="1" stop-color="#075E61"/></linearGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F8FAFC"/><stop offset=".42" stop-color="#93C5FD"/><stop offset=".72" stop-color="#67E8F9"/><stop offset="1" stop-color="#5EEAD4"/></linearGradient>
  <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#60A5FA" stop-opacity="0"/><stop offset=".5" stop-color="#22D3EE" stop-opacity=".95"/><stop offset="1" stop-color="#A78BFA" stop-opacity="0"/></linearGradient>
  <radialGradient id="orb"><stop offset="0" stop-color="#22D3EE" stop-opacity=".25"/><stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>
  <clipPath id="round"><rect x="0" y="0" width="1200" height="244" rx="18"/></clipPath>
  <filter id="glow" x="-20%" y="-35%" width="140%" height="170%"><feGaussianBlur stdDeviation="3.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  .orb1{{animation:drift1 11s ease-in-out infinite alternate;transform-origin:center}}
  .orb2{{animation:drift2 14s ease-in-out infinite alternate;transform-origin:center}}
  .trail{{animation:trace 5.6s ease-in-out infinite}}
  .hero{{opacity:1;animation:enter 1s cubic-bezier(.2,.8,.2,1) .12s both}}
  .sub{{opacity:1;animation:enter .85s ease-out .58s both}}
  .accent{{animation:pulse 3.4s ease-in-out infinite}}
  .name-glint{{animation:glint 5s ease-in-out infinite}}
  @keyframes drift1{{from{{transform:translate(-30px,8px)}}to{{transform:translate(80px,-18px)}}}}
  @keyframes drift2{{from{{transform:translate(45px,-8px)}}to{{transform:translate(-60px,18px)}}}}
  @keyframes trace{{0%{{transform:translateX(-900px);opacity:0}}20%{{opacity:.95}}70%{{opacity:.8}}100%{{transform:translateX(1300px);opacity:0}}}}
  @keyframes enter{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
  @keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
  @keyframes glint{{0%,14%{{opacity:0;transform:translateX(-260px)}}35%{{opacity:.7}}62%,100%{{opacity:0;transform:translateX(310px)}}}}
  @media (prefers-reduced-motion:reduce){{.orb1,.orb2,.trail,.hero,.sub,.accent,.name-glint{{animation:none!important;opacity:1!important;transform:none!important}}}}
</style>
<g clip-path="url(#round)">
  <rect width="1200" height="244" fill="url(#bg)"/>
  <circle class="orb1" cx="235" cy="30" r="270" fill="url(#orb)"/>
  <circle class="orb2" cx="1040" cy="240" r="360" fill="url(#orb)"/>
  <path d="M0 190 C175 146 300 226 470 184 S780 150 930 192 S1100 228 1200 168 V244 H0Z" fill="#08111F" opacity=".36"/>
  <path d="M0 208 C160 170 290 230 460 199 S780 172 960 210 S1100 220 1200 197" fill="none" stroke="#38BDF8" stroke-opacity=".28" stroke-width="1.5"/>
  <g class="trail"><path d="M0 199 H1200" stroke="url(#trail)" stroke-width="2.2" filter="url(#glow)"/></g>
  <g class="hero" text-anchor="middle">
    <text x="600" y="104" font-family="'Segoe Script','Brush Script MT','Lucida Handwriting',cursive" font-size="76" font-style="italic" font-weight="600" letter-spacing="1.1" fill="url(#name)" filter="url(#glow)">Arpit Jham</text>
    <text class="name-glint" x="600" y="104" font-family="'Segoe Script','Brush Script MT','Lucida Handwriting',cursive" font-size="76" font-style="italic" font-weight="600" letter-spacing="1.1" fill="none" stroke="#E0F2FE" stroke-opacity=".38" stroke-width=".7">Arpit Jham</text>
  </g>
  <g class="sub" text-anchor="middle" font-family="'Times New Roman',Georgia,serif">
    <text x="600" y="151" font-size="23" font-weight="700" letter-spacing=".55" fill="#F0F7FF">TEAM LEAD  ·  FULL-STACK DEVELOPER  ·  AI PRODUCT ENGINEERING</text>
  </g>
  <path class="accent" d="M315 219 C450 219 490 225 600 219 S750 213 885 219" fill="none" stroke="url(#trail)" stroke-width="2.8" stroke-linecap="round"/>
</g>
</svg>'''


def tagline_svg() -> str:
    phrases = [
        "BUILDING SCALABLE PROJECTS",
        "DESIGNING PREMIUM USER INTERFACES",
        "LEAD DEVELOPER · AI PRODUCT ENGINEERING",
    ]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="82" viewBox="0 0 1200 82" role="img" aria-labelledby="title desc">
<title id="title">Arpit Jham — rotating developer tagline</title>
<desc id="desc">Transparent animated type that cycles between building scalable projects, designing premium user interfaces, and lead developer and AI product engineering.</desc>
<defs>
 <linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#60A5FA"/><stop offset=".46" stop-color="#22D3EE"/><stop offset="1" stop-color="#5EEAD4"/></linearGradient>
 <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".8"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
 <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#60A5FA" stop-opacity=".12"/><stop offset=".5" stop-color="#22D3EE" stop-opacity=".75"/><stop offset="1" stop-color="#5EEAD4" stop-opacity=".12"/></linearGradient>
 <filter id="softglow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3.1" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
 .phrase{{font-family:'Times New Roman',Georgia,serif;font-size:25px;font-weight:700;font-style:italic;letter-spacing:1.7px;fill:url(#g);filter:url(#softglow)}}
 .shine{{animation:scan 4.8s ease-in-out infinite}}
 .underline{{stroke-dasharray:250;stroke-dashoffset:250;animation:draw 4s ease-in-out infinite}}
 @keyframes scan{{0%{{transform:translateX(-550px);opacity:0}}22%{{opacity:.85}}58%{{opacity:0}}100%{{transform:translateX(550px);opacity:0}}}}
 @keyframes draw{{0%,8%{{stroke-dashoffset:250;opacity:.25}}42%,60%{{stroke-dashoffset:0;opacity:.9}}100%{{stroke-dashoffset:-250;opacity:.2}}}}
 @media (prefers-reduced-motion:reduce){{.shine,.underline{{animation:none}}.shine{{opacity:.25}}.underline{{stroke-dashoffset:0}}}}
</style>
<!-- Transparent canvas: only the type, a faint baseline, and moving light are rendered. -->
<text class="phrase" x="600" y="42" text-anchor="middle" opacity="1">{html.escape(phrases[0])}<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.04;.25;.32;1" dur="9s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 9;0 0;0 0;0 -8;0 -8" keyTimes="0;.04;.25;.32;1" dur="9s" repeatCount="indefinite"/></text>
<text class="phrase" x="600" y="42" text-anchor="middle" opacity="0">{html.escape(phrases[1])}<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.32;.37;.60;.66;1" dur="9s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 9;0 9;0 0;0 0;0 -8;0 -8" keyTimes="0;.32;.37;.60;.66;1" dur="9s" repeatCount="indefinite"/></text>
<text class="phrase" x="600" y="42" text-anchor="middle" opacity="0">{html.escape(phrases[2])}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.66;.71;.94;1" dur="9s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 9;0 9;0 0;0 0;0 -8" keyTimes="0;.66;.71;.94;1" dur="9s" repeatCount="indefinite"/></text>
<path d="M150 66 H1050" stroke="url(#line)" stroke-width="1.5" stroke-linecap="round"/>
<path class="underline" d="M300 66 H900" stroke="url(#g)" stroke-width="2.1" stroke-linecap="round" fill="none"/>
<rect class="shine" x="0" y="64" width="300" height="4" rx="2" fill="url(#shine)"/>
</svg>'''

SECTIONS = [
    ("section-about.svg", "01", "ABOUT", BLUE, 0.08),
    ("section-leadership.svg", "02", "LEADERSHIP EXPERIENCE", TEAL, 0.16),
    ("section-skills.svg", "03", "TECHNICAL SKILLS", VIOLET, 0.24),
    ("section-projects.svg", "04", "FEATURED PROJECTS", CYAN, 0.32),
    ("section-achievements.svg", "05", "ACHIEVEMENTS", GOLD, 0.40),
    ("section-contributions.svg", "06", "CONTRIBUTIONS", BLUE, 0.48),
]


def section_svg(number: str, label: str, accent: str, delay: float) -> str:
    safe_label = html.escape(label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="72" viewBox="0 0 1100 72" role="img" aria-labelledby="title">
<title id="title">{number} — {safe_label}</title>
<defs><linearGradient id="panel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}" stop-opacity=".20"/><stop offset=".55" stop-color="{PANEL}" stop-opacity=".96"/><stop offset="1" stop-color="{PANEL_2}"/></linearGradient><linearGradient id="beam"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient></defs>
<style>
 .card{{opacity:1;transform:translateX(0);animation:slide .72s cubic-bezier(.2,.8,.2,1) {delay}s both}}
 .beam{{stroke-dasharray:260;stroke-dashoffset:260;animation:draw 1.45s ease-out {delay + 0.22:.2f}s forwards}}
 .dot{{animation:blink 2.8s ease-in-out {delay:.2f}s infinite}}
 @keyframes slide{{from{{opacity:0;transform:translateX(-26px)}}to{{opacity:1;transform:translateX(0)}}}}
 @keyframes draw{{to{{stroke-dashoffset:0}}}}
 @keyframes blink{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
 @media (prefers-reduced-motion:reduce){{.card{{opacity:1;transform:none;animation:none}}.beam{{stroke-dashoffset:0;animation:none}}.dot{{animation:none;opacity:1}}}}
</style>
<g class="card">
 <rect x="2" y="2" width="1096" height="68" rx="13" fill="url(#panel)" stroke="{BORDER}" stroke-opacity=".95"/>
 <rect x="2" y="2" width="6" height="68" rx="3" fill="{accent}"/>
 <text x="33" y="44" font-family="Segoe UI,Arial,sans-serif" font-size="17" font-weight="800" fill="{accent}" letter-spacing="2">{number}</text>
 <text x="88" y="44" font-family="Segoe UI,Arial,sans-serif" font-size="24" font-weight="750" fill="{TEXT}" letter-spacing="1.2">{safe_label}</text>
 <path d="M87 57 H1060" stroke="{BORDER}" stroke-width="1.2"/>
 <path class="beam" d="M87 57 H350" stroke="url(#beam)" stroke-width="2.8" stroke-linecap="round"/>
 <circle class="dot" cx="1060" cy="36" r="5" fill="{accent}"/>
 <circle cx="1060" cy="36" r="10" fill="none" stroke="{accent}" stroke-opacity=".32"/>
</g>
</svg>'''


def activity_graph_svg(data: dict) -> str:
    all_days = data.get("days", [])
    if not isinstance(all_days, list) or not all_days:
        raise ValueError(f"No daily entries found in {DATA_PATH}. Run fetch_contributions.py first.")

    days = all_days[-31:]
    points_data = []
    for item in days:
        try:
            day = dt.date.fromisoformat(str(item["date"]))
            count = max(0, int(item.get("count", 0)))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid contribution-day entry: {item!r}") from exc
        points_data.append((day, count))

    width, height = 1120, 340
    left, right, top, bottom = 76.0, 1084.0, 76.0, 256.0
    max_value = max((count for _, count in points_data), default=0)
    # Give low-volume days some breathing room without duplicated tick labels.
    if max_value <= 6:
        scale_max = max(2, max_value + 1)
    else:
        scale_max = math.ceil(max_value / 5) * 5

    coords: list[tuple[float, float, int]] = []
    denominator = max(1, len(points_data) - 1)
    for i, (_, count) in enumerate(points_data):
        x = left + (right - left) * i / denominator
        y = bottom - (bottom - top) * count / scale_max
        coords.append((x, y, count))

    # Cubic Bezier segments pass through the real observations while rounding
    # transitions at isolated peaks. Control points are clamped to the segment.
    def smooth_path(points: list[tuple[float, float, int]]) -> tuple[str, float]:
        if not points:
            return "", 0.0
        if len(points) == 1:
            return f"M {points[0][0]:.2f} {points[0][1]:.2f}", 1.0
        commands = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
        curve_length = 0.0
        for i in range(len(points) - 1):
            p0 = points[max(0, i - 1)]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[min(len(points) - 1, i + 2)]
            c1x = p1[0] + (p2[0] - p0[0]) / 6
            c1y = p1[1] + (p2[1] - p0[1]) / 6
            c2x = p2[0] - (p3[0] - p1[0]) / 6
            c2y = p2[1] - (p3[1] - p1[1]) / 6
            low_y, high_y = sorted((p1[1], p2[1]))
            c1y = max(low_y, min(high_y, c1y))
            c2y = max(low_y, min(high_y, c2y))
            commands.append(f"C {c1x:.2f} {c1y:.2f}, {c2x:.2f} {c2y:.2f}, {p2[0]:.2f} {p2[1]:.2f}")

            # Numerically estimate this cubic segment's arc length so the stroke
            # draw animation reaches the true end of the smoother curve.
            previous = (p1[0], p1[1])
            for step in range(1, 25):
                t = step / 24
                u = 1 - t
                x = u**3 * p1[0] + 3*u*u*t*c1x + 3*u*t*t*c2x + t**3*p2[0]
                y = u**3 * p1[1] + 3*u*u*t*c1y + 3*u*t*t*c2y + t**3*p2[1]
                curve_length += math.hypot(x - previous[0], y - previous[1])
                previous = (x, y)
        return " ".join(commands), max(curve_length, 1.0)

    path_d, path_len = smooth_path(coords)
    area_d = f"{path_d} L {coords[-1][0]:.2f} {bottom:.2f} L {coords[0][0]:.2f} {bottom:.2f} Z"

    if scale_max <= 6:
        tick_values = list(range(scale_max, -1, -1))
    else:
        tick_values = sorted(set([scale_max, round(scale_max * .75), round(scale_max * .5), round(scale_max * .25), 0]), reverse=True)

    grid = []
    for val in tick_values:
        y = bottom - (bottom - top) * val / scale_max
        grid.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="{BORDER}" stroke-opacity=".66" stroke-dasharray="3 8"/>')
        grid.append(f'<text x="{left-20}" y="{y+4:.2f}" text-anchor="end" fill="{MUTED}" font-size="12">{val}</text>')

    xticks = []
    tick_indexes = sorted(set([0, 7, 14, 21, min(30, len(coords) - 1)]))
    for idx in tick_indexes:
        if 0 <= idx < len(points_data):
            date = points_data[idx][0]
            x = coords[idx][0]
            label = date.strftime("%b ") + str(date.day)
            xticks.append(f'<text x="{x:.2f}" y="294" text-anchor="middle" fill="{MUTED}" font-size="12">{html.escape(label)}</text>')

    markers = []
    n = max(1, len(coords) - 1)
    for i, (x, y, count) in enumerate(coords):
        delay = 0.35 + (i / n) * 1.75
        if count > 0:
            markers.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="8.5" fill="{CYAN}" opacity=".12"><animate attributeName="opacity" values=".04;.22;.08" dur="3s" begin="{delay:.2f}s" repeatCount="indefinite"/></circle>')
            radius, fill = 4.5, CYAN
        else:
            radius, fill = 2.35, BLUE
        markers.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{fill}" stroke="{NAVY}" stroke-width="1.3"><animate attributeName="r" values="{radius-0.5};{radius};{radius-0.5}" dur="3.4s" begin="{delay:.2f}s" repeatCount="indefinite"/></circle>')

    last_total = sum(count for _, count in points_data)
    start_label = points_data[0][0].strftime("%b ") + str(points_data[0][0].day)
    end_label = points_data[-1][0].strftime("%b ") + str(points_data[-1][0].day)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="340" viewBox="0 0 1120 340" role="img" aria-labelledby="title desc">
<title id="title">GitHub contributions over the last 31 days</title>
<desc id="desc">A smooth line chart based on {len(points_data)} daily contribution records from {html.escape(start_label)} to {html.escape(end_label)}. Total activity during this period: {last_total} contributions.</desc>
<defs>
 <linearGradient id="chartbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{NAVY}"/></linearGradient>
 <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/><stop offset=".48" stop-color="{CYAN}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>
 <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".23"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".01"/></linearGradient>
 <filter id="softglow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="2.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
 .line{{stroke-dasharray:{path_len:.1f};stroke-dashoffset:{path_len:.1f};animation:draw 2.8s cubic-bezier(.3,.7,.2,1) .25s forwards}}
 .area{{opacity:0;animation:fade 1.3s ease-out .65s forwards}}
 .header{{opacity:0;animation:up .65s ease-out .12s forwards}}
 @keyframes draw{{to{{stroke-dashoffset:0}}}} @keyframes fade{{to{{opacity:.58}}}} @keyframes up{{from{{opacity:0;transform:translateY(7px)}}to{{opacity:1;transform:translateY(0)}}}}
 @media (prefers-reduced-motion:reduce){{.line{{stroke-dashoffset:0;animation:none}}.area,.header{{opacity:1;animation:none}}}}
</style>
<rect x="1" y="1" width="1118" height="338" rx="18" fill="url(#chartbg)" stroke="{BORDER}"/>
<circle cx="22" cy="22" r="4" fill="#FF6B6B"/><circle cx="37" cy="22" r="4" fill="{GOLD}"/><circle cx="52" cy="22" r="4" fill="{TEAL}"/>
<g class="header" font-family="Segoe UI,Arial,sans-serif"><text x="76" y="27" fill="{TEXT}" font-size="13" font-weight="700" letter-spacing="1.1">GITHUB ACTIVITY</text><text x="76" y="47" fill="{MUTED}" font-size="11">{html.escape(start_label)} — {html.escape(end_label)} · {last_total} contributions</text><text x="1084" y="28" fill="{TEAL}" font-size="12" text-anchor="end">LAST 31 DAYS</text></g>
{''.join(grid)}
<path class="area" d="{area_d}" fill="url(#area)"/>
<path class="line" d="{path_d}" fill="none" stroke="url(#line)" stroke-width="3.1" stroke-linecap="round" stroke-linejoin="round" filter="url(#softglow)"/>
{''.join(markers)}
{''.join(xticks)}
<text x="1084" y="322" text-anchor="end" fill="{MUTED}" font-size="11">LOCAL · DAILY ACTIVITY SNAPSHOT</text>
</svg>'''


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit(f"Contribution data not found: {DATA_PATH}\nRun: python scripts/fetch_contributions.py")
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not parse {DATA_PATH}: {exc}") from exc

    ASSETS.mkdir(parents=True, exist_ok=True)
    write_svg(ASSETS / "profile-hero.svg", hero_svg())
    write_svg(ASSETS / "profile-tagline.svg", tagline_svg())
    for filename, number, label, accent, delay in SECTIONS:
        write_svg(ASSETS / filename, section_svg(number, label, accent, delay))
    graph = activity_graph_svg(data)
    write_svg(ROOT / "activity-graph.svg", graph)

    print("Generated profile visuals:")
    print(f"  {ASSETS / 'profile-hero.svg'}")
    print(f"  {ASSETS / 'profile-tagline.svg'}")
    for filename, *_ in SECTIONS:
        print(f"  {ASSETS / filename}")
    print(f"  {ROOT / 'activity-graph.svg'}")


if __name__ == "__main__":
    main()
