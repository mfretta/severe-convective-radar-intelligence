"""Build display-ready trajectories from real per-timestamp cell products."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
points=[]
for path in sorted((ROOT/'data'/'gold'/'cells').glob('time=*.json')):
    record=json.loads(path.read_text(encoding='utf-8'))
    for cell in record.get('cells',[]):
        if cell.get('track_id'):
            points.append({'track_id':cell['track_id'],'timestamp_token':record['timestamp_token'],'grid_x':cell['centroid_grid_x'],'grid_y':cell['centroid_grid_y'],'max_dbzh':cell['max_dbzh'],'area_km2':cell['area_km2'],'state':cell.get('state','new')})
out=ROOT/'data'/'gold'/'track_geometry.json';out.write_text(json.dumps({'grid_size':241,'points':points},indent=2),encoding='utf-8')
print(f'points={len(points)} tracks={len({p["track_id"] for p in points})}')
