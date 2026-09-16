from pathlib import Path
import json
import sys
import xarray as xr
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.hazards.warnings import warning_features  # noqa: E402
from sc_sentinel.ingestion.rainbow_header import read_rainbow_header  # noqa: E402
if __name__ == "__main__":
    token=sys.argv[1] if len(sys.argv)>1 else "2026083023540400"
    cells=json.loads((ROOT/'data'/'gold'/'cells'/f'time={token}.json').read_text(encoding='utf-8'))['cells']
    for cell in cells: cell['timestamp_token']=token
    cappi=xr.open_zarr(ROOT/'data'/'gold'/'cappi'/f'time={token}'/'height=1000m_dbzh.zarr')
    header=read_rainbow_header(ROOT/'2026-08-30'/f'{token}dBZ.vol')
    collection={"type":"FeatureCollection","features":warning_features(cells,cappi.easting_m.values,cappi.northing_m.values,header.latitude_deg,header.longitude_deg)}
    output=ROOT/'data'/'gold'/'warnings'/f'time={token}.geojson';output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(collection,indent=2),encoding='utf-8')
    print(f"warnings={len(collection['features'])}")
