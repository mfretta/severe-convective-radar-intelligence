"""Checkpointed all-timestamp DBZH processing and cell tracking."""
from pathlib import Path
import json
import sys
import xarray as xr
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.pipelines.silver import decode_timestamp
from sc_sentinel.radar.cappi import write_cappi
from sc_sentinel.storms.segmentation import segment_cells
from sc_sentinel.storms.tracking import track_pair
from sc_sentinel.hazards.scoring import score_cell

inventory=json.loads((ROOT/'data'/'metadata'/'radar_inventory.json').read_text(encoding='utf-8'))
times=sorted({r['timestamp_token'] for r in inventory['records']})
out=ROOT/'data'/'gold'/'archive_tracks.json'; state={'processed':[],'skipped':[],'track_points':[]}
if out.exists(): state=json.loads(out.read_text(encoding='utf-8'))
done=set(state['processed'])|{x['timestamp_token'] for x in state['skipped']}
previous=None
for token in times:
    if token in done: continue
    source_files=[r for r in inventory['records'] if r['timestamp_token']==token and r['moment_from_name']=='dBZ']
    if not source_files:
        state['skipped'].append({'timestamp_token':token,'reason':'dBZ native moment unavailable'})
        out.write_text(json.dumps(state,indent=2),encoding='utf-8');continue
    try:
        decode_timestamp(ROOT/'data'/'bronze'/'radar',token,ROOT/'data'/'silver'/'radar',moments={'dBZ'})
        silver=ROOT/'data'/'silver'/'radar'/f'time={token}.zarr';cappi_path=ROOT/'data'/'gold'/'cappi'/f'time={token}'/'height=1000m_dbzh.zarr'
        if not cappi_path.exists():write_cappi(silver,ROOT/'2026-08-30'/f'{token}dBZ.vol',cappi_path)
        cappi=xr.open_zarr(cappi_path);cells=segment_cells(cappi.DBZH.values,cappi.coverage.values,float(cappi.attrs['grid_spacing_m']),40,16)
        current={'timestamp_token':token,'cells':cells}
        assignments=track_pair(previous,current) if previous else track_pair({'timestamp_token':token,'cells':[]},current)
        for cell,assignment in zip(cells,assignments):cell.update(assignment);cell['hazards']=score_cell(cell);state['track_points'].append({'timestamp_token':token,**assignment,'max_dbzh':cell['max_dbzh'],'area_km2':cell['area_km2']})
        cell_out=ROOT/'data'/'gold'/'cells'/f'time={token}.json';cell_out.parent.mkdir(parents=True,exist_ok=True);cell_out.write_text(json.dumps(current,indent=2),encoding='utf-8')
        previous=current;state['processed'].append(token)
    except Exception as exc: state['skipped'].append({'timestamp_token':token,'reason':str(exc)})
    out.write_text(json.dumps(state,indent=2),encoding='utf-8')
print(json.dumps({'processed':len(state['processed']),'skipped':len(state['skipped']),'track_points':len(state['track_points'])}))
