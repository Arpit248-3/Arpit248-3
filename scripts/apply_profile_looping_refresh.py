#!/usr/bin/env python3
"""Loop local profile visuals and generate high-contrast light-theme variants.
Run at the repository root: python scripts/apply_profile_looping_refresh.py
This script preserves contribution data. It only adjusts SVG animations/palettes and writes *-light.svg variants.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIGHT_MAP = {
    '#070b14':'#F8FAFC','#08111f':'#F8FAFC','#080d1b':'#F8FAFC','#0a101f':'#F8FAFC','#0a1322':'#F8FAFC',
    '#0b1220':'#F8FAFC','#0b1322':'#F1F5F9','#0d1728':'#F1F5F9','#0e1b2d':'#EFF6FF','#101d31':'#EFF6FF',
    '#102237':'#EFF6FF','#10243b':'#E2E8F0','#0b2631':'#ECFEFF','#0c2032':'#E0F2FE','#0d1117':'#F8FAFC',
    '#101827':'#F1F5F9','#101b2c':'#EFF6FF','#111722':'#F1F5F9','#111827':'#E2E8F0','#0f172a':'#F8FAFC',
    '#161b22':'#E2E8F0','#1d314b':'#CBD5E1','#1d6471':'#0E7490','#21425a':'#CBD5E1','#28516a':'#CBD5E1',
    '#29415a':'#CBD5E1','#29425c':'#CBD5E1','#283548':'#CBD5E1','#2e4968':'#CBD5E1','#30363d':'#CBD5E1',
    '#334155':'#CBD5E1','#164e63':'#BAE6FD','#1e293b':'#E2E8F0','#e6f1ff':'#0F172A','#e8f1ff':'#0F172A',
    '#f8fafc':'#0F172A','#f9fafb':'#0F172A','#e6edf3':'#0F172A','#dce6f2':'#1E293B','#d6e7ff':'#1E293B',
    '#e0f2fe':'#1E293B','#e2e8f0':'#1E293B','#d1d5db':'#334155','#c9d1d9':'#334155','#a5f3fc':'#0E7490',
    '#a9bdd5':'#475569','#9fb3c8':'#475569','#8da3be':'#475569','#94a3b8':'#475569','#7d8590':'#475569',
    '#9ca3af':'#475569','#64748b':'#475569','#52657e':'#475569','#b8c5d6':'#475569','#39d353':'#16A34A',
    '#26a641':'#15803D','#67e8f9':'#0E7490','#c4b5fd':'#6D28D9','#60a5fa':'#2563EB'
}
COLOR_RE = re.compile(r'#[0-9a-fA-F]{6}')
def lightify(svg: str) -> str:
    return COLOR_RE.sub(lambda m: LIGHT_MAP.get(m.group(0).lower(), m.group(0)), svg)

def dims(svg: str):
    m = re.search(r'<svg\b[^>]*viewBox="([^"]+)"', svg)
    if m:
        a=[float(x) for x in m.group(1).replace(',', ' ').split()]
        return a[2], a[3]
    m = re.search(r'<svg\b[^>]*width="([0-9.]+)"[^>]*height="([0-9.]+)"', svg)
    return (float(m.group(1)),float(m.group(2))) if m else (1000.0,300.0)

def add_sweep(svg: str, marker: str, opacity='0.12') -> str:
    if marker in svg: return svg
    w,h=dims(svg); beam=max(36,w*0.075)
    overlay=(f'<!-- {marker} -->'
      f'<defs><linearGradient id="{marker}Grad" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" stop-color="#22D3EE" stop-opacity="0"/>'
      '<stop offset="0.5" stop-color="#22D3EE" stop-opacity="0.8"/>'
      '<stop offset="1" stop-color="#A78BFA" stop-opacity="0"/>'
      f'</linearGradient></defs><rect x="{-beam:.1f}" y="0" width="{beam:.1f}" height="{h:.1f}" fill="url(#{marker}Grad)" opacity="{opacity}" pointer-events="none">'
      f'<animate attributeName="x" values="{-beam:.1f};{w:.1f};{-beam:.1f}" dur="15s" repeatCount="indefinite"/></rect>')
    return svg.replace('</svg>', overlay+'</svg>')

def loop_graph(svg: str) -> str:
    # Turn the first-draw animation into a deliberate draw / hold / reset loop.
    svg = re.sub(r'\.line\{stroke-dasharray:([0-9.]+);stroke-dashoffset:([0-9.]+);animation:[^}]*\}',
      lambda m: f'.line{{stroke-dasharray:{m.group(1)};stroke-dashoffset:{m.group(1)};animation:drawloop 10s cubic-bezier(.3,.7,.2,1) infinite}}', svg)
    # Replace the one-shot draw keyframes if present; fallback adds looping CSS if not.
    svg = re.sub(r'@keyframes draw\{to\{stroke-dashoffset:0\}\}',
      lambda m: (lambda L: f'@keyframes drawloop{{0%{{stroke-dashoffset:{L};opacity:.55}}35%{{stroke-dashoffset:0;opacity:1}}78%{{stroke-dashoffset:0;opacity:1}}100%{{stroke-dashoffset:{L};opacity:.55}}}}')(re.search(r'\.line\{stroke-dasharray:([0-9.]+)',svg).group(1) if re.search(r'\.line\{stroke-dasharray:([0-9.]+)',svg) else '1200'), svg)
    svg = re.sub(r'\.area\{opacity:0;animation:[^}]*\}', '.area{opacity:.12;animation:arealoop 10s ease-in-out infinite}', svg)
    svg = re.sub(r'@keyframes fade\{to\{opacity:([0-9.]+)\}\}', '@keyframes arealoop{0%,100%{opacity:.12}35%,78%{opacity:.55}}', svg)
    svg = re.sub(r'\.header\{opacity:0;animation:[^}]*\}', '.header{opacity:.82;animation:headerloop 10s ease-in-out infinite}', svg)
    if '@keyframes headerloop' not in svg:
        svg = svg.replace('</style>', '@keyframes headerloop{0%,100%{opacity:.82}12%,85%{opacity:1}}\n</style>')
    # Add a spark that travels over the contribution path so the loop is visible, not just a static line.
    if 'id="activity-loop-spark"' not in svg:
        m = re.search(r'<path class="line" d="([^"]+)"', svg)
        if m:
            d=m.group(1)
            spark=(f'<circle id="activity-loop-spark" r="4.2" fill="#22D3EE" stroke="#F8FAFC" stroke-width="1.3">'
                   f'<animateMotion dur="10s" repeatCount="indefinite" path="{d}" />'
                   '<animate attributeName="r" values="3;4.8;3" dur="2.2s" repeatCount="indefinite" />'
                   '</circle>')
            svg = svg.replace('</svg>', spark+'</svg>')
    return svg

def loop_stats(svg: str) -> str:
    # The generator initially animates cards/bars once with forwards. Let them softly re-enter every 12 seconds.
    svg = re.sub(r'\.t\{opacity:0;animation:in [^}]*\}', '.t{opacity:.72;animation:statloop 12s cubic-bezier(.3,.7,.2,1) infinite}', svg)
    svg = re.sub(r'\.b\{transform-box:fill-box;transform-origin:bottom;transform:scaleY\(0\);animation:grow [^}]*\}', '.b{transform-box:fill-box;transform-origin:bottom;animation:barloop 12s cubic-bezier(.3,.7,.2,1) infinite}', svg)
    svg = svg.replace('@keyframes in{0%{opacity:0;transform:translateY(14px)}100%{opacity:1;transform:translateY(0)}}', '@keyframes statloop{0%,100%{opacity:.46;transform:translateY(8px)}8%,82%{opacity:1;transform:translateY(0)}90%{opacity:.72;transform:translateY(2px)}}')
    svg = svg.replace('@keyframes grow{to{transform:scaleY(1)}}', '@keyframes barloop{0%,100%{transform:scaleY(.04)}16%,80%{transform:scaleY(1)}90%{transform:scaleY(.55)}}')
    if '@keyframes statloop' not in svg:
        svg = svg.replace('</style>', '@keyframes statloop{0%,100%{opacity:.46;transform:translateY(8px)}8%,82%{opacity:1;transform:translateY(0)}90%{opacity:.72;transform:translateY(2px)}}\n</style>')
    if '@keyframes barloop' not in svg:
        svg = svg.replace('</style>', '@keyframes barloop{0%,100%{transform:scaleY(.04)}16%,80%{transform:scaleY(1)}90%{transform:scaleY(.55)}}\n</style>')
    return svg

def main():
    targets=['activity-graph.svg','contrib-heatmap.svg','profile-ascii.svg','stats.svg']
    for name in targets:
        p=ROOT/name
        if not p.exists():
            print(f'SKIP {name}: not present. It will not be overwritten.')
            continue
        svg=p.read_text(encoding='utf-8')
        if name == 'activity-graph.svg': svg=loop_graph(svg)
        elif name == 'stats.svg': svg=loop_stats(svg)
        if name in ('contrib-heatmap.svg','profile-ascii.svg','stats.svg'):
            svg=add_sweep(svg, 'looping_refresh_'+p.stem, '0.09')
        ET.fromstring(svg)
        p.write_text(svg,encoding='utf-8',newline='\n')
        light=lightify(svg)
        ET.fromstring(light)
        (ROOT/(p.stem+'-light.svg')).write_text(light,encoding='utf-8',newline='\n')
        print(f'Updated {name} and generated {p.stem}-light.svg')

if __name__ == '__main__': main()
