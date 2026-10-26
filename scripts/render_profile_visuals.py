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
<desc id="desc">An animated midnight-blue and teal profile banner with moving light trails.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#080D1B"/><stop offset=".48" stop-color="#123451"/><stop offset="1" stop-color="#075E61"/></linearGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F8FAFC"/><stop offset=".48" stop-color="#93C5FD"><animate attributeName="offset" values=".35;.62;.35" dur="6s" repeatCount="indefinite"/></stop><stop offset="1" stop-color="#5EEAD4"/></linearGradient>
  <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#60A5FA" stop-opacity="0"/><stop offset=".5" stop-color="#22D3EE" stop-opacity=".9"/><stop offset="1" stop-color="#A78BFA" stop-opacity="0"/></linearGradient>
  <radialGradient id="orb"><stop offset="0" stop-color="#22D3EE" stop-opacity=".28"/><stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>
  <clipPath id="round"><rect x="0" y="0" width="1200" height="244" rx="18"/></clipPath>
  <filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  .orb1{{animation:drift1 11s ease-in-out infinite alternate;transform-origin:center}}
  .orb2{{animation:drift2 14s ease-in-out infinite alternate;transform-origin:center}}
  .trail{{animation:trace 5.6s ease-in-out infinite}}
  .hero{{opacity:1;animation:enter .95s cubic-bezier(.2,.8,.2,1) .15s both}}
  .sub{{opacity:1;animation:enter .8s ease-out .65s both}}
  .accent{{animation:pulse 3.4s ease-in-out infinite}}
  @keyframes drift1{{from{{transform:translate(-30px,8px)}}to{{transform:translate(80px,-18px)}}}}
  @keyframes drift2{{from{{transform:translate(45px,-8px)}}to{{transform:translate(-60px,18px)}}}}
  @keyframes trace{{0%{{transform:translateX(-900px);opacity:0}}20%{{opacity:.95}}70%{{opacity:.8}}100%{{transform:translateX(1300px);opacity:0}}}}
  @keyframes enter{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
  @keyframes pulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
  @media (prefers-reduced-motion:reduce){{.orb1,.orb2,.trail,.hero,.sub,.accent{{animation:none!important;opacity:1!important;transform:none!important}}}}
</style>
<g clip-path="url(#round)">
  <rect width="1200" height="244" fill="url(#bg)"/>
  <circle class="orb1" cx="235" cy="30" r="270" fill="url(#orb)"/>
  <circle class="orb2" cx="1040" cy="240" r="360" fill="url(#orb)"/>
  <path d="M0 192 C180 152 300 224 470 184 S780 150 930 192 S1100 228 1200 168 V244 H0Z" fill="#08111F" opacity=".38"/>
  <path d="M0 210 C160 172 290 230 460 201 S780 174 960 211 S1100 220 1200 198" fill="none" stroke="#38BDF8" stroke-opacity=".22" stroke-width="1.5"/>
  <g class="trail"><path d="M0 199 H1200" stroke="url(#trail)" stroke-width="2.2" filter="url(#glow)"/></g>
  <g class="hero" text-anchor="middle">
    <text x="600" y="98" font-family="Segoe UI, Arial, sans-serif" font-size="58" font-weight="800" letter-spacing="2" fill="url(#name)" filter="url(#glow)">ARPIT JHAM</text>
  </g>
  <g class="sub" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif">
    <text x="600" y="141" font-size="18" font-weight="700" letter-spacing=".65" fill="#E6F7FF">TEAM LEAD  |  FULL-STACK DEVELOPER  |  AI PRODUCT ENGINEERING</text>
    <text x="600" y="171" font-size="13" letter-spacing="2.1" fill="#A9D8E8">BUILDING RELIABLE SOFTWARE · INTELLIGENT WORKFLOWS · USEFUL INTERFACES</text>
  </g>
  <rect class="accent" x="410" y="220" width="380" height="3" rx="1.5" fill="url(#trail)"/>
</g>
</svg>'''


def tagline_svg() -> str:
    phrase = "ENGINEERING RELIABLE AI PRODUCTS  ·  DESIGNING CLEAR INTERFACES  ·  LEADING TEAMS TO DELIVERY"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="64" viewBox="0 0 1200 64" role="img" aria-labelledby="title">
<title id="title">Engineering reliable AI products, designing clear interfaces, leading teams to delivery</title>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/><stop offset=".52" stop-color="{CYAN}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient><linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".7"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient></defs>
<style>
  .caption{{font-family:'JetBrains Mono',Consolas,monospace;font-size:19px;font-weight:700;letter-spacing:.35px;fill:url(#g)}}
  .sweep{{animation:sweep 4.8s ease-in-out infinite}}
  @keyframes sweep{{0%{{transform:translateX(-520px);opacity:0}}18%{{opacity:.8}}58%{{transform:translateX(520px);opacity:0}}100%{{transform:translateX(520px);opacity:0}}}}
  @media (prefers-reduced-motion:reduce){{.sweep{{animation:none;display:none}}}}
</style>
<rect width="1200" height="64" rx="14" fill="{PANEL}" fill-opacity=".9" stroke="{BORDER}" stroke-opacity=".8"/>
<text class="caption" x="600" y="36" text-anchor="middle">{html.escape(phrase)}</text>
<path d="M26 51 H1174" stroke="{BORDER}" stroke-width="1"/><path d="M26 51 H1174" stroke="url(#g)" stroke-width="2.2" stroke-linecap="round" opacity=".65"/>
<rect class="sweep" x="0" y="49" width="330" height="4" rx="2" fill="url(#shine)"/>
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
    left, right, top, bottom = 74.0, 1080.0, 76.0, 257.0
    max_value = max((count for _, count in points_data), default=0)
    scale_max = max(1, math.ceil(max_value / 2) * 2 if max_value <= 10 else math.ceil(max_value / 5) * 5)
    coords = []
    for i, (_, count) in enumerate(points_data):
        x = left + (right - left) * i / max(1, len(points_data) - 1)
        y = bottom - (bottom - top) * count / scale_max
        coords.append((x, y, count))
    path_d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y, _ in coords)
    area_d = f"{path_d} L {right:.2f} {bottom:.2f} L {left:.2f} {bottom:.2f} Z"
    path_len = sum(math.hypot(coords[i][0]-coords[i-1][0], coords[i][1]-coords[i-1][1]) for i in range(1, len(coords)))
    path_len = max(path_len, 1)

    grid = []
    for j in range(5):
        y = top + (bottom - top) * j / 4
        val = scale_max * (4-j) / 4
        grid.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="{BORDER}" stroke-opacity=".6" stroke-dasharray="4 8"/>')
        grid.append(f'<text x="{left-18}" y="{y+5:.2f}" text-anchor="end" fill="{MUTED}" font-size="12">{int(round(val))}</text>')

    xticks = []
    tick_indexes = sorted(set([0, 7, 14, 21, 30 if len(coords) > 30 else len(coords)-1]))
    for idx in tick_indexes:
        if 0 <= idx < len(points_data):
            date = points_data[idx][0]
            x = coords[idx][0]
            label = date.strftime("%b ") + str(date.day)
            xticks.append(f'<text x="{x:.2f}" y="294" text-anchor="middle" fill="{MUTED}" font-size="12">{label}</text>')

    circles = []
    n = max(1, len(coords)-1)
    for i, (x, y, count) in enumerate(coords):
        delay = 0.5 + (i/n)*1.9
        radius = 3.1 if count == 0 else 4.1
        circles.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{CYAN if count else BLUE}" stroke="{NAVY}" stroke-width="1.5" opacity="1"><animate attributeName="opacity" values="0;1" begin="{delay:.2f}s" dur=".35s" fill="freeze"/><animate attributeName="r" values="1;{radius}" begin="{delay:.2f}s" dur=".35s" fill="freeze"/></circle>')

    last_total = sum(count for _, count in points_data)
    start_label = points_data[0][0].strftime("%b ") + str(points_data[0][0].day)
    end_label = points_data[-1][0].strftime("%b ") + str(points_data[-1][0].day)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">GitHub contributions over the last 31 days</title><desc id="desc">A local chart based on {len(points_data)} daily contribution records from {html.escape(start_label)} to {html.escape(end_label)}. Total activity during this period: {last_total} contributions.</desc>
<defs>
 <linearGradient id="chartbg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{NAVY}"/></linearGradient>
 <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BLUE}"/><stop offset=".55" stop-color="{CYAN}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>
 <linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".28"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".005"/></linearGradient>
 <filter id="softglow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
 .line{{stroke-dasharray:{path_len:.1f};stroke-dashoffset:0;animation:draw 2.5s cubic-bezier(.22,.7,.2,1) .25s both}}
 .area{{opacity:.55;animation:fade 1.2s ease-out .7s both}}
 .header{{opacity:1;animation:up .65s ease-out .1s both}}
 @keyframes draw{{from{{stroke-dashoffset:{path_len:.1f}}}to{{stroke-dashoffset:0}}}} @keyframes fade{{from{{opacity:0}}to{{opacity:.55}}}} @keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
 @media (prefers-reduced-motion:reduce){{.line{{stroke-dashoffset:0;animation:none}}.area,.header{{opacity:1;animation:none}}}}
</style>
<rect x="1" y="1" width="1118" height="338" rx="18" fill="url(#chartbg)" stroke="{BORDER}"/>
<circle cx="22" cy="22" r="4" fill="#FF6B6B"/><circle cx="37" cy="22" r="4" fill="{GOLD}"/><circle cx="52" cy="22" r="4" fill="{TEAL}"/>
<g class="header" font-family="Segoe UI,Arial,sans-serif"><text x="76" y="27" fill="{TEXT}" font-size="13" font-weight="700" letter-spacing="1.1">GITHUB ACTIVITY</text><text x="76" y="47" fill="{MUTED}" font-size="11">{html.escape(start_label)} — {html.escape(end_label)} · {last_total} contributions</text><text x="1080" y="28" fill="{TEAL}" font-size="12" text-anchor="end">LAST 31 DAYS</text></g>
{''.join(grid)}
<path class="area" d="{area_d}" fill="url(#area)"/>
<path class="line" d="{path_d}" fill="none" stroke="url(#line)" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#softglow)"/>
{''.join(circles)}
{''.join(xticks)}
<text x="1080" y="322" text-anchor="end" fill="{MUTED}" font-size="11">Generated from contribution snapshot</text>
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
