#!/usr/bin/env python3
"""Targeted GitHub profile animation/color repair.

Run from the profile repository root:
  python scripts/fix_profile_animation_scope.py

This intentionally edits only:
- README image references for the centered tagline and animated section headings
- root contribution SVGs (activity graph, heatmap, ASCII panel, local stats panel)
- theme-specific light SVG variants generated from those sources
- section-heading/tagline light variants
- update-profile-art.yml, when present, so generated SVGs keep these animation fixes

It does not change section content/order, project descriptions, skills layout, achievements,
banner files, or contribution data.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

LIGHT_MAP = {
    "#070b14":"#F8FAFC", "#08111f":"#F8FAFC", "#080d1b":"#F8FAFC", "#0a101f":"#F8FAFC",
    "#0a1322":"#F8FAFC", "#0b1220":"#F8FAFC", "#0b1322":"#F1F5F9", "#0d1728":"#F1F5F9",
    "#0e1b2d":"#EFF6FF", "#101d31":"#EFF6FF", "#102237":"#EFF6FF", "#10243b":"#E2E8F0",
    "#0b2631":"#ECFEFF", "#0c2032":"#E0F2FE", "#0d1117":"#F8FAFC", "#101827":"#F1F5F9",
    "#101b2c":"#EFF6FF", "#111722":"#F1F5F9", "#111827":"#E2E8F0", "#0f172a":"#F8FAFC",
    "#161b22":"#E2E8F0", "#1d314b":"#CBD5E1", "#1d6471":"#0E7490", "#21425a":"#CBD5E1",
    "#28516a":"#CBD5E1", "#29415a":"#CBD5E1", "#29425c":"#CBD5E1", "#283548":"#CBD5E1",
    "#2e4968":"#CBD5E1", "#30363d":"#CBD5E1", "#334155":"#CBD5E1", "#164e63":"#BAE6FD",
    "#1e293b":"#E2E8F0", "#e6f1ff":"#0F172A", "#e8f1ff":"#0F172A", "#f8fafc":"#0F172A",
    "#f9fafb":"#0F172A", "#e6edf3":"#0F172A", "#dce6f2":"#1E293B", "#d6e7ff":"#1E293B",
    "#e0f2fe":"#1E293B", "#e2e8f0":"#1E293B", "#d1d5db":"#334155", "#c9d1d9":"#334155",
    "#a5f3fc":"#0E7490", "#a9bdd5":"#475569", "#9fb3c8":"#475569", "#8da3be":"#475569",
    "#94a3b8":"#475569", "#7d8590":"#475569", "#9ca3af":"#475569", "#64748b":"#475569",
    "#52657e":"#475569", "#b8c5d6":"#475569", "#39d353":"#16A34A", "#26a641":"#15803D",
    "#67e8f9":"#0E7490", "#c4b5fd":"#6D28D9", "#60a5fa":"#2563EB", "#22d3ee":"#0E7490",
    "#10b981":"#047857", "#a78bfa":"#7C3AED", "#38bdf8":"#0369A1",
}
COLOR_RE = re.compile(r"#[0-9a-fA-F]{6}")

SECTION_FILES = [
    "section-developer-stats-accent.svg",
    "section-about-accent.svg",
    "section-contributions-accent.svg",
    "section-leadership-accent.svg",
    "section-skills-accent.svg",
    "section-projects-accent.svg",
    "section-achievements-accent.svg",
    "section-snake-accent.svg",
]

WRAPPERS = {
    "activity-graph.svg": "loopRevealActivityGraph",
    "contrib-heatmap.svg": "loopRevealHeatmap",
    "profile-ascii.svg": "loopRevealAsciiPortrait",
    "stats.svg": "loopRevealStats",
}


def log(msg: str) -> None:
    print(msg)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def one_pass_lightify(svg: str) -> str:
    return COLOR_RE.sub(lambda m: LIGHT_MAP.get(m.group(0).lower(), m.group(0)), svg)


def make_light_section(source: Path, target: Path) -> bool:
    if not source.exists():
        log(f"SKIP {source.relative_to(ROOT)}: source asset is missing")
        return False
    svg = read_text(source)
    # Change only the thin title-rule gradient for light mode; preserve its accent color and animated title.
    def patch_line_gradient(match: re.Match[str]) -> str:
        block = match.group(0)
        block = re.sub(r'stop-color="#334155"', 'stop-color="#AFC0D4"', block, flags=re.I)
        block = re.sub(r'stop-color="#0B1220"', 'stop-color="#DCE7F4"', block, flags=re.I)
        return block
    svg = re.sub(r'<linearGradient\b(?=[^>]*\bid="line")[^>]*>.*?</linearGradient>', patch_line_gradient, svg, count=1, flags=re.S)
    # Put the static fallback dot at the start of the underline; SMIL moves it across the line indefinitely.
    svg = svg.replace('<circle id="loop-travel-dot" r="3.1" cy="52"', '<circle id="loop-travel-dot" r="3.1" cx="118" cy="52"')
    # All relevant heading SVGs have their own repeating title gradient, moving line, and pulsing dot.
    ET.fromstring(svg)
    write_text(target, svg)
    return True


def make_light_tagline() -> bool:
    source = ROOT / "assets" / "profile-tagline.svg"
    target = ROOT / "assets" / "profile-tagline-light.svg"
    if not source.exists():
        log("SKIP assets/profile-tagline-light.svg: profile-tagline.svg is missing")
        return False
    svg = read_text(source)
    # Use deeper blue/cyan/violet in light mode, without changing the moving dot/underline animation.
    svg = svg.replace('stop-color="#38BDF8"', 'stop-color="#0369A1"')
    svg = svg.replace('stop-color="#22D3EE"', 'stop-color="#0891B2"')
    svg = svg.replace('stop-color="#A78BFA"', 'stop-color="#6D28D9"')
    svg = svg.replace('stroke="#64748B"', 'stroke="#94A3B8"')
    svg = svg.replace('fill="#22D3EE"', 'fill="#0891B2"')
    ET.fromstring(svg)
    write_text(target, svg)
    return True


def patch_outer_reveal(svg: str, clip_id: str) -> str:
    """Disable only the previous full-canvas wipe. Leave all internal art/animations in place."""
    group_id = clip_id + "Group"
    # Remove the clip-path from only the known bad wrapper group.
    def patch_group(m: re.Match[str]) -> str:
        tag = m.group(0)
        tag = re.sub(r'\sclip-path=["\']url\(#' + re.escape(clip_id) + r'\)["\']', '', tag)
        return tag
    svg = re.sub(r'<g\b[^>]*\bid=["\']' + re.escape(group_id) + r'["\'][^>]*>', patch_group, svg, count=1)
    # Remove only its corresponding animated clipPath definition.
    svg = re.sub(r'<clipPath\b(?=[^>]*\bid=["\']' + re.escape(clip_id) + r'["\'])[^>]*>.*?</clipPath>', '', svg, count=1, flags=re.S)
    return svg


def remove_added_sweep(svg: str, stem: str) -> str:
    """Remove the old full-panel moving overlay if a previous script injected it."""
    marker = f"looping_refresh_{stem}"
    pat = re.compile(
        r'<!--\s*' + re.escape(marker) + r'\s*-->\s*'
        r'<defs>.*?<linearGradient\b[^>]*\bid=["\']' + re.escape(marker) + r'Grad["\'][^>]*>.*?</linearGradient>.*?</defs>\s*'
        r'<rect\b(?=[^>]*fill=["\']url\(#' + re.escape(marker) + r'Grad\)["\'])[^>]*>.*?</rect>',
        re.S,
    )
    svg = pat.sub('', svg, count=1)
    # In a few older variants the comment is missing but the gradient/overlay remains.
    svg = re.sub(r'<defs>\s*<linearGradient\b[^>]*\bid=["\']' + re.escape(marker) + r'Grad["\'][^>]*>.*?</linearGradient>\s*</defs>', '', svg, count=1, flags=re.S)
    svg = re.sub(r'<rect\b(?=[^>]*fill=["\']url\(#' + re.escape(marker) + r'Grad\)["\'])[^>]*>.*?</rect>', '', svg, count=1, flags=re.S)
    return svg


def patch_graph_line_only(svg: str) -> str:
    # Keep the plot, grid, markers, labels, and filled area static; only the line stroke repeatedly draws.
    m = re.search(r'\.line\s*\{([^}]*)\}', svg)
    if not m:
        log("WARN activity-graph.svg: no .line CSS rule found; kept the file unchanged apart from removing a full-canvas wipe")
        return svg
    body = m.group(1)
    dash = re.search(r'stroke-dasharray\s*:\s*([0-9.]+)', body)
    if not dash:
        log("WARN activity-graph.svg: no numeric stroke-dasharray found; kept chart line CSS unchanged")
        return svg
    length = dash.group(1)
    declarations = [p.strip() for p in body.split(';') if p.strip()]
    kept = []
    for declaration in declarations:
        low = declaration.lower()
        if low.startswith('animation:') or low.startswith('stroke-dashoffset:'):
            continue
        if low.startswith('stroke-dasharray:'):
            continue
        kept.append(declaration)
    kept.extend([
        f'stroke-dasharray:{length}',
        f'stroke-dashoffset:{length}',
        'animation:activityLineLoop 10s cubic-bezier(.3,.7,.2,1) infinite',
    ])
    new_rule = '.line{' + ';'.join(kept) + '}'
    svg = svg[:m.start()] + new_rule + svg[m.end():]
    keyframes = f'@keyframes activityLineLoop{{0%,100%{{stroke-dashoffset:{length};opacity:.42}}34%,78%{{stroke-dashoffset:0;opacity:1}}}}'
    # Replace old one-shot keyframe or a prior variant of our keyframe, avoiding the old animation ending forever.
    svg = re.sub(r'@keyframes\s+draw\s*\{(?:[^{}]|\{[^{}]*\})*\}', keyframes, svg, count=1)
    if re.search(r'@keyframes\s+activityLineLoop\s*\{', svg):
        svg = re.sub(r'@keyframes\s+activityLineLoop\s*\{(?:[^{}]|\{[^{}]*\})*\}', keyframes, svg, count=1)
    elif keyframes not in svg:
        if '</style>' in svg:
            svg = svg.replace('</style>', keyframes + '</style>', 1)
        else:
            svg = svg.replace('</svg>', '<style>' + keyframes + '</style></svg>', 1)
    return svg


def loop_stats_tiles_bars(svg: str) -> str:
    # Keep the staggered .t tiles and .b bars; remove only a global wipe wrapper elsewhere.
    tile_rule = '.t{opacity:.55;animation:statsTileLoop 12s cubic-bezier(.3,.7,.2,1) infinite}'
    bar_rule = '.b{transform-box:fill-box;transform-origin:bottom;animation:statsBarLoop 12s cubic-bezier(.3,.7,.2,1) infinite}'
    if re.search(r'\.t\s*\{[^}]*\}', svg):
        svg = re.sub(r'\.t\s*\{[^}]*\}', tile_rule, svg, count=1)
    else:
        svg = svg.replace('</style>', tile_rule + '</style>', 1)
    if re.search(r'\.b\s*\{[^}]*\}', svg):
        svg = re.sub(r'\.b\s*\{[^}]*\}', bar_rule, svg, count=1)
    else:
        svg = svg.replace('</style>', bar_rule + '</style>', 1)
    kf = (
        '@keyframes statsTileLoop{0%,100%{opacity:.25;transform:translateY(8px)}'
        '10%,78%{opacity:1;transform:translateY(0)}88%{opacity:.62;transform:translateY(2px)}}'
        '@keyframes statsBarLoop{0%,100%{transform:scaleY(.04)}18%,78%{transform:scaleY(1)}88%{transform:scaleY(.55)}}'
    )
    for name in ('statsTileLoop', 'statsBarLoop'):
        svg = re.sub(r'@keyframes\s+' + name + r'\s*\{(?:[^{}]|\{[^{}]*\})*\}', '', svg, count=1)
    svg = svg.replace('</style>', kf + '</style>', 1)
    # Don't let the reduced-motion rule accidentally suppress the default loop for everybody; respect user setting only.
    return svg


def animate_heatmap_columns(svg: str) -> str:
    """Reveal contribution cell columns left-to-right in a repeating cycle, never whole-canvas wipe."""
    # Work on rect opening tags only, preserving all unrelated paths, labels, colors, and data.
    rx = re.compile(r'<rect\b[^>]*?(?:/>|>)', re.S)
    rects = list(rx.finditer(svg))
    styles = "\n".join(re.findall(r'<style\b[^>]*>(.*?)</style>', svg, flags=re.S | re.I))
    cells = []
    for m in rects:
        tag = m.group(0)
        # Ignore rects that already have a child animation by construction; this tag only covers the opening element.
        attrs = {}
        for am in re.finditer(r'([\w:-]+)\s*=\s*["\']([^"\']*)["\']', tag):
            attrs[am.group(1)] = am.group(2)
        try:
            x = float(attrs.get('x', 'nan'))
            y = float(attrs.get('y', 'nan'))
            w = float(attrs.get('width', 'nan'))
            h = float(attrs.get('height', 'nan'))
        except ValueError:
            continue
        if not all(v == v for v in (x, y, w, h)):
            continue
        if not (20 <= x <= 2000 and 24 <= y <= 1000 and 4 <= w <= 18 and 4 <= h <= 18 and .78 <= w / h <= 1.28):
            continue
        if 'class' in attrs and any(k in attrs['class'].lower() for k in ('legend', 'dot', 'cursor')):
            continue
        class_names = attrs.get('class', '').split()
        if any(re.search(r'\.' + re.escape(class_name) + r'\s*\{[^}]*\banimation\s*:', styles, flags=re.S) for class_name in class_names):
            # The original heatmap already animates this class; keep its native column timing.
            continue
        try:
            peak_opacity = max(0.05, min(1.0, float(attrs.get('opacity', '1'))))
        except ValueError:
            peak_opacity = 1.0
        cells.append((m.start(), m.end(), tag, x, y, peak_opacity))
    xs = sorted({round(c[3], 1) for c in cells})
    if len(cells) < 40 or len(xs) < 12:
        log(f'INFO contrib-heatmap.svg: found {len(cells)} candidate cells across {len(xs)} columns; preserving the current per-cell animation')
        return svg
    col_index = {x: i for i, x in enumerate(xs)}
    edits = []
    for start, end, tag, x, y, peak_opacity in cells:
        # Preserve pre-existing cell-level column animations from the original heatmap renderer.
        if 'animate' in tag.lower():
            continue
        if not tag.rstrip().endswith('/>'):
            close_pos = svg.find('</rect>', end)
            if close_pos >= 0 and '<animate' in svg[end:close_pos].lower():
                continue
        idx = col_index[round(x, 1)]
        delay = 4.0 * idx / max(1, len(xs) - 1)
        peak = f'{peak_opacity:.3f}'.rstrip('0').rstrip('.')
        animation = (
            f'<animate attributeName="opacity" values="0.12;{peak};{peak};0.12" '
            f'keyTimes="0;0.16;0.78;1" dur="12s" begin="{delay:.3f}s" repeatCount="indefinite" />'
        )
        if tag.rstrip().endswith('/>'):
            open_tag = tag.rstrip()[:-2].rstrip()
            open_tag = re.sub(r'\sopacity\s*=\s*["\'][^"\']*["\']', '', open_tag)
            open_tag += ' opacity="0.12">'
            replacement = open_tag + animation + '</rect>'
        else:
            if re.search(r'\sopacity\s*=', tag):
                replacement = re.sub(r'\sopacity\s*=\s*["\'][^"\']*["\']', ' opacity="0.12"', tag, count=1)
            else:
                replacement = tag[:-1].rstrip() + ' opacity="0.12">'
            replacement += animation
        edits.append((start, end, replacement))
    for start, end, replacement in reversed(edits):
        svg = svg[:start] + replacement + svg[end:]
    if edits:
        log(f'Applied left-to-right loop to {len(edits)} heatmap cells across {len(xs)} columns')
    else:
        log(f'Heatmap already has per-cell animation; preserving it across {len(xs)} columns')
    return svg


def patch_readme_references() -> None:
    path = ROOT / 'README.md'
    if not path.exists():
        log('SKIP README.md: not found')
        return
    text = read_text(path)
    original = text
    # Change the centered tagline GIF back to its color-preserving theme-aware SVG.
    text = re.sub(
        r'<img\b(?=[^>]*\bsrc=["\']\./assets/animated/profile-tagline-loop\.gif["\'])[^>]*?/?>',
        lambda m: (
            '<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/profile-tagline.svg" />'
            '<source media="(prefers-color-scheme: light)" srcset="./assets/profile-tagline-light.svg" />'
            '<img src="./assets/profile-tagline.svg" width="100%" alt="Building scalable projects, designing premium interfaces, leading teams" /></picture>'
        ),
        text,
        count=1,
    )
    # Replace the transparent GIF conversions for each section header with their original colored, indefinitely animated SVGs.
    pattern = re.compile(r'<img\b[^>]*\bsrc=["\']\./assets/animated/(section-[a-z0-9-]+-accent-loop)\.gif["\'][^>]*?/?>', re.I)
    def replace_header(m: re.Match[str]) -> str:
        loop_name = m.group(1)
        base = loop_name.removesuffix('-loop')
        source = f'./assets/{base}.svg'
        light = f'./assets/{base}-light.svg'
        if not (ROOT / 'assets' / f'{base}.svg').exists():
            return m.group(0)
        alt_match = re.search(r'\balt=["\']([^"\']*)["\']', m.group(0), re.I)
        alt = (alt_match.group(1) if alt_match else base.replace('-', ' ')).replace('&', '&amp;')
        return (
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="{source}" />'
            f'<source media="(prefers-color-scheme: light)" srcset="{light}" />'
            f'<img src="{source}" width="100%" alt="{alt}" /></picture>'
        )
    text = pattern.sub(replace_header, text)
    # Preserve README final newline, but do not add extra blank lines.
    text = text.rstrip() + '\n'
    if text != original:
        backup = ROOT.parent / (ROOT.name + '-README.before-animation-color-fix.bak')
        if not backup.exists(): backup.write_text(original, encoding='utf-8', newline='\n')
        write_text(path, text)
        log('Updated only the tagline and section-heading image references in README.md')
    else:
        log('README.md: no tagline/header GIF references required changing')


def patch_workflow_for_future_runs() -> None:
    path = ROOT / '.github' / 'workflows' / 'update-profile-art.yml'
    if not path.exists():
        path = ROOT / '.github' / 'workflows' / 'update-profile-art.yaml'
    if not path.exists():
        log('INFO: no update-profile-art workflow found; local SVGs are still patched')
        return
    text = read_text(path)
    step = (
        '      - name: Apply scoped animation and light-theme fixes\n'
        '        run: python scripts/fix_profile_animation_scope.py --assets-only\n\n'
    )
    if 'python scripts/fix_profile_animation_scope.py --assets-only' not in text:
        anchor = '      - name: Commit refreshed profile visuals'
        if anchor in text:
            text = text.replace(anchor, step + anchor, 1)
        else:
            log(f'INFO: {path.relative_to(ROOT)} has no known commit step; skipped automatic workflow insertion')
    # Ensure the generated light files are committed by the scheduled workflow too.
    text = re.sub(
        r'file_pattern:\s*["\']?[^\n]+',
        'file_pattern: "data/contributions.json contrib-heatmap.svg contrib-heatmap-light.svg stats.svg stats-light.svg activity-graph.svg activity-graph-light.svg profile-ascii.svg profile-ascii-light.svg assets/*.svg"',
        text,
        count=1,
    )
    if text != read_text(path):
        write_text(path, text)
        log(f'Updated {path.relative_to(ROOT)} so future scheduled refreshes keep the scoped animations')


def make_light_root_svg(name: str) -> None:
    source = ROOT / name
    if not source.exists():
        log(f'SKIP {name}: not present in this repository')
        return
    svg = read_text(source)
    # Disable only the former full-canvas wipe; preserve the ASCII portrait itself unchanged.
    if name in WRAPPERS:
        svg = patch_outer_reveal(svg, WRAPPERS[name])
        svg = remove_added_sweep(svg, Path(name).stem)
    if name == 'activity-graph.svg':
        svg = patch_graph_line_only(svg)
    elif name == 'contrib-heatmap.svg':
        svg = animate_heatmap_columns(svg)
    elif name == 'stats.svg':
        svg = loop_stats_tiles_bars(svg)
    # The ASCII art is intentionally NOT given a new hide/redraw loop.
    ET.fromstring(svg)
    write_text(source, svg)
    light = one_pass_lightify(svg)
    ET.fromstring(light)
    write_text(ROOT / f'{source.stem}-light.svg', light)
    log(f'Updated {name}; generated {source.stem}-light.svg')


def main() -> None:
    assets_only = '--assets-only' in sys.argv[1:]
    # Generate high-contrast light variants for the existing colored header SVGs; their accent colors remain unchanged.
    for name in SECTION_FILES:
        source = ROOT / 'assets' / name
        target = source.with_name(source.stem + '-light.svg')
        if source.exists():
            make_light_section(source, target)
    make_light_tagline()
    for name in ('activity-graph.svg', 'contrib-heatmap.svg', 'profile-ascii.svg', 'stats.svg'):
        make_light_root_svg(name)
    if not assets_only:
        patch_readme_references()
        patch_workflow_for_future_runs()
    # Final XML validation for generated local SVGs and section variants.
    paths = list(ROOT.glob('*.svg')) + list((ROOT / 'assets').glob('*-light.svg'))
    validated = 0
    for path in paths:
        try:
            ET.parse(path)
            validated += 1
        except Exception as exc:
            raise SystemExit(f'SVG validation failed for {path.relative_to(ROOT)}: {exc}')
    log(f'Validated {validated} SVG files. No portfolio section content was rewritten.')


if __name__ == '__main__':
    main()
