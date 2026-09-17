"""Render a presentation-quality MP4 from actual archived CAPPI and cell products."""
from pathlib import Path
import json, sys, subprocess, hashlib
from datetime import datetime
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.serving.ppi import ensure_cappi_2km
OUT=ROOT/'docs'/'video'; OUT.mkdir(parents=True,exist_ok=True)
FRAMES=OUT/'frames'; FRAMES.mkdir(exist_ok=True)
state=json.loads((ROOT/'data/gold/archive_tracks.json').read_text())
times=[t for t in state['processed'] if '2026083021000000'<=t<='2026083023545999']
points=json.loads((ROOT/'data/gold/track_geometry.json').read_text())['points']
tracks=defaultdict(list)
for p in points: tracks[p['track_id']].append(p)
BG='#07131f'; PANEL='#0e2535'; MUTED='#9cb7c9'; CYAN='#6ce4df'
# Display the central 320 km, equally scaled in x and y. All layers use the
# identical crop of the existing dashboard local Cartesian reference.
X,Y,S=46,151,810
LOW,HIGH=40,200
def pos(x,y): return (X+(x-LOW)/(HIGH-LOW)*S,Y+(HIGH-y)/(HIGH-LOW)*S)
def font(size,bold=False): return ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),size)
def col(v): return '#9b59ff' if v>=65 else '#ed1c24' if v>=55 else '#ff8c00' if v>=45 else '#ffe600'
def stamp(t): return datetime.strptime(t[:14],'%Y%m%d%H%M%S')
base=Image.open(ROOT/'data/serving/santa_catarina_shp_basemap.png').convert('RGB')
base=base.crop((base.width/6,base.height/6,base.width*5/6,base.height*5/6)).resize((S,S),Image.Resampling.LANCZOS)
manifest=[]
for i,t in enumerate(times):
    cells=json.loads((ROOT/'data/gold/cells'/f'time={t}.json').read_text())['cells']
    im=Image.new('RGB',(1920,1080),BG); d=ImageDraw.Draw(im)
    def txt(x,y,st,size=22,color='#edf5fa',bold=False): d.text((x,y),st,font=font(size,bold),fill=color)
    txt(46,27,'SEVERE CONVECTIVE RADAR INTELLIGENCE',34,bold=True)
    txt(46,79,'CHAPECÓ / SANTA CATARINA     •     REAL 2 KM CAPPI DBZH',20,CYAN)
    txt(1390,29,stamp(t).strftime('%H:%M:%S UTC'),38,CYAN,True)
    txt(1390,81,'30 AUG 2026  ·  ARCHIVED REPLAY',18,MUTED)
    im.paste(base,(X,Y))
    radar=Image.open(ensure_cappi_2km(ROOT,t)).convert('RGBA')
    radar=radar.crop((radar.width/6,radar.height/6,radar.width*5/6,radar.height*5/6)).resize((S,S),Image.Resampling.NEAREST)
    im.paste(radar,(X,Y),radar)
    layer=Image.new('RGBA',(S,S)); ld=ImageDraw.Draw(layer)
    def local(x,y):
        px,py=pos(x,y); return (px-X,py-Y)
    active=0
    for c in cells:
        trail=[p for p in tracks.get(c.get('track_id'),[]) if p['timestamp_token']<=t][-12:]
        if len(trail)>1:
            active+=1
            xy=[local(p['grid_x'],p['grid_y']) for p in trail]
            ld.line(xy,fill='#02080e',width=5); ld.line(xy,fill=col(c['max_dbzh']),width=2)
        # Cancel shared edges: render only the measured cell perimeter.
        edges={}
        for x,y in c.get('grid_pixels',[]):
            vertices=[(x-.5,y-.5),(x+.5,y-.5),(x+.5,y+.5),(x-.5,y+.5)]
            for a,b in zip(vertices,vertices[1:]+vertices[:1]):
                key=tuple(sorted((a,b)))
                if key in edges: del edges[key]
                else: edges[key]=(a,b)
        for a,b in edges.values(): ld.line([local(*a),local(*b)],fill=col(c['max_dbzh']),width=2)
    im.paste(layer,(X,Y),layer)
    d=ImageDraw.Draw(im)
    cx,cy=pos(120,120); d.polygon([(cx,cy-9),(cx-8,cy+7),(cx+8,cy+7)],fill='#ffce5b',outline='#000000')
    d.rectangle((X,Y,X+S,Y+S),outline='#355469',width=2)
    txt(64,168,'N ↑',20,CYAN,True)
    txt(64,920,'Local Cartesian view · 320 km extent',16,MUTED)
    d.rounded_rectangle((900,151,1874,367),radius=12,fill=PANEL)
    txt(928,174,'SCAN STATUS',16,CYAN,True)
    for xx,val,label in [(930,len(cells),'DETECTED CELLS'),(1230,active,'ACTIVE TRACKS'),(1530,f'{i+1}/{len(times)}','ARCHIVE FRAME')]:
        txt(xx,217,str(val),49,bold=True); txt(xx,295,label,16,MUTED)
    txt(920,394,'DETECTED CELL INTENSITY',18,CYAN,True)
    bands=[(40,45,'40–<45 dBZ','#ffe600'),(45,55,'45–<55 dBZ','#ff8c00'),(55,65,'55–<65 dBZ','#ed1c24'),(65,999,'≥65 dBZ','#9b59ff')]
    bx=920
    for low,high,label,color in bands:
        if any(low<=c['max_dbzh']<high for c in cells):
            d.rounded_rectangle((bx,437,bx+212,491),radius=5,fill=color)
            txt(bx+12,451,label,21,'#07131f' if low<55 else '#ffffff',True); bx+=232
    txt(920,527,'TRACKED CELLS / TOP 6 BY REFLECTIVITY',18,CYAN,True)
    txt(920,574,'CELL ID',15,MUTED);txt(1420,574,'PEAK DBZH',15,MUTED);txt(1670,574,'AREA',15,MUTED)
    for j,c in enumerate(sorted(cells,key=lambda c:c['max_dbzh'],reverse=True)[:6]):
        yy=615+j*43; d.line((920,yy-11,1850,yy-11),fill='#253f51')
        txt(920,yy,c.get('track_id',str(c['component_id'])),18)
        txt(1420,yy,f"{c['max_dbzh']:.1f} dBZ",21,col(c['max_dbzh']),True)
        txt(1670,yy,f"{c['area_km2']:.0f} km²",20)
    txt(920,906,'Real observations · Recent trajectories · No interpolated scans',18,MUTED)
    txt(920,940,'Analytical replay — not an official meteorological warning',18,MUTED)
    start,end=stamp(times[0]),stamp(times[-1]); progress=(stamp(t)-start).total_seconds()/(end-start).total_seconds()
    d.rounded_rectangle((46,1005,1874,1012),radius=3,fill='#27404d')
    d.rounded_rectangle((46,1005,46+1828*max(progress,.001),1012),radius=3,fill=CYAN)
    txt(46,1031,'21:00 UTC',18,MUTED);txt(1718,1031,'23:54 UTC',18,MUTED)
    path=FRAMES/f'{i:04d}.png'; im.save(path)
    manifest.append({'frame':i,'timestamp':t,'cells':len(cells),'tracks':active,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    print(f'{i+1}/{len(times)} {t}',flush=True)
(OUT/'replay-manifest.json').write_text(json.dumps(manifest,indent=2))
im.save(OUT/'replay-preview.png')
# Encode the requested 1.5x playback: 4/3 second per observation, then final hold.
ffmpeg=next((ROOT/'.video-tools/imageio_ffmpeg/binaries').glob('ffmpeg*.exe'))
video=OUT/'Radar_Replay_2100-2354_UTC.mp4'
command=[str(ffmpeg),'-y','-framerate','3/4','-i',str(FRAMES/'%04d.png'),'-vf','fps=30,tpad=stop_mode=clone:stop_duration=1.333333','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
subprocess.run(command,check=True,stdout=subprocess.DEVNULL)
assert len({f['sha256'] for f in manifest})==len(times)
assert times[0].startswith('202608302100') and times[-1].startswith('202608302354')
subprocess.run([str(ffmpeg),'-v','error','-i',str(video),'-f','null','-'],check=True)
print(json.dumps({'video':str(video),'scans':len(times),'seconds':(len(times)*2+2)/1.5,'speed':1.5,'bytes':video.stat().st_size}),flush=True)
