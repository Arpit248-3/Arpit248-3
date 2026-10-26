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

NAVY = "#0A0F1E"
PANEL = "#11182A"
PANEL_2 = "#17213A"
BLUE = "#82A8FF"
CYAN = "#55D6FF"
TEAL = "#75D7D0"
VIOLET = "#B5A2FF"
GOLD = "#E9C46A"
TEXT = "#E9EEFA"
MUTED = "#A9B5CA"
BORDER = "#28334A"


def write_svg(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


# The name is drawn as vector paths (Z003 Medium Italic outline), rather than
# relying on a font installed on GitHub's SVG renderer. This keeps the script-like
# letterforms visible across browsers without shipping a font file.
HERO_GLYPHS = {'A': 'M23 9C46 2 57 0 76 0C144 0 191 36 322 186C401 186 460 185 499 182C497 170 495 158 494 146C492 136 489 115 486 93C484 74 481 56 480 52C477 35 475 19 475 9C475 -4 485 -13 498 -13C502 -13 529 -8 579 1L636 11C643 12 654 14 671 17L687 41C646 38 621 36 613 36C573 36 562 46 562 81C562 145 601 425 633 584L619 594C589 563 587 562 566 562C553 562 548 563 509 569C464 576 438 579 418 579C372 579 324 556 277 510C224 459 201 415 201 362C201 338 204 322 215 293L289 333C273 380 268 403 268 426C268 483 311 517 384 517C395 517 408 516 421 515L445 512C459 511 469 510 476 509C492 507 501 507 528 505L355 281C313 227 248 151 221 125C181 86 151 72 105 72C88 72 79 73 61 79ZM353 227 546 480 505 227Z', 'J': 'M258 342C252 376 250 392 250 414C250 492 291 534 368 534H383L328 314C309 298 306 295 288 277C303 267 307 262 312 248C304 223 304 223 289 166C260 62 258 57 239 20C212 -32 167 -60 108 -60C88 -60 72 -58 41 -50L1 -117C20 -121 29 -122 45 -122C107 -122 150 -102 244 -27C328 40 336 53 366 174L458 543L491 572C420 572 392 570 351 562C241 540 173 464 173 364C173 344 175 333 182 307Z', 'a': 'M492 131C419 81 402 71 392 71C385 71 380 79 380 91C380 118 403 223 440 360C451 376 453 378 469 396C421 407 387 411 343 411C302 411 282 407 257 391C221 370 179 339 166 325C128 283 87 148 87 67C87 19 103 -13 128 -13C150 -13 183 7 308 97C297 46 293 21 293 8C293 -6 299 -13 309 -13C322 -13 330 -9 401 38C435 61 454 74 491 101ZM316 138C281 112 263 99 262 98C229 77 203 64 190 64C173 64 164 82 164 114C164 165 179 231 205 289C229 344 251 365 285 365C303 365 337 360 370 352C350 280 343 253 342 248C336 223 331 198 325 172C324 167 321 155 316 138Z', 'h': 'M75 -9 146 20 205 253C215 260 224 265 229 268C255 285 273 296 277 298C343 334 343 334 352 334C358 334 363 328 363 319C363 305 359 286 345 233C316 120 302 55 302 28C302 15 306 4 317 -15C372 13 445 59 499 99L506 128C423 79 407 71 394 71C385 71 379 81 379 97C379 124 384 144 424 291C450 388 450 388 450 394C450 404 442 411 429 411C407 411 342 375 214 292L248 426C272 524 282 555 295 580C309 608 330 621 357 621C370 621 378 620 417 612L460 673C442 677 434 678 418 678C364 678 335 663 262 599C210 553 202 536 171 404Z', 'i': 'M273 616C245 594 222 576 204 564C211 543 220 526 242 494C270 519 273 522 307 548C304 554 302 558 294 571C288 583 287 583 279 603ZM311 116 294 107C225 69 213 64 201 64C190 64 183 75 183 92C183 109 183 109 216 241C253 393 253 393 253 401C253 407 248 411 241 411C224 411 165 378 83 323L81 295C142 328 145 329 154 329C162 329 166 323 166 312C166 298 163 284 148 227C101 53 101 53 101 27C101 3 110 -13 125 -13C142 -13 169 0 222 34C241 46 260 58 279 71C288 76 295 81 307 88Z', 'm': 'M92 -10 163 17 227 260C292 305 335 329 348 329C356 329 361 321 361 307C361 277 323 126 281 -10L357 17L419 267C476 304 530 334 542 334C551 334 555 327 555 315C555 293 546 248 519 145C504 83 499 58 499 35C499 14 504 3 523 -10C581 19 637 55 692 99L693 122C608 70 608 70 594 70C583 70 576 80 576 96C576 119 588 172 609 246C641 357 647 380 647 396C647 406 642 411 631 411C613 411 551 379 429 307C433 325 433 325 442 364C446 379 449 396 449 400C449 407 444 411 436 411C419 411 381 390 237 299C253 367 258 390 258 397C258 406 252 411 243 411C233 411 222 405 172 377C106 339 106 339 88 327L81 299C134 326 143 329 155 329C163 329 169 321 169 310C169 295 166 282 126 123C117 91 109 58 101 25Z', 'p': 'M22 -213 -8 -245C10 -246 22 -246 26 -246L98 -247L162 -248C170 -248 184 -248 209 -247L240 -222L128 -216C141 -155 147 -126 151 -110C156 -89 160 -68 165 -46L176 -3C196 -7 207 -8 224 -8C279 -8 290 -3 368 62C402 89 414 103 429 132C461 197 482 275 482 332C482 380 461 411 428 411C404 411 370 396 329 366C285 334 258 314 247 307C261 366 268 396 268 398C268 404 261 411 254 411C244 411 163 368 89 324L83 298C90 301 104 307 124 315C143 324 147 325 155 325C167 325 174 315 174 297C174 261 115 4 58 -211ZM200 98 215 166 230 231C231 236 234 249 238 267C319 327 351 344 377 344C397 344 410 323 410 289C410 244 396 187 371 133C344 73 310 44 269 44C244 44 217 52 193 66Z', 'r': 'M90 -10 167 19 242 304C276 330 299 339 326 339C348 339 361 331 379 308L409 403C391 409 382 411 372 411C353 411 333 402 306 383C293 373 280 363 266 354C260 349 253 344 247 340L259 400C259 406 253 411 246 411C233 411 145 368 84 332L81 305C139 333 140 334 153 334C166 334 172 327 172 313C172 299 162 253 150 209Z', 't': 'M363 126C287 80 255 64 241 64C228 64 212 89 212 111C212 125 213 128 235 223C240 241 244 260 248 279C249 282 253 298 255 307C289 308 320 310 354 312L392 341H264C269 364 271 371 274 386C277 396 284 423 298 477L304 503L287 494C281 492 273 488 262 483C255 479 247 476 239 472C235 470 231 468 225 466L216 425L205 377L197 341C188 340 182 340 179 340H155C153 340 148 340 140 339C135 336 131 333 130 333C127 331 121 326 111 318C109 317 104 312 96 307H120H166H188L178 263C135 86 135 86 135 54C135 22 156 -13 175 -13C197 -13 265 28 361 101Z'}
HERO_ADVANCES = {'A': 620, 'J': 400, 'a': 420, 'h': 440, 'i': 240, 'm': 620, 'p': 440, 'r': 300, 't': 320}
HERO_SPACE_ADVANCE = 220
HERO_NAME = "Arpit Jham"
HERO_SCALE = 0.145
HERO_LETTER_SPACING = 24


def hero_svg() -> str:
    """Transparent editorial hero with refined typography, not a filled banner card."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="238" viewBox="0 0 1200 238" role="img" aria-labelledby="title desc">
<title id="title">Arpit Jham — Team Lead, Full-Stack Developer and AI Product Engineering</title>
<desc id="desc">A transparent hero with elegant italic serif lettering, midnight blue and periwinkle accents, and subtle animated light trails.</desc>
<defs>
 <radialGradient id="heroHalo"><stop offset="0" stop-color="#4567B7" stop-opacity=".12"/><stop offset=".58" stop-color="#253D76" stop-opacity=".035"/><stop offset="1" stop-color="#0A0F1E" stop-opacity="0"/></radialGradient>
 <linearGradient id="heroName" x1=".08" y1="0" x2=".94" y2="0"><stop offset="0" stop-color="#F4F7FF"/><stop offset=".34" stop-color="#A9C7FF"/><stop offset=".68" stop-color="#78DDF7"/><stop offset="1" stop-color="#B5A2FF"/></linearGradient>
 <linearGradient id="heroRule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#82A8FF" stop-opacity="0"/><stop offset=".3" stop-color="#82A8FF" stop-opacity=".8"/><stop offset=".68" stop-color="#55D6FF" stop-opacity=".8"/><stop offset="1" stop-color="#B5A2FF" stop-opacity="0"/></linearGradient>
 <radialGradient id="orbital"><stop offset="0" stop-color="#55D6FF" stop-opacity=".10"/><stop offset="1" stop-color="#55D6FF" stop-opacity="0"/></radialGradient>
 <filter id="wordGlow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="1.8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
 .halo{{animation:haloDrift 11s ease-in-out infinite alternate;transform-origin:center}}
 .word{{opacity:1;animation:wordIn 1.1s cubic-bezier(.2,.8,.2,1) .1s forwards}}
 .role{{opacity:1;animation:roleIn .8s ease-out .45s forwards}}
 .micro{{opacity:1;animation:roleIn .8s ease-out .72s forwards}}
 .beam{{stroke-dasharray:520;stroke-dashoffset:520;animation:beamIn 1.8s ease-out .55s forwards}}
 .spark{{animation:sparkMove 6s ease-in-out infinite alternate}}
 @keyframes haloDrift{{from{{transform:translate(-26px,2px) scale(.96)}}to{{transform:translate(30px,-6px) scale(1.05)}}}}
 @keyframes wordIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
 @keyframes roleIn{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:translateY(0)}}}}
 @keyframes beamIn{{to{{stroke-dashoffset:0}}}}
 @keyframes sparkMove{{from{{opacity:.25;transform:translateX(-12px)}}to{{opacity:.95;transform:translateX(12px)}}}}
 @media (prefers-reduced-motion:reduce){{.halo,.word,.role,.micro,.beam,.spark{{animation:none!important;opacity:1;transform:none;stroke-dashoffset:0}}}}
</style>
<!-- Transparent canvas blends into GitHub's page; only typography, fine trails, and small orbital accents are drawn. -->
<circle cx="128" cy="60" r="18" fill="none" stroke="#82A8FF" stroke-opacity=".20" stroke-width="1"/><circle cx="128" cy="60" r="2" fill="#82A8FF"/><circle cx="1072" cy="54" r="24" fill="none" stroke="#55D6FF" stroke-opacity=".18" stroke-width="1"/><circle cx="1072" cy="54" r="2" fill="#55D6FF"/>
<path d="M70 182 C230 164 304 204 440 188 S690 177 812 190 S1010 205 1130 178" fill="none" stroke="#42608B" stroke-opacity=".28" stroke-width="1.2"/>
<path d="M76 190 C240 174 310 211 450 194 S690 185 820 196 S1008 209 1124 185" fill="none" stroke="url(#heroRule)" stroke-opacity=".8" stroke-width="1.6"/>
<g class="word" filter="url(#wordGlow)"><text x="600" y="100" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="72" font-style="italic" font-weight="600" letter-spacing=".5" fill="url(#heroName)">Arpit Jham</text></g>
<g class="role" font-family="'Segoe UI', Arial, sans-serif"><text x="310" y="139" font-size="17" font-weight="650" letter-spacing=".7" fill="#E9EEFA">TEAM LEAD <tspan fill="#82A8FF">·</tspan> FULL-STACK DEVELOPER <tspan fill="#55D6FF">·</tspan> AI PRODUCT ENGINEERING</text></g>
<g class="micro" font-family="'Segoe UI', Arial, sans-serif"><text x="350" y="166" font-size="11" font-weight="600" letter-spacing="2.05" fill="#A9B5CA">RELIABLE SOFTWARE  ·  CLEAR INTERFACES  ·  APPLIED AI</text></g>
<path class="beam" d="M280 211 H920" stroke="url(#heroRule)" stroke-width="2.2" stroke-linecap="round" fill="none"/>
<circle class="spark" cx="280" cy="211" r="2.5" fill="#55D6FF"/>
</svg>'''

def tagline_svg() -> str:
    phrases = [
        "BUILDING SCALABLE PROJECTS",
        "DESIGNING PREMIUM USER INTERFACES",
        "LEAD DEVELOPER · AI PRODUCT ENGINEERING",
    ]
    p1, p2, p3 = map(html.escape, phrases)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="66" viewBox="0 0 1200 66" role="img" aria-labelledby="title desc">
<title id="title">Arpit Jham — rotating professional tagline</title>
<desc id="desc">A transparent tagline cycling between scalable projects, premium interfaces, and AI product engineering.</desc>
<defs>
 <linearGradient id="taglineGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#82A8FF"/><stop offset=".48" stop-color="#55D6FF"/><stop offset="1" stop-color="#B5A2FF"/></linearGradient>
 <linearGradient id="taglineRule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#82A8FF" stop-opacity="0"/><stop offset=".5" stop-color="#55D6FF" stop-opacity=".72"/><stop offset="1" stop-color="#B5A2FF" stop-opacity="0"/></linearGradient>
</defs>
<style>
 .phrase{{font-family:'Segoe UI',Arial,sans-serif;font-size:21px;font-weight:650;letter-spacing:1.75px;fill:url(#taglineGradient)}}
 .rule{{stroke-dasharray:700;stroke-dashoffset:700;animation:ruleDraw 9s ease-in-out infinite}}
 .spark{{animation:sparkTravel 4.5s ease-in-out infinite alternate}}
 @keyframes ruleDraw{{0%,5%{{stroke-dashoffset:700;opacity:.2}}30%,57%{{stroke-dashoffset:0;opacity:.8}}100%{{stroke-dashoffset:-700;opacity:.15}}}}
 @keyframes sparkTravel{{from{{transform:translateX(0);opacity:.2}}to{{transform:translateX(680px);opacity:1}}}}
 @media (prefers-reduced-motion:reduce){{.rule,.spark{{animation:none}}.rule{{stroke-dashoffset:0}}.spark{{opacity:.5}}}}
</style>
<!-- First phrase stays visible if a renderer disables SVG animation. -->
<text class="phrase" x="600" y="30" text-anchor="middle" opacity="1">{p1}<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.24;.29;.95;1" dur="12s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -5;0 -5;0 0" keyTimes="0;.24;.29;.95;1" dur="12s" repeatCount="indefinite"/></text>
<text class="phrase" x="600" y="30" text-anchor="middle" opacity="0">{p2}<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.28;.33;.57;.62;1" dur="12s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 5;0 5;0 0;0 0;0 -5;0 -5" keyTimes="0;.28;.33;.57;.62;1" dur="12s" repeatCount="indefinite"/></text>
<text class="phrase" x="600" y="30" text-anchor="middle" opacity="0">{p3}<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.61;.66;.94;1" dur="12s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 5;0 5;0 0;0 0;0 -5" keyTimes="0;.61;.66;.94;1" dur="12s" repeatCount="indefinite"/></text>
<path d="M170 48 H1030" stroke="url(#taglineRule)" stroke-width="1.2" stroke-linecap="round"/>
<path class="rule" d="M260 48 H940" stroke="url(#taglineGradient)" stroke-width="1.8" stroke-linecap="round" fill="none"/>
<circle class="spark" cx="260" cy="48" r="2.2" fill="#55D6FF"/>
</svg>'''

SECTIONS = [
    ("section-about.svg", "01", "ABOUT", BLUE, "about"),
    ("section-contributions.svg", "02", "CONTRIBUTIONS", CYAN, "contributions"),
    ("section-leadership.svg", "03", "LEADERSHIP EXPERIENCE", TEAL, "leadership"),
    ("section-skills.svg", "04", "TECHNICAL SKILLS", VIOLET, "skills"),
    ("section-projects.svg", "05", "FEATURED PROJECTS", BLUE, "projects"),
    ("section-achievements.svg", "06", "ACHIEVEMENTS", GOLD, "achievements"),
]

ICON_PATHS = {
    "about": '<circle cx="12" cy="12" r="8.2"/><path d="M8.5 12.2l2.2 2.2 4.8-5"/>',
    "contributions": '<path d="M3 19V5M3 19H21M5 15l4-4 4 2 6-7"/><circle cx="19" cy="6" r="1.5"/>',
    "leadership": '<circle cx="12" cy="6" r="3"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/><path d="M12 9v4M5 15v-2h14v2"/>',
    "skills": '<path d="M8 5L2 12l6 7M16 5l6 7-6 7M14 3l-4 18"/>',
    "projects": '<path d="M12 3L21 8 12 13 3 8 12 3Z M3 12l9 5 9-5M3 16l9 5 9-5"/>',
    "achievements": '<path d="M12 2.8l2.8 5.6 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2-4.5-4.4 6.2-.9L12 2.8Z"/>',
}


def section_svg(number: str, label: str, accent: str, icon: str) -> str:
    safe_label = html.escape(label.title() if label != "TECHNICAL SKILLS" else "Technical Skills")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="68" viewBox="0 0 1200 68" role="img" aria-labelledby="title desc">
<title id="title">{number} — {safe_label}</title>
<desc id="desc">Minimal editorial section heading with a colored index, line icon, and animated gradient rule.</desc>
<defs>
 <linearGradient id="ruleGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}" stop-opacity=".9"/><stop offset=".46" stop-color="{CYAN}" stop-opacity=".7"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".03"/></linearGradient>
 <filter id="iconGlow" x="-40%" y="-50%" width="180%" height="200%"><feGaussianBlur stdDeviation="1.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
 .heading{{opacity:1;animation:headingIn .62s cubic-bezier(.2,.8,.2,1) .05s forwards}}
 .line{{stroke-dasharray:920;stroke-dashoffset:920;animation:lineIn 1.15s cubic-bezier(.2,.8,.2,1) .18s forwards}}
 .dot{{animation:dotPulse 3.2s ease-in-out infinite}}
 @keyframes headingIn{{from{{opacity:0;transform:translateX(-12px)}}to{{opacity:1;transform:translateX(0)}}}}
 @keyframes lineIn{{to{{stroke-dashoffset:0}}}}
 @keyframes dotPulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
 @media (prefers-reduced-motion:reduce){{.heading,.line,.dot{{animation:none;opacity:1;stroke-dashoffset:0}}}}
</style>
<g class="heading">
 <text x="18" y="35" font-family="'Segoe UI',Arial,sans-serif" font-size="14" font-weight="700" fill="{accent}" letter-spacing="1.4">{number}</text>
 <g transform="translate(63 13)" stroke="{accent}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#iconGlow)">{ICON_PATHS[icon]}</g>
 <text x="105" y="37" font-family="'Segoe UI',Arial,sans-serif" font-size="24" font-weight="650" fill="{TEXT}" letter-spacing=".25">{safe_label}</text>
 <path d="M105 53 H1180" stroke="{BORDER}" stroke-width="1" stroke-opacity=".76"/>
 <path class="line" d="M105 53 H520" stroke="url(#ruleGradient)" stroke-width="2.1" stroke-linecap="round" fill="none"/>
 <circle class="dot" cx="1180" cy="53" r="2.4" fill="{accent}"/>
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
 .line{{stroke-dasharray:{path_len:.1f};stroke-dashoffset:0;animation:draw 2.8s cubic-bezier(.3,.7,.2,1) .25s}}
 .area{{opacity:0;animation:fade 1.3s ease-out .65s forwards}}
 .header{{opacity:0;animation:up .65s ease-out .12s forwards}}
 @keyframes draw{{from{{stroke-dashoffset:{path_len:.1f}}}to{{stroke-dashoffset:0}}}} @keyframes fade{{to{{opacity:.58}}}} @keyframes up{{from{{opacity:0;transform:translateY(7px)}}to{{opacity:1;transform:translateY(0)}}}}
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
    for filename, number, label, accent, icon in SECTIONS:
        write_svg(ASSETS / filename, section_svg(number, label, accent, icon))
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
