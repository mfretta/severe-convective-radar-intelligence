"""Add exact 2 km CAPPI component footprints to existing real cell products."""
from pathlib import Path
import json
import xarray as xr
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from sc_sentinel.storms.segmentation import segment_cells

updated = 0
for path in sorted((ROOT / 'data' / 'gold' / 'cells').glob('time=*.json')):
    token = path.stem.removeprefix('time=')
    cappi = ROOT / 'data' / 'gold' / 'cappi' / f'time={token}' / 'height=2000m_dbzh.zarr'
    if not cappi.exists():
        continue
    current = json.loads(path.read_text(encoding='utf-8'))
    data = xr.open_zarr(cappi)
    rebuilt = segment_cells(data.DBZH.values, data.coverage.values, float(data.attrs['grid_spacing_m']), 40, 16)
    by_id = {cell['component_id']: cell for cell in rebuilt}
    for cell in current.get('cells', []):
        if cell['component_id'] in by_id:
            cell['grid_pixels'] = by_id[cell['component_id']]['grid_pixels']
    path.write_text(json.dumps(current, indent=2), encoding='utf-8')
    updated += 1
print(json.dumps({'updated': updated}))
