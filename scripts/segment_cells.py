from pathlib import Path
import json
import sys
import xarray as xr
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.storms.segmentation import segment_cells  # noqa: E402
if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else "2026083023540400"
    p = ROOT / "data" / "gold" / "cappi" / f"time={token}" / "height=1000m_dbzh.zarr"
    d = xr.open_zarr(p)
    cells = segment_cells(d.DBZH.values, d.coverage.values, float(d.attrs['grid_spacing_m']), 40.0, 16.0)
    output = ROOT / "data" / "gold" / "cells" / f"time={token}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"timestamp_token": token, "method": "reflectivity_CAPPI_configurable", "cells": cells}, indent=2), encoding="utf-8")
    print(f"cells={len(cells)}")
