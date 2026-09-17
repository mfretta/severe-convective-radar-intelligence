"""Build the project presentation and a matching layout contact sheet.

Install python-pptx in .presentation-tools or in the active Python environment.
"""
from pathlib import Path
import sys, json
ROOT = Path(__file__).resolve().parents[1]
from PIL import Image, ImageDraw, ImageFont

OUT = ROOT / 'docs' / 'presentation'
OUT.mkdir(exist_ok=True)
ASSETS = ROOT / 'docs' / 'assets'
slides = []
BG, PANEL, WHITE, MUTED, CYAN = '07131F', '102536', 'F1F6FA', 'A0B8C9', '52D9EE'
SCALE = 100
previews, notes = [], []
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('arialbd.ttf' if bold else 'arial.ttf'), round(size * SCALE / 72))
def rect(x,y,w,h,color=PANEL,stroke=None):
    s['items'].append(dict(kind='rect',x=x,y=y,w=w,h=h,color=color))
    draw.rectangle((x*SCALE,y*SCALE,(x+w)*SCALE,(y+h)*SCALE),fill='#'+color)
def text(t,x,y,w,h,size=22,color=WHITE,bold=False):
    s['items'].append(dict(kind='text',text=t,x=x,y=y,w=w,h=h,size=size,color=color,bold=bold))
    yy=y*SCALE; f=font(size,bold)
    for line in t.split('\n'):
        words=line.split(); row=''
        for word in words:
            proposed=(row+' '+word).strip()
            if draw.textlength(proposed,font=f)>w*SCALE and row:
                draw.text((x*SCALE,yy),row,font=f,fill='#'+color); yy+=size*SCALE/72*1.2; row=word
            else: row=proposed
        draw.text((x*SCALE,yy),row,font=f,fill='#'+color); yy+=size*SCALE/72*1.2+5*SCALE/72
def pic(name,x,y,w,h):
    path=ASSETS/name
    im=Image.open(path).convert('RGB'); iw,ih=im.size; ratio=min(w/iw,h/ih)
    ww,hh=iw*ratio,ih*ratio; xx,yy=x+(w-ww)/2,y+(h-hh)/2
    s['items'].append(dict(kind='image',path=str(path),x=xx,y=yy,w=ww,h=hh))
    canvas.paste(im.resize((round(ww*SCALE),round(hh*SCALE))), (round(xx*SCALE),round(yy*SCALE)))
def slide(kicker,title,subtitle=None):
    global s,canvas,draw
    s={'items':[]}; slides.append(s)
    canvas=Image.new('RGB',(1600,900),'#'+BG); draw=ImageDraw.Draw(canvas)
    rect(.65,.55,.42,.055,CYAN); text(kicker.upper(),1.22,.43,13,.35,12,CYAN,True)
    text(title,.65,1.05,14.7,1.1,34,WHITE,True)
    if subtitle: text(subtitle,.65,2.02,14.7,.7,18,MUTED)
    rect(.65,8.43,14.7,.015,'254354')
    text('SEVERE CONVECTIVE RADAR INTELLIGENCE  /  ENGINEERING CASE STUDY',.65,8.58,13,.25,9,MUTED)
    text(f'{len(slides):02d} / 08',14.6,8.55,.8,.3,11,CYAN,True)
def finish(note):
    s['notes']=note
    notes.append(note); previews.append(canvas)
def card(x,y,w,h,label,body,accent=CYAN):
    rect(x,y,w,h); rect(x,y,.045,h,accent)
    text(label,x+.25,y+.24,w-.5,.65,23,accent,True)
    text(body,x+.25,y+1.02,w-.5,h-1.15,19)

state=json.loads((ROOT/'data/gold/archive_tracks.json').read_text(encoding='utf-8'))
processed, skipped, points=len(state['processed']),len(state['skipped']),len(state['track_points'])

slide('01 / The project','Severe Convective\nRadar Intelligence')
text('From native radar volumes\nto traceable storm-cell intelligence.',.68,3.1,6.0,1.55,26,CYAN)
text('Chapecó · Santa Catarina · Brazil\nArchived observations: 30 August 2026',.68,5.12,5.85,1.2,20,MUTED)
text('Murilo Fretta',.68,7.2,5,.5,22,WHITE,True)
pic('Platform2.png',6.8,2.75,8.55,4.6)
finish('Introduce the project as an engineering case study using real archived weather-radar observations. The interface replays historical timestamps; it is not a live operational warning service. Explain the goal: turn complex sensor files into inspectable cells and trajectories with traceable processing.')

slide('02 / Why this is a data engineering problem','One radar. Many dimensions.','Every derived storm object starts with a correctly interpreted observation.')
for x,n,l in [(.65,'2,045','Native Rainbow .vol files'),(5.63,'233','Timestamp groups'),(10.61,'14','Elevation slices')]:
    rect(x,2.95,4.72,1.6); text(n,x+.25,3.1,4.2,.7,40,CYAN,True); text(l,x+.25,3.95,4.2,.4,17,MUTED)
card(.65,4.95,7.1,2.85,'DECODE THE OBSERVATION','Read actual fields, scaling, timestamps,\nrange and elevation metadata.')
card(8.02,4.95,7.31,2.85,'PRESERVE THE CONTEXT','Keep source files, missing values and\ncoverage explicit through processing.')
finish('The archive contains separate moment volumes, rather than one tidy table per scan. Available moments include reflectivity, differential reflectivity, native KDP, correlation coefficient, differential phase, velocity and spectrum width. Field availability does not imply every moment contributes to the current tracking algorithm. The current cell path uses DBZH.')

slide('03 / Architecture','A medallion pipeline with traceable outputs')
pic('severe-convective-radar-intelligence-architecture.png',1.8,2.12,12.4,5.97)
finish('Walk from left to right: preserve Rainbow source files in Bronze; decode sweep-aware Zarr groups and check quality; derive coverage-aware 2 km CAPPI, cells and tracks in Gold; serve products with FastAPI and the React dashboard. The illustration is conceptual: CAPPI products are stored under Gold in the current repository. Hazard scores and analytical polygons are heuristic products. The current dashboard is a 2D image and SVG view, not a validated 3D product.')

slide('04 / Data quality','Trust is built at every transformation.','Validation covers the file, the measurement and the derived product.')
for x,label,body in [(.65,'01  SOURCE','Preserve originals\nSHA-256 checksums\nMetadata inventory'),(5.63,'02  SCIENCE','Dimensions and units\nCoverage masks\nGeometry checks'),(10.61,'03  DELIVERY','Timestamp alignment\nExplicit missing scans\nTraceable outputs')]:
    card(x,3.0,4.72,3.35,label,body)
rect(.65,6.78,14.68,1.05,'143443')
text('A successful pipeline run is only useful when its outputs are credible.',.95,7.05,14,.55,23,CYAN,True)
finish('Explain the difference between software validity and scientific validity. Parsing successfully does not guarantee correct geometry, units or coverage. Preserve gaps and exclusions rather than implying complete observations. These are implemented controls and checks, not a claim of comprehensive clutter removal, attenuation correction or independently verified forecast skill.')

slide('05 / Detection and tracking','From reflectivity pixels to persistent cells','Cell boundaries come from connected CAPPI pixels; tracks associate objects between scans.')
card(.65,3,4.72,3.2,'DETECT','2 km altitude CAPPI (ASL)\nDBZH ≥40 dBZ\nMinimum area: 16 km²')
card(5.63,3,4.72,3.2,'ASSOCIATE','Hungarian assignment\nSpeed gate: ≤150 km/h\nPeak DBZH change: ≤25 dBZ')
card(10.61,3,4.72,3.2,'DISPLAY','Cell perimeter + trajectory\nActive cells in each scan\nRecent history: 12 points')
colors=[('FFE600','40–<45 dBZ'),('FF8C00','45–<55 dBZ'),('ED1C24','55–<65 dBZ'),('9B59FF','≥65 dBZ')]
for i,(col,label) in enumerate(colors):
    x=.65+i*3.72; rect(x,6.62,3.49,.65,col); text(label,x+.18,6.75,3.15,.4,20,'07131F' if i<2 else WHITE,True)
text('Reflectivity classes describe intensity; they do not confirm hail or tornadoes.',.65,7.57,14,.42,17,MUTED)
finish('The altitude is 2 km above sea level, while the Cartesian grid spacing is also 2 km. Four connected grid pixels meet the 16 km² minimum area. Connectivity includes diagonals. Association uses actual elapsed time between scans. Current limitations include simple one-to-one association and no mature split/merge model. The tail is capped at 12 points, which is not exactly one hour because archive cadence and gaps vary. The side legend classifies detected cells by peak DBZH; weaker echoes remain visible in the raster.')

slide('06 / The interface','Inspect the storm, its shape and its history.')
pic('Platform2.png',.65,2.05,14.7,5.92)
finish('Use this screenshot to walk through the actual interface: supplied municipal and country boundaries, the real 2 km CAPPI, outlined cell footprints and trajectories, the scan-specific side legend, and the cell table. Replay changes presentation timing while retaining observation timestamps. The screenshot includes heuristic heavy-rain and hail fields and rotation marked NOT_ASSESSED. Explain that display projection and physical validation remain improvement areas.')

slide('07 / Archive results','A complete run makes coverage visible.','Recorded processing outcome for the supplied historical archive.')
for x,n,l in [(.65,str(processed),'Processed timestamps'),(5.63,str(skipped),'Excluded timestamps'),(10.61,f'{points:,}','Tracked-cell observations')]:
    rect(x,2.95,4.72,1.58); text(n,x+.25,3.1,4.2,.72,40,CYAN,True); text(l,x+.25,3.95,4.2,.38,17,MUTED)
pic('Platform.png',.65,4.92,7.4,2.96)
text('What the numbers mean',8.5,5.0,6.5,.6,25,WHITE,True)
text('Processing coverage, not detection accuracy.\nTrack points are cell observations,\nnot distinct storms or verified impacts.',8.5,5.85,6.45,1.6,21,MUTED)
finish(f'The local archive checkpoint reports {processed} processed timestamps, {skipped} exclusions and {points} track-point records. These measure engineering throughput and available products, not recall, false-alarm rate or confirmed storm severity. Review exclusion reasons in the archive manifest. Independent event truth and quantitative skill evaluation remain future work.')

slide('08 / Lessons and next steps','Data quality makes the result explainable.','The strongest outcome is a traceable path from source observation to visual evidence.')
card(.65,3.0,7.1,3.6,'WHAT I LEARNED','Metadata are part of the measurement.\nRaw files must remain recoverable.\nMissing coverage must stay visible.\nEvery visual needs a traceable source.')
card(8.02,3.0,7.31,3.6,'WHAT COMES NEXT','Validate projection and cell matching.\nEvaluate velocity and rotation safely.\nCompare against independent events.\nMeasure quality and performance.')
text('Explore the code and architecture',.65,7.12,14,.45,21,CYAN,True)
url='https://github.com/mfretta/severe-convective-radar-intelligence'
text(url,.65,7.65,14,.45,17,MUTED)
s['items'][-1]['hyperlink']=url
finish('Close by connecting the work to data engineering: provenance, reproducible processing, explicit quality and understandable outputs. The project is an analytical prototype based on archived data. Rain and hail scores are heuristic; rotation is not assessed. Invite questions about design decisions and point to the GitHub repository. Suggested presentation length: eight to ten minutes.')

target=OUT/'Severe_Convective_Radar_Intelligence.pptx'
(OUT/'slides.json').write_text(json.dumps(slides),encoding='utf-8')
# Layout proof uses the same positions, font sizes and assets as the slide builder.
sheet=Image.new('RGB',(1600,1800),'#0B1723')
for i,im in enumerate(previews):
    im.save(OUT/f'slide-{i+1:02d}.png')
    sheet.paste(im.resize((800,450)),((i%2)*800,(i//2)*450))
sheet.save(OUT/'presentation-overview.jpg',quality=92)
(OUT/'speaker-notes.md').write_text('\n\n'.join(f'## Slide {i+1}\n\n{n}' for i,n in enumerate(notes)),encoding='utf-8')
assert len(slides)==8
print(json.dumps({'slides':len(slides),'processed':processed,'excluded':skipped,'track_points':points}))
