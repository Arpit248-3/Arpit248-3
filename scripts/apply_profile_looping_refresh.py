#!/usr/bin/env python3
"""Patch looping/reveal animations for existing local GitHub contribution visuals.
No third-party packages required. Run from repository root:
    python scripts/apply_profile_looping_refresh.py
Preserves the user's existing content/data in activity-graph.svg, contrib-heatmap.svg, profile-ascii.svg and stats.svg.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SVG='http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')
LIGHT_MAP={
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
 '#26a641':'#15803D','#67e8f9':'#0E7490','#c4b5fd':'#6D28D9','#60a5fa':'#2563EB',
 '#f1f5f9':'#0F172A','#aab8cb':'#475569'
}
def tag(el): return el.tag.split('}',1)[-1]
def dims(root):
    try:
        v=[float(x) for x in root.get('viewBox','0 0 1000 300').replace(',',' ').split()]
        return v[2],v[3]
    except Exception: return 1000.0,300.0
def new_clip(root, ident, w, h):
    defs=next((x for x in list(root) if tag(x)=='defs'),None)
    if defs is None:
        defs=ET.Element(f'{{{SVG}}}defs'); root.insert(0,defs)
    cp=ET.SubElement(defs,f'{{{SVG}}}clipPath',{'id':ident,'clipPathUnits':'userSpaceOnUse'})
    rect=ET.SubElement(cp,f'{{{SVG}}}rect',{'x':'0','y':'0','width':f'{w:.2f}','height':'0'})
    ET.SubElement(rect,f'{{{SVG}}}animate',{
        'attributeName':'height','values':f'0;{h:.2f};{h:.2f};0','keyTimes':'0;0.36;0.79;1',
        'dur':'12s','repeatCount':'indefinite'
    })
def wrap_foreground(root, ident):
    w,h=dims(root)
    if any(x.get('id')==ident for x in root.iter()): return
    new_clip(root,ident,w,h)
    # Keep defs, accessibility, styles, and full-canvas backgrounds outside the animated wipe.
    children=list(root)
    keep=[]; content=[]
    for child in children:
        if tag(child) in ('defs','title','desc','style','metadata'):
            keep.append(child); continue
        if tag(child)=='rect':
            try:
                x=float(child.get('x','0')); y=float(child.get('y','0'))
                rw=float(child.get('width',str(w)).replace('%','')); rh=float(child.get('height',str(h)).replace('%',''))
                if abs(x)<1 and abs(y)<1 and (rw>=w*.98 or child.get('width')=='100%') and (rh>=h*.98 or child.get('height')=='100%'):
                    keep.append(child); continue
            except Exception: pass
        content.append(child)
    # Build the group at the original content start to preserve z-order.
    group=ET.Element(f'{{{SVG}}}g',{'id':ident,'clip-path':f'url(#{ident}Clip)'})
    for child in content: group.append(child)
    # We created a clipPath id ident, and name the wrapper id identGroup.
    group.set('id',ident+'Group')
    # correct clip URL
    group.set('clip-path',f'url(#{ident})')
    for c in list(root): root.remove(c)
    # Insert defs before original background, then rest with group where the foreground began.
    # Simpler ordering: defs/metadata first, then original full-canvas bg shapes, then group contents.
    for c in keep: root.append(c)
    root.append(group)
def loop_profile_group(root, ident):
    if any(x.get('id')==ident for x in root.iter()): return
    w,h=dims(root); new_clip(root,ident,w,h)
    found=None
    for e in root.iter():
        if tag(e)=='g' and 'ascii portrait' in e.get('aria-label','').lower():
            found=e; break
    if found is not None: found.set('clip-path',f'url(#{ident})')
    else: wrap_foreground(root,ident)
def loop_graph_css(s):
    # Repeating line draw/reset; if styles differ, the clip reveal below still guarantees a full reset.
    m=re.search(r'\.line\{([^}]*)\}',s)
    if m:
        body=m.group(1)
        da=re.search(r'stroke-dasharray:([0-9.]+)',body)
        do=da.group(1) if da else '1200'
        body=re.sub(r'animation:[^;]+;?','',body)
        body=re.sub(r'stroke-dashoffset:[^;]+;?','',body)
        body += f';stroke-dasharray:{do};stroke-dashoffset:{do};animation:drawLoop 12s cubic-bezier(.3,.7,.2,1) infinite'
        s=s[:m.start()]+'.line{'+body+'}'+s[m.end():]
    s=re.sub(r'@keyframes\s+draw\s*\{\s*to\s*\{\s*stroke-dashoffset\s*:\s*0\s*;?\s*\}\s*\}',
             f'@keyframes drawLoop{{0%,100%{{stroke-dashoffset:1200;opacity:.35}}34%,78%{{stroke-dashoffset:0;opacity:1}}}}',s)
    if '@keyframes drawLoop' not in s and '</style>' in s:
        s=s.replace('</style>','@keyframes drawLoop{0%,100%{stroke-dashoffset:1200;opacity:.35}34%,78%{stroke-dashoffset:0;opacity:1}}</style>')
    return s
def lightify(s):
    # One-pass exact color token replacement; the replacement is not processed a second time.
    import re
    return re.sub(r'#[0-9a-fA-F]{6}',lambda m:LIGHT_MAP.get(m.group(0).lower(),m.group(0)),s)
def main():
    root_targets={
        'activity-graph.svg':'loopRevealActivityGraph',
        'contrib-heatmap.svg':'loopRevealHeatmap',
        'profile-ascii.svg':'loopRevealAsciiPortrait',
        'stats.svg':'loopRevealStats'
    }
    for filename,ident in root_targets.items():
        path=ROOT/filename
        if not path.exists():
            print(f'SKIP {filename}: file not present; no replacement was created.')
            continue
        text=path.read_text(encoding='utf-8')
        if filename=='activity-graph.svg': text=loop_graph_css(text)
        root=ET.fromstring(text)
        if filename=='profile-ascii.svg': loop_profile_group(root,ident)
        else: wrap_foreground(root,ident)
        content=ET.tostring(root,encoding='unicode',short_empty_elements=True)
        # Keep every root graphic's animation loops explicit and deterministic.
        ET.fromstring(content)
        path.write_text(content,encoding='utf-8',newline='\n')
        light=lightify(content)
        ET.fromstring(light)
        (ROOT/(path.stem+'-light.svg')).write_text(light,encoding='utf-8',newline='\n')
        print(f'Updated {filename}; generated {path.stem}-light.svg with the same repeating draw/reset loop.')
if __name__=='__main__': main()
