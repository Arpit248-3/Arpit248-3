#!/usr/bin/env python3
"""Generate theme-aware looping leadership, skills and activity-chart GIFs.
Run from the GitHub profile repository root:
    python scripts/generate_profile_animation_assets.py

The script reads data/contributions.json, generates GIFs under assets/animated,
updates only the existing Leadership/Technical Skills/Contribution line-chart
picture references in README.md, and inserts itself into update-profile-art.yml
so scheduled contribution refreshes regenerate the graph GIFs.
It does not replace README.md, change text/content order, or edit other sections.
Requires Pillow: python -m pip install Pillow
"""
from __future__ import annotations
import json, math, re, sys, os
from functools import lru_cache
from datetime import date
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
ANIM = ROOT / "assets" / "animated"

DARK = {
    "bg1":"#08111F", "bg2":"#10243A", "card":"#0D1A2B", "card2":"#101F33",
    "border":"#2A415B", "text":"#ECF5FF", "muted":"#9BB0C8", "faint":"#6F86A2",
    "blue":"#60A5FA", "cyan":"#22D3EE", "teal":"#2DD4BF", "violet":"#A78BFA",
    "green":"#34D399", "amber":"#FBBF24", "red":"#FB7185", "line":"#1D314B",
    "pill":"#12263A", "pill2":"#152A41", "glow":"#22D3EE", "chartbg":"#0B1220",
    "chartcard":"#0E1B2D", "grid":"#24364E", "charttext":"#DDE9F7", "chartmuted":"#91A4BD",
}
LIGHT = {
    "bg1":"#F7FAFE", "bg2":"#EAF3FC", "card":"#FFFFFF", "card2":"#F4F8FD",
    "border":"#D4E1EF", "text":"#152B43", "muted":"#4E647C", "faint":"#71869D",
    "blue":"#2563EB", "cyan":"#0891B2", "teal":"#0F9F92", "violet":"#7C3AED",
    "green":"#15803D", "amber":"#B45309", "red":"#BE123C", "line":"#E0EAF4",
    "pill":"#EAF3FE", "pill2":"#E5F8FA", "glow":"#0891B2", "chartbg":"#F3F7FC",
    "chartcard":"#FFFFFF", "grid":"#DCE6F0", "charttext":"#172B45", "chartmuted":"#526880",
}
ACCENTS = [DARK["blue"], DARK["cyan"], DARK["teal"], DARK["violet"], DARK["amber"], "#818CF8"]

# Fonts are platform-appropriate and gracefully fall back to the default bitmap font.
def font(size, bold=False, mono=False):
    candidates=[]
    if os.name == 'nt':
        candidates += ([r'C:\Windows\Fonts\consolab.ttf', r'C:\Windows\Fonts\consola.ttf'] if mono else ([r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\arialbd.ttf'] if bold else [r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\arial.ttf']))
    candidates += (["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf"] if mono and bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf"] if mono else ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"])
    for p in candidates:
        try: return ImageFont.truetype(p, size)
        except OSError: pass
    return ImageFont.load_default()

F = {
    'tiny': font(10, mono=True), 'small': font(12), 'smallb': font(12, bold=True),
    'label': font(13, mono=True, bold=True), 'body': font(14), 'bodyb': font(14, bold=True),
    'title': font(18, bold=True), 'hero': font(31, bold=True), 'hero2': font(18, bold=True),
    'sub': font(16), 'hskill': font(17, bold=True), 'pill': font(12, bold=True),
}

def rgb(hexcol):
    h=hexcol.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def rgba(hexcol, alpha=255): return (*rgb(hexcol), alpha)

@lru_cache(maxsize=16)
def _gradient_bg_cached(size, start, end, vertical=False):
    # Build gradients with Pillow draw primitives (fast and deterministic), not Python per-pixel loops.
    w,h=size; img=Image.new('RGB', size); d=ImageDraw.Draw(img); a=rgb(start); b=rgb(end)
    if vertical:
        span=max(1,h-1)
        for y in range(h):
            t=y/span; c=tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3))
            d.line((0,y,w,y),fill=c)
    else:
        span=max(1,w-1)
        for x in range(w):
            t=x/span; c=tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3))
            d.line((x,0,x,h),fill=c)
    return img

def gradient_bg(size, start, end, vertical=False):
    return _gradient_bg_cached(size,start,end,vertical).copy()

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def centered_text(draw, xy, txt, fo, fill):
    draw.text(xy, txt, font=fo, fill=fill, anchor='mm')

def draw_gradient_line(draw, pts, colors, width=3):
    # Interpolate color along the polyline segment-by-segment.
    if len(pts)<2: return
    total=len(pts)-1
    c0,c1,c2=[rgb(c) for c in colors]
    for i in range(total):
        t=i/max(1,total-1)
        if t<.5:
            u=t*2; c=tuple(round(c0[k]*(1-u)+c1[k]*u) for k in range(3))
        else:
            u=(t-.5)*2; c=tuple(round(c1[k]*(1-u)+c2[k]*u) for k in range(3))
        draw.line([pts[i],pts[i+1]], fill=(*c,255), width=width)

def save_loop_gif(frames, path, duration=100):
    # Quantize with one shared palette based on the first frame; make endless playback explicit.
    path.parent.mkdir(parents=True, exist_ok=True)
    # Choose a fully revealed frame so the shared palette includes every card/theme accent.
    palette_frame=frames[len(frames)//2] if len(frames)>1 else frames[0]
    pal=palette_frame.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    palframes=[]
    for frame in frames:
        palframes.append(frame.convert('RGB').quantize(palette=pal, dither=Image.Dither.NONE))
    palframes[0].save(path, save_all=True, append_images=palframes[1:], duration=duration,
                      loop=0, optimize=True, disposal=2)

def draw_leadership(theme, light=False, frames_count=42):
    C=LIGHT if light else DARK; frames=[]; W,H=1200,300
    for fi in range(frames_count):
        t=fi/max(1,frames_count-1); phase=t*2*math.pi
        im=gradient_bg((W,H), C['bg1'], C['bg2'], vertical=False)
        # subtle radial light blooms
        bloom=Image.new('RGBA',(W,H),(0,0,0,0)); bd=ImageDraw.Draw(bloom,'RGBA')
        for rad,alpha in [(150,14),(112,18),(76,20)]:
            bd.ellipse((115-rad,148-rad,115+rad,148+rad),fill=rgba(C['cyan'],alpha))
        im=Image.alpha_composite(im.convert('RGBA'),bloom.filter(ImageFilter.GaussianBlur(18))).convert('RGB')
        d=ImageDraw.Draw(im,'RGBA')
        # card frame
        rounded(d,(12,12,1188,288),22,rgba(C['card'],235),rgba(C['border'],255),2)
        rounded(d,(25,25,1175,275),18,(0,0,0,0),rgba(C['border'],190),1)
        # Top fine ruled accents
        d.line((285,57,1145,57),fill=rgba(C['border'],155),width=1)
        # Orbit/network illustration stays entirely to the left of the text column.
        cx,cy=132,146
        for r,alpha,offset in [(83,75,0),(68,90,.8),(53,85,1.9)]:
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=rgba(C['cyan'],alpha),width=1)
        # slightly dashed outer orbit
        r=91
        dashpts=[]
        for a in range(0,360,6):
            rad=math.radians(a+t*360)
            dashpts.append((cx+r*math.cos(rad),cy+r*math.sin(rad)))
        for i in range(0,len(dashpts)-1,3):
            d.line((dashpts[i],dashpts[i+1]),fill=rgba(C['blue'],105),width=1)
        # Network points rotate along orbital rings
        nodes=[]
        for j,(r0,ang,col) in enumerate([(54,18,C['cyan']),(68,112,C['violet']),(60,205,C['teal']),(74,292,C['blue']),(43,245,C['cyan'])]):
            a=math.radians(ang+t*360*(1 if j%2==0 else -1))
            nodes.append((cx+r0*math.cos(a),cy+r0*math.sin(a),col))
        for i in range(len(nodes)):
            n1=nodes[i]; n2=nodes[(i+1)%len(nodes)]
            d.line((n1[0],n1[1],n2[0],n2[1]),fill=rgba(C['cyan'],100),width=2)
        for nx,ny,col in nodes:
            pulse=2.8+1.6*(.5+.5*math.sin(phase*2+nx*.02))
            d.ellipse((nx-pulse-3,ny-pulse-3,nx+pulse+3,ny+pulse+3),fill=rgba(col,35))
            d.ellipse((nx-pulse,ny-pulse,nx+pulse,ny+pulse),fill=rgba(col,255))
        # central sensor
        d.ellipse((cx-29,cy-29,cx+29,cy+29),fill=rgba(C['card2'],250),outline=rgba(C['cyan'],235),width=2)
        d.ellipse((cx-21,cy-21,cx+21,cy+21),outline=rgba(C['blue'],150),width=1)
        d.line((cx-12,cy+7,cx-2,cy-4,cx+4,cy+2,cx+14,cy-12),fill=rgba(C['text'],255),width=3,joint='curve')
        # TEAM LEAD pill
        rounded(d,(304,36,432,62),13,rgba(C['pill'],250),rgba(C['cyan'],210),1)
        d.ellipse((316,46,324,54),fill=rgba(C['teal'],255))
        d.text((332,43),'TEAM LEAD',font=F['label'],fill=rgba(C['cyan'],255))
        # Text area, no left-side overlap and no extra leadership label/tagline.
        title_color=C['text'] if not light else '#12314D'
        d.text((304,72),'AI for Bharat Hackathon 2026',font=F['hero'],fill=rgba(title_color,255),stroke_width=0)
        d.text((305,119),'AyuScout AI',font=F['hero2'],fill=rgba(C['cyan'] if not light else '#0E7490',255))
        d.text((305,151),'Pharmacovigilance intelligence platform',font=F['body'],fill=rgba(C['muted'],255))
        d.text((305,177),'Safety-signal review · Patient-data protection · Regulatory reporting',font=F['body'],fill=rgba(C['muted'],255))
        # Underline scan: line stays visible, a short beam traverses horizontally.
        d.line((304,208,1136,208),fill=rgba(C['border'],210),width=1)
        scanx=304 + ((t*2.0)%1.0)*832
        beamw=130
        draw_gradient_line(d,[(max(304,scanx-beamw),208),(scanx,208),(min(1136,scanx+beamw),208)],[C['blue'],C['cyan'],C['violet']],2)
        d.ellipse((scanx-3,205,scanx+3,211),fill=rgba(C['cyan'],255))
        # Bottom moving wave, always legible; separate from the text block.
        wave=[]
        for x in range(12,1188,5):
            yy=246 + 12*math.sin((x/W)*math.pi*3.4 + phase) + 3*math.sin((x/W)*math.pi*7.0-phase*.7)
            wave.append((x,yy))
        draw_gradient_line(d,wave,[C['teal'],C['blue'],C['violet']],1)
        # Dotted travelling light on wave
        sparkx=20 + ((t*2.0)%1)*1160
        sparky=246 + 12*math.sin((sparkx/W)*math.pi*3.4 + phase) + 3*math.sin((sparkx/W)*math.pi*7.0-phase*.7)
        d.ellipse((sparkx-4,sparky-4,sparkx+4,sparky+4),fill=rgba(C['cyan'],245))
        # tiny ambient particles on the right
        for j,(x0,y0,col) in enumerate([(1094,52,C['teal']),(1120,72,C['violet']),(1078,82,C['blue'])]):
            a=.35+.65*(.5+.5*math.sin(phase*1.4+j*2))
            d.ellipse((x0-2.4,y0-2.4,x0+2.4,y0+2.4),fill=rgba(col,int(255*a)))
        frames.append(im.convert('RGB'))
    return frames

SKILLS = [
    ("PROGRAMMING & QUERY", ["Python", "C++", "JavaScript", "MySQL / SQL"], "Language fundamentals · DSA · SQL querying"),
    ("FRONTEND & UI", ["React", "React Native", "Vite", "UI Design"], "Component design · Responsive layouts · State"),
    ("BACKEND & APIs", ["FastAPI", "Django", "Node.js", "REST APIs"], "API design · Validation · Service integration"),
    ("DATABASES", ["MySQL", "PostgreSQL", "MongoDB", "SQLite"], "Schema design · Queries · Data modeling"),
    ("TOOLS & DELIVERY", ["Git", "GitHub", "Vercel", "VS Code", "Anaconda"], "Version control · Development · Deployment"),
    ("AI & RETRIEVAL", ["LSTM", "Transformers", "XGBoost", "RAG / BM25"], "Forecasting · Hybrid retrieval · Verification"),
]
SKILL_ACCENTS = ["#60A5FA", "#22D3EE", "#2DD4BF", "#A78BFA", "#F59E0B", "#818CF8"]

def mix_color(hexcol, base, alpha):
    a=rgb(hexcol); b=rgb(base)
    return tuple(round(a[i]*alpha+b[i]*(1-alpha)) for i in range(3))

def draw_skill_card(theme, idx, reveal, yshift=0):
    C=LIGHT if theme=='light' else DARK
    W,H=560,174
    layer=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(layer,'RGBA')
    accent=SKILL_ACCENTS[idx]
    # Fade whole card through alpha, while its surface stays understated and premium.
    alpha=int(255*max(0,min(1,reveal)))
    fill=rgba(C['card'] if theme=='light' else C['card'], alpha)
    edge=rgba(C['border'],alpha)
    rounded(d,(2,2,W-2,H-2),18,fill,edge,2)
    # Accent top rail and subtle left rail
    d.rounded_rectangle((16,1,W-16,5),radius=2,fill=rgba(accent,alpha))
    d.rounded_rectangle((2,20,6,H-20),radius=2,fill=rgba(accent,alpha))
    # Number pill
    rounded(d,(20,22,66,46),11,rgba(accent,int(38*reveal if reveal<=1 else 38)),rgba(accent,alpha),1)
    d.text((32,27),f'{idx+1:02d} /',font=F['label'],fill=rgba(accent,alpha))
    d.text((79,22),SKILLS[idx][0],font=F['hskill'],fill=rgba(C['text'],alpha))
    d.line((20,56,W-20,56),fill=rgba(C['border'],alpha),width=1)
    # compact labeled chips, dynamic width to ensure all entries fit the card
    tags=SKILLS[idx][1]
    left=20; top=70; available=W-40; gap=8
    raw_widths=[]
    for tag in tags:
        tw=d.textbbox((0,0),tag,font=F['pill'])[2]
        raw_widths.append(tw+25)
    sumw=sum(raw_widths)+gap*(len(tags)-1)
    shrink=min(1.0,available/max(1,sumw))
    x=left
    for j,tag in enumerate(tags):
        cw=max(55,int(raw_widths[j]*shrink))
        # chip colors are restrained tints instead of heavy solid rectangular badges
        chipfill=rgba(accent,int(24*reveal))
        rounded(d,(x,top,x+cw,top+28),8,chipfill,rgba(accent,alpha),1)
        textfill=rgba(C['text'],alpha)
        d.text((x+cw/2,top+14),tag,font=F['pill'],fill=textfill,anchor='mm')
        x += cw+gap
    # Bottom explanatory label uses enough contrast in both themes.
    d.text((20,135),SKILLS[idx][2],font=F['small'],fill=rgba(C['muted'],alpha))
    # animated travelling point on card's own edge
    dotx=25+((idx+1)*17 + reveal*350)%(W-50)
    d.ellipse((dotx-2.5,H-13,dotx+2.5,H-8),fill=rgba(accent,alpha))
    return layer

def draw_skills_grid(theme, frames_count=72):
    C=LIGHT if theme=='light' else DARK; frames=[]
    W,H=1200,670; cycle=frames_count*.10
    for fi in range(frames_count):
        t=fi/max(1,frames_count-1)*cycle; im=gradient_bg((W,H),C['bg1'],C['bg2'],vertical=True)
        # subtle background washes
        wash=Image.new('RGBA',(W,H),(0,0,0,0)); wd=ImageDraw.Draw(wash,'RGBA')
        wd.ellipse((-120,-160,460,380),fill=rgba(C['blue'],14 if theme=='light' else 12))
        wd.ellipse((760,360,1350,920),fill=rgba(C['violet'],15 if theme=='light' else 11))
        im=Image.alpha_composite(im.convert('RGBA'),wash.filter(ImageFilter.GaussianBlur(38))).convert('RGB')
        d=ImageDraw.Draw(im,'RGBA')
        rounded(d,(10,10,1190,660),22,rgba(C['card'],160 if theme=='light' else 140),rgba(C['border'],220),2)
        # header, always present so only the six skill cards animate
        d.text((32,26),'ENGINEERING TOOLKIT',font=F['label'],fill=rgba(C['cyan'],255))
        d.text((1168,26),'06 SKILL DOMAINS',font=F['tiny'],fill=rgba(C['muted'],255),anchor='ra')
        d.line((32,47,1168,47),fill=rgba(C['border'],230),width=1)
        # Composite all animated card layers into RGBA once per frame; only the cards change opacity.
        base_rgba=im.convert('RGBA')
        # row-by-row sequence: left-to-right across each row; reverse-order fade-out at the end.
        for idx in range(6):
            col=idx%2; row=idx//2
            x=24 + col*576
            y=58 + row*196
            start=.25+idx*.48
            in_dur=.42
            p=max(0,min(1,(t-start)/in_dur))
            # Cards reverse out one by one, bottom-right first, without wiping the frame.
            out_start=5.55+(5-idx)*.08
            out_dur=.30
            if t>out_start:
                p *= max(0,1-(t-out_start)/out_dur)
            if t>=cycle-.05: p=0
            if p<=0: continue
            ease=1-(1-p)**3
            shifted_y=int(y+13*(1-ease))
            card=draw_skill_card(theme,idx,ease)
            base_rgba.alpha_composite(card,(x,shifted_y))
        im=base_rgba.convert('RGB')
        d=ImageDraw.Draw(im,'RGBA')
        # moving fine scan line is limited to the header/footer, never a full-panel wipe
        scanx=36+((t/3.2)%1)*1128
        d.line((scanx,642,min(1168,scanx+90),642),fill=rgba(C['cyan'],180),width=1)
        d.text((32,646),'PROGRAMMING  ·  USER INTERFACES  ·  APIS  ·  DATA  ·  AI SYSTEMS',font=F['tiny'],fill=rgba(C['faint'],240))
        frames.append(im.convert('RGB'))
    return frames

# chart line smoothing, sampled cubic segments

def make_smooth_points(points, samples=8):
    if len(points)<2: return points[:]
    out=[]
    for i in range(len(points)-1):
        p0=points[max(i-1,0)]; p1=points[i]; p2=points[i+1]; p3=points[min(i+2,len(points)-1)]
        for j in range(samples):
            t=j/samples; t2=t*t; t3=t2*t
            x=.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y=.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x,y))
    out.append(points[-1]); return out

def data_points():
    if not DATA.exists():
        raise SystemExit(f"Contribution data not found: {DATA}. Run your existing fetch/render workflow first.")
    try: data=json.loads(DATA.read_text(encoding='utf-8'))
    except Exception as exc: raise SystemExit(f"Unable to read {DATA}: {exc}")
    days=data.get('days',[])
    records=[]
    for item in days[-31:]:
        try: records.append((date.fromisoformat(str(item['date'])),max(0,int(item.get('count',0)))))
        except Exception as exc: raise SystemExit(f"Invalid daily contribution record {item!r}: {exc}")
    if len(records)<7:
        raise SystemExit(f"Only {len(records)} daily records found in data/contributions.json; need at least 7 to render a meaningful 31-day chart. Run scripts/fetch_contributions.py first.")
    return records

def draw_activity_chart(theme, records, frames_count=64):
    C=LIGHT if theme=='light' else DARK
    W,H=1120,340; left,right,top,bottom=76,1084,76,256
    vals=[c for _,c in records]; maxv=max(vals or [0])
    scale=max(2,math.ceil(maxv/5)*5) if maxv>6 else max(2,maxv+1)
    raw=[]
    for i,(_,count) in enumerate(records):
        x=left+(right-left)*i/max(1,len(records)-1)
        y=bottom-(bottom-top)*count/scale
        raw.append((x,y,count))
    core=make_smooth_points([(x,y) for x,y,_ in raw], samples=7)
    # cumulative fraction for progressive line reveal
    cum=[0.0]
    for a,b in zip(core,core[1:]): cum.append(cum[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
    total=cum[-1] if cum[-1] else 1.0
    norm=[v/total for v in cum]
    ticks=sorted(set([scale,round(scale*.75),round(scale*.5),round(scale*.25),0]),reverse=True)
    xidx=sorted(set([0,7,14,21,len(records)-1]))
    labels=[(records[i][0].strftime('%b')+' '+str(records[i][0].day),raw[i][0]) for i in xidx if i<len(records)]
    total_count=sum(vals)
    gradient_cols=[C['blue'],C['cyan'],C['teal']]
    frames=[]
    for fi in range(frames_count):
        t=fi/max(1,frames_count-1)*6.4
        if t<3.3: prog=t/3.3
        elif t<4.65: prog=1.0
        else: prog=max(0.0,1-(t-4.65)/(6.4-4.65))
        im=gradient_bg((W,H),C['chartbg'],C['chartcard'],vertical=True)
        d=ImageDraw.Draw(im,'RGBA')
        rounded(d,(8,8,W-8,H-8),20,rgba(C['chartcard'],255),rgba(C['border'],255),2)
        # top-left tiny status lights
        d.ellipse((24,22,32,30),fill=(251,113,133,255)); d.ellipse((39,22,47,30),fill=(251,191,36,255)); d.ellipse((54,22,62,30),fill=rgba(C['teal'],255))
        d.text((76,18),'GITHUB ACTIVITY',font=F['label'],fill=rgba(C['charttext'],255))
        start=records[0][0].strftime('%b')+' '+str(records[0][0].day)
        end=records[-1][0].strftime('%b')+' '+str(records[-1][0].day)
        d.text((76,38),f'{start} — {end} · {total_count} contributions',font=F['small'],fill=rgba(C['chartmuted'],255))
        d.text((1084,23),'LAST 31 DAYS',font=F['smallb'],fill=rgba(C['teal'],255),anchor='ra')
        # static grid and axis labels
        for val in ticks:
            y=bottom-(bottom-top)*val/scale
            dashx=left
            while dashx<right:
                d.line((dashx,y,min(dashx+3,right),y),fill=rgba(C['grid'],215),width=1)
                dashx+=11
            d.text((left-22,y-7),str(val),font=F['small'],fill=rgba(C['chartmuted'],255),anchor='ra')
        for lab,x in labels:
            d.text((x,286),lab,font=F['small'],fill=rgba(C['chartmuted'],255),anchor='mm')
        d.text((1082,318),'LOCAL · DAILY ACTIVITY SNAPSHOT',font=F['tiny'],fill=rgba(C['chartmuted'],255),anchor='ra')
        # stable low-key point markers mean only the actual line animates.
        for i,(x,y,count) in enumerate(raw):
            r=3 if count>0 else 1.7
            color=C['cyan'] if count>0 else C['blue']
            d.ellipse((x-r,y-r,x+r,y+r),fill=rgba(color,130 if count==0 else 215))
        # progressive line: draw -> hold -> erase; the panel, grid, labels and markers remain static.
        visible_end=0
        for j,n in enumerate(norm):
            if n<=prog: visible_end=j
            else: break
        line_pts=core[:visible_end+1]
        if len(line_pts)>=2:
            glow=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow,'RGBA')
            gd.line(line_pts,fill=rgba(C['cyan'],125),width=10,joint='curve')
            im=Image.alpha_composite(im.convert('RGBA'),glow.filter(ImageFilter.GaussianBlur(5))).convert('RGB')
            d=ImageDraw.Draw(im,'RGBA')
            draw_gradient_line(d,line_pts,gradient_cols,width=3)
            # active traversal point glows at the leading edge while drawing.
            if prog<1 and visible_end<len(core):
                px,py=core[min(visible_end,len(core)-1)]
                pulse=4+1.5*(.5+.5*math.sin(fi*.6))
                d.ellipse((px-pulse-4,py-pulse-4,px+pulse+4,py+pulse+4),fill=rgba(C['cyan'],55))
                d.ellipse((px-pulse,py-pulse,px+pulse,py+pulse),fill=rgba(C['cyan'],255),outline=rgba(C['chartcard'],255),width=2)
        frames.append(im.convert('RGB'))
    return frames

def patch_readme():
    path=ROOT/'README.md'
    if not path.exists():
        print('README.md not found; generated assets only.')
        return
    text=path.read_text(encoding='utf-8'); original=text
    # Touch only the picture block explicitly labelled as the 31-day activity chart.
    matches=list(re.finditer(r'<picture>.*?</picture>',text,flags=re.S|re.I))
    target=None
    for m in matches:
        if 'GitHub activity line chart for the last 31 days' in m.group(0):
            target=m; break
    if target is None:
        print('WARNING: activity chart picture block not found; left README unchanged.')
        return
    block=target.group(0)
    block=block.replace('srcset="./activity-graph.svg"','srcset="./assets/animated/activity-graph-dark.gif"')
    block=block.replace('srcset="./activity-graph-light.svg"','srcset="./assets/animated/activity-graph-light.gif"')
    block=block.replace('src="./activity-graph.svg"','src="./assets/animated/activity-graph-dark.gif"')
    block=block.replace('src="./activity-graph-light.svg"','src="./assets/animated/activity-graph-light.gif"')
    if block != target.group(0):
        backup=ROOT.parent/'README.md.before-leadership-skills-chart-loop-fix.bak'
        if not backup.exists(): backup.write_text(original,encoding='utf-8',newline='\n')
        text=text[:target.start()]+block+text[target.end():]
        path.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')
        print('README: updated only the contribution line-chart picture references.')
    else:
        print('README: activity chart already references the animated GIF assets.')
    # Repoint leadership/skills image blocks only if older non-GIF references are present.
    text=path.read_text(encoding='utf-8'); orig=text
    replacements={
        './assets/leadership-ayuscout.svg':'./assets/animated/leadership-ayuscout-dark.gif',
        './assets/leadership-ayuscout-light.svg':'./assets/animated/leadership-ayuscout-light.gif',
        './assets/skills-grid.svg':'./assets/animated/skills-grid-dark.gif',
        './assets/skills-grid-light.svg':'./assets/animated/skills-grid-light.gif',
    }
    # Each replacement is confined to a picture block carrying the corresponding alt description.
    for marker,pairs in [
        ('Animated AI for Bharat Hackathon leadership showcase', [('./assets/leadership-ayuscout.svg','./assets/animated/leadership-ayuscout-dark.gif'),('./assets/leadership-ayuscout-light.svg','./assets/animated/leadership-ayuscout-light.gif')]),
        ('Technical Skills — six skill domains', [('./assets/skills-grid.svg','./assets/animated/skills-grid-dark.gif'),('./assets/skills-grid-light.svg','./assets/animated/skills-grid-light.gif')]),
    ]:
        for m in list(re.finditer(r'<picture>.*?</picture>',text,flags=re.S|re.I)):
            if marker in m.group(0):
                block=m.group(0)
                for old,new in pairs: block=block.replace(old,new)
                if block!=m.group(0): text=text[:m.start()]+block+text[m.end():]; break
    if text != orig:
        path.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')
        print('README: adjusted only leadership/skills picture references that used old SVG paths.')

def patch_workflow():
    path=ROOT/'.github'/'workflows'/'update-profile-art.yml'
    if not path.exists():
        print('Workflow file not found; GIFs were generated locally only.')
        return
    text=path.read_text(encoding='utf-8'); original=text
    step=("      - name: Generate looping leadership, skills and activity chart GIFs\n"
          "        run: python scripts/generate_profile_animation_assets.py --assets-only\n\n")
    anchor='      - name: Commit refreshed profile visuals'
    if 'scripts/generate_profile_animation_assets.py --assets-only' not in text:
        if anchor in text: text=text.replace(anchor,step+anchor,1)
        else: print('Workflow commit-step anchor not found; skipped workflow insertion.')
    # Ensure scheduled workflow commits generated GIFs in nested assets/animated,
    # retaining the original YAML quote style.
    lines=text.splitlines()
    for i,line in enumerate(lines):
        if re.match(r'^\s*file_pattern\s*:',line):
            m=re.match(r'^(\s*file_pattern:\s*)([\"\'])(.*)\2\s*$',line)
            if m:
                prefix,quote,value=m.group(1),m.group(2),m.group(3)
                if 'assets/animated/*.gif' not in value:
                    lines[i]=prefix+quote+value+' assets/animated/*.gif'+quote
            elif 'assets/animated/*.gif' not in line:
                lines[i]=line.rstrip()+' assets/animated/*.gif'
            break
    text='\n'.join(lines)+'\n'
    # Pillow is installed explicitly in Actions because this script creates GIF frames.
    if 'python -m pip install Pillow' not in text:
        setup_anchor='      - name: Set up Python\n'
        # safer anchor is the final line of Set up Python's uses/with block
        use_match=re.search(r'      - name: Set up Python\n        uses: actions/setup-python@v\d+\n        with:\n          python-version: ["\']?[^\n]+\n',text)
        if use_match:
            insert='\n      - name: Install Pillow for animated profile GIFs\n        run: python -m pip install Pillow\n'
            text=text[:use_match.end()]+insert+text[use_match.end():]
    if text != original:
        path.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')
        print('Workflow: inserted GIF generator and ensured nested GIFs are committed.')
    else:
        print('Workflow already contains the looping-asset generator step.')

def main():
    ANIM.mkdir(parents=True,exist_ok=True)
    # Full design animations are regenerated from deterministic vectors, with the current contribution data only affecting the chart.
    save_loop_gif(draw_leadership(DARK,False),ANIM/'leadership-ayuscout-dark.gif',duration=100)
    save_loop_gif(draw_leadership(LIGHT,True),ANIM/'leadership-ayuscout-light.gif',duration=100)
    save_loop_gif(draw_skills_grid('dark'),ANIM/'skills-grid-dark.gif',duration=100)
    save_loop_gif(draw_skills_grid('light'),ANIM/'skills-grid-light.gif',duration=100)
    records=data_points()
    save_loop_gif(draw_activity_chart('dark',records),ANIM/'activity-graph-dark.gif',duration=100)
    save_loop_gif(draw_activity_chart('light',records),ANIM/'activity-graph-light.gif',duration=100)
    print('Generated six looping GIF assets in assets/animated/.')
    if '--assets-only' not in sys.argv[1:]:
        patch_readme(); patch_workflow()
    print('Done. Existing data/contributions.json and unrelated README sections were preserved.')

if __name__ == '__main__': main()
