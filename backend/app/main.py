"""SC Sentinel serving API for derived, real radar products."""
from pathlib import Path
import json
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
app = FastAPI(title="SC SENTINEL", version="0.1.0", description="Non-official severe convective radar analytical guidance")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.mount('/products', StaticFiles(directory=ROOT / 'data' / 'serving'), name='products')

def read_json(path: Path):
    if not path.exists(): raise HTTPException(404, "Requested derived product is not available")
    return json.loads(path.read_text(encoding="utf-8"))

@app.get('/health')
def health(): return {'status':'ok','project':'SC SENTINEL'}

@app.get('/api/scans')
def scans():
    # Replay only scans that have a decoded 2 km CAPPI cell product.  This keeps
    # a missing native dBZ file from leaving the previous image on screen.
    archive = ROOT / 'data' / 'gold' / 'archive_tracks.json'
    if archive.exists():
        state = read_json(archive)
        processed = state.get('processed', [])
        if processed:
            return {'timestamps': processed, 'excluded_scans': len(state.get('skipped', []))}
    d=read_json(ROOT/'data'/'metadata'/'radar_inventory.json')
    return {'timestamps':sorted({r['timestamp_token'] for r in d['records']}), 'excluded_scans': 0}

@app.get('/api/map/countries')
def countries_map():
    return FileResponse(ROOT / 'data' / 'serving' / 'countries.geojson', media_type='application/geo+json')

@app.get('/api/map/municipalities')
def municipalities_map():
    return FileResponse(ROOT / 'data' / 'serving' / 'santa_catarina_municipios.geojson', media_type='application/geo+json')

@app.get('/api/cells/{timestamp}')
def cells(timestamp: str): return read_json(ROOT/'data'/'gold'/'cells'/f'time={timestamp}.json')

@app.get('/api/warnings/{timestamp}')
def warnings(timestamp: str): return read_json(ROOT/'data'/'gold'/'warnings'/f'time={timestamp}.geojson')

@app.get('/api/radar/info')
def radar_info():
    d=read_json(ROOT/'data'/'metadata'/'radar_inventory.json')
    return d['representative_headers'][0]

@app.get('/api/cappi/{timestamp}/{height}')
def cappi(timestamp: str, height: str):
    path=ROOT/'data'/'gold'/'cappi'/f'time={timestamp}'/f'height={height}_dbzh.zarr'/'sc_sentinel_cappi.json'
    return read_json(path)

@app.get('/api/volume/{timestamp}')
def volume(timestamp: str):
    return read_json(ROOT/'data'/'silver'/'radar'/f'time={timestamp}.zarr'/'sc_sentinel_manifest.json')

@app.get('/api/cells/{cell_id}/track')
def track(cell_id: str):
    data=read_json(ROOT/'data'/'gold'/'storm_tracks.json')
    return {'cell_id':cell_id,'points':[p for p in data['assignments'] if p['track_id']==cell_id]}

@app.get('/api/replay/status')
def replay_status():
    return {'mode':'archived','timestamp_token':'2026083023540400','playing':False,'speed':1,'note':'Simulation time is separate from native source timestamps.'}

@app.get('/api/archive/progress')
def archive_progress():
    path=ROOT/'data'/'gold'/'archive_tracks.json'
    if not path.exists(): return {'status':'not_started','processed':0,'skipped':0,'track_points':0}
    state=read_json(path)
    inventory=read_json(ROOT/'data'/'metadata'/'radar_inventory.json')
    total=len({record['timestamp_token'] for record in inventory['records']})
    complete=len(state['processed'])+len(state['skipped'])==total
    return {'status':'complete' if complete else 'running_or_checkpointed','total_timestamps':total,'processed':len(state['processed']),'skipped':len(state['skipped']),'track_points':len(state['track_points']),'last_processed':state['processed'][-1] if state['processed'] else None}

@app.get('/api/archive/tracks')
def archive_tracks():
    state=read_json(ROOT/'data'/'gold'/'archive_tracks.json')
    return {'track_points':state['track_points'],'processed_timestamps':state['processed'],'data_gaps':state['skipped']}

@app.get('/api/archive/track-geometry')
def track_geometry():
    return read_json(ROOT/'data'/'gold'/'track_geometry.json')

@app.get('/api/ppi/{timestamp}')
def ppi(timestamp: str):
    try:
        from sc_sentinel.serving.ppi import ensure_ppi
        return FileResponse(ensure_ppi(ROOT,timestamp), media_type='image/png')
    except (FileNotFoundError, KeyError):
        raise HTTPException(404,'Real DBZH PPI is unavailable for this timestamp')

@app.get('/api/cappi-image/{timestamp}')
def cappi_image(timestamp: str):
    try:
        from sc_sentinel.serving.ppi import ensure_cappi_2km
        return FileResponse(ensure_cappi_2km(ROOT, timestamp), media_type='image/png')
    except (FileNotFoundError, KeyError):
        raise HTTPException(404, 'Real 2 km DBZH CAPPI is unavailable for this timestamp')
