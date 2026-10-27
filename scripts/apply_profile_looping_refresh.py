#!/usr/bin/env python3
"""Apply looping strokes and generate light-theme variants for local contribution visuals.
Run from the profile repository root: python scripts/apply_profile_looping_refresh.py
Only reads existing SVG assets and creates/updates the named light variants; contribution values are unchanged.
"""
from pathlib import Path
import re, sys, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
LIGHT_MAP = {
 '#070b14':'#F1F5F9','#08111f':'#F8FAFC','#080d1b':'#F8FAFC','#0a101f':'#F8FAFC','#0a1322':'#F8FAFC',
 '#0b1220':'#F8FAFC','#0b1322':'#F1F5F9','#0d1728':'#F8FAFC','#0e1b2d':'#EFF6FF','#101d31':'#F1F5F9',
 '#102237':'#EFF6FF','#10243b':'#E2E8F0','#0b2631':'#ECFEFF','#0c2032':'#E0F2FE','#0d1117':'#F8FAFC',
 '#161b22':'#E2E8F0','#1d314b':'#CBD5E1','#1d6471':'#99F6E4','#21425a':'#CBD5E1','#28516a':'#CBD5E1',
 '#29415a':'#CBD5E1','#29425c':'#CBD5E1','#164e63':'#BAE6FD','#2e4968':'#CBD5E1',
 '#e6f1ff':'#0F172A','#e8f1ff':'#0F172A','#f8fafc':'#0F172A','#e0f2fe':'#1E293B','#a5f3fc':'#0E7490',
 '#a9bdd5':'#475569','#9fb3c8':'#475569','#8da3be':'#475569','#94a3b8':'#475569','#64748b':'#64748B',
 '#c9d1d9':'#334155','#d1d5db':'#334155','#f9fafb':'#0F172A','#52657e':'#475569','#9ca3af':'#475569',
}
def lightify(s):
 for old,new in sorted(LIGHT_MAP.items(), key=lambda p:-len(p[0])): s=re.sub(re.escape(old), new, s, flags=re.I)
 return s

def viewbox_dims(s):
 m=re.search(r'<svg\b[^>]*viewBox="([^"]+)"', s)
 if m:
  vals=[float(x) for x in m.group(1).replace(',', ' ').split()]
  return vals[2], vals[3]
 m=re.search(r'<svg\b[^>]*width="([0-9.]+)"[^>]*height="([0-9.]+)"', s)
 return (float(m.group(1)),float(m.group(2))) if m else (1000,300)

def add_sweep(s, marker, strength='0.12'):
 if marker in s: return s
 w,h=viewbox_dims(s)
 # Narrow translucent beam; this is purely decorative and does not change plotted values or cells.
 beam=80
 overlay=(f'<!-- {marker} --><defs><linearGradient id="{marker}Grad" x1="0" y1="0" x2="1" y2="0">'
          '<stop offset="0" stop-color="#22D3EE" stop-opacity="0"/><stop offset="0.5" stop-color="#22D3EE" stop-opacity="0.65"/><stop offset="1" stop-color="#A78BFA" stop-opacity="0"/>'
          f'</linearGradient></defs><rect x="{-beam}" y="0" width="{beam}" height="{h:.1f}" fill="url(#{marker}Grad)" opacity="{strength}" pointer-events="none">'
          f'<animate attributeName="x" values="{-beam};{w:.1f}" dur="13s" repeatCount="indefinite"/></rect>')
 return s.replace('</svg>',overlay+'</svg>')

def loop_graph(s):
 # Turn a one-shot graph line reveal into a repeating draw/hold/reset sequence.
 pattern=re.compile(r'\.line\{stroke-dasharray:([0-9.]+);stroke-dashoffset:([0-9.]+);animation:draw 2\.8s cubic-bezier\(\.3,\.7,\.2,1\) \.25s forwards\}')
 m=pattern.search(s)
 if m:
  length=m.group(1)
  s=s[:m.start()]+f'.line{{stroke-dasharray:{length};stroke-dashoffset:{length};animation:drawloop 9s cubic-bezier(.3,.7,.2,1) infinite}}'+s[m.end():]
  s=s.replace('@keyframes draw{to{stroke-dashoffset:0}}', f'@keyframes drawloop{{0%{{stroke-dashoffset:{length};opacity:.48}}34%{{stroke-dashoffset:0;opacity:1}}76%{{stroke-dashoffset:0;opacity:1}}100%{{stroke-dashoffset:{length};opacity:.48}}}}')
 # Loop its area fade instead of leaving it frozen after first load.
 s=s.replace('.area{opacity:0;animation:fade 1.3s ease-out .65s forwards}', '.area{opacity:.15;animation:arealoop 9s ease-in-out infinite}')
 s=s.replace('@keyframes fade{to{opacity:.58}}', '@keyframes arealoop{0%,100%{opacity:.12}35%,75%{opacity:.58}}')
 # Preserve user data and accessibility text; validate SVG.
 return s

def main():
 for fname in ['activity-graph.svg','contrib-heatmap.svg','profile-ascii.svg','stats.svg']:
  p=ROOT/fname
  if not p.exists():
   print(f'SKIP: {fname} not found; leave existing README path as-is or create it first.')
   continue
  s=p.read_text(encoding='utf-8')
  if fname=='activity-graph.svg': s=loop_graph(s)
  if fname in ('contrib-heatmap.svg','stats.svg'):
   s=add_sweep(s, 'looping_refresh_'+Path(fname).stem, '0.08')
  ET.fromstring(s)
  p.write_text(s,encoding='utf-8',newline='\n')
  light=lightify(s)
  ET.fromstring(light)
  (ROOT/(p.stem+'-light.svg')).write_text(light,encoding='utf-8',newline='\n')
  print('Updated',fname,'and generated',p.stem+'-light.svg')

if __name__=='__main__': main()
