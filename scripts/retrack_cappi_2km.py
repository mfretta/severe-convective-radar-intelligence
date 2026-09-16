"""Rebuild all cell tracks from the coverage-aware 2 km DBZH CAPPI."""
from pathlib import Path
import json,sys
import xarray as xr
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.radar.cappi import write_cappi
from sc_sentinel.storms.segmentation import segment_cells
from sc_sentinel.storms.tracking import track_pair
from sc_sentinel.hazards.scoring import score_cell

inventory=json.loads((ROOT/'data'/'metadata'/'radar_inventory.json').read_text(encoding='utf-8'));times=sorted({r['timestamp_token'] for r in inventory['records']});previous=None;state={'processed':[],'skipped':[],'track_points':[],'segmentation_source':'coverage-aware 2 km ASL DBZH CAPPI'}
for token in times:
    zarr=ROOT/'data'/'silver'/'radar'/f'time={token}.zarr';header=ROOT/'2026-08-30'/f'{token}dBZ.vol';product=ROOT/'data'/'gold'/'cappi'/f'time={token}'/'height=2000m_dbzh.zarr'
    if not zarr.exists() or not header.exists():state['skipped'].append({'timestamp_token':token,'reason':'No decoded dBZ Silver product'});continue
    try:
        if not product.exists():write_cappi(zarr,header,product,height_m=2000)
        cappi=xr.open_zarr(product);cells=segment_cells(cappi.DBZH.values,cappi.coverage.values,float(cappi.attrs['grid_spacing_m']),40,16);current={'timestamp_token':token,'segmentation_source':'coverage-aware 2 km ASL DBZH CAPPI','cells':cells};assign=track_pair(previous,current) if previous else track_pair({'timestamp_token':token,'cells':[]},current)
        for cell,a in zip(cells,assign):cell.update(a);cell['hazards']=score_cell(cell);state['track_points'].append({'timestamp_token':token,**a,'max_dbzh':cell['max_dbzh'],'area_km2':cell['area_km2']})
        (ROOT/'data'/'gold'/'cells'/f'time={token}.json').write_text(json.dumps(current,indent=2),encoding='utf-8');state['processed'].append(token);previous=current
    except Exception as exc:state['skipped'].append({'timestamp_token':token,'reason':str(exc)})
    (ROOT/'data'/'gold'/'archive_tracks.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
(ROOT/'data'/'gold'/'archive_tracks.json').write_text(json.dumps(state,indent=2),encoding='utf-8');print(json.dumps({'processed':len(state['processed']),'skipped':len(state['skipped']),'points':len(state['track_points'])}))
