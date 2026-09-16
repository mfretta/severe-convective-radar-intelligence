from pathlib import Path
import json
import numpy as np
import xarray as xr
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
from matplotlib import image as mpl_image

def ensure_ppi(root: Path, token: str) -> Path:
    output=root/'data'/'serving'/f'ppi_dbzh_{token}.png'
    if output.exists(): return output
    ds=xr.open_zarr(root/'data'/'silver'/'radar'/f'time={token}.zarr',group='sweep_0/dBZ')
    dbzh,az,ranges=ds.DBZH.values,ds.azimuth.values,ds.range.values
    extent=float(ranges.max());axis=np.linspace(-extent,extent,800);east,north=np.meshgrid(axis,axis);bearing=(np.degrees(np.arctan2(east,north))+360)%360;distance=np.hypot(east,north)
    ai=np.mod(np.rint((bearing-float(az[0]))/(360/len(az))).astype(int),len(az));ri=np.clip(np.rint((distance-float(ranges[0]))/float(np.median(np.diff(ranges)))).astype(int),0,len(ranges)-1)
    grid=dbzh[ai,ri].astype(float);grid[distance>ranges.max()]=np.nan;grid[grid<5]=np.nan
    cmap=LinearSegmentedColormap.from_list('radar',['#1767aa','#16a6dc','#2dd45a','#e8e334','#f3a126','#e94d37','#bd2458','#ffffff']);cmap.set_bad((0,0,0,0))
    output.parent.mkdir(parents=True,exist_ok=True);mpl_image.imsave(output,cmap(np.clip(grid/70,0,1)),origin='lower')
    return output

def ensure_cappi_2km(root: Path, token: str) -> Path:
    """Render the real 2 km ASL DBZH CAPPI used by segmentation and tracking.

    Unlike ``ensure_ppi``, this is not a lowest-sweep display product: every
    pixel comes from the coverage-aware CAPPI cube generated for this timestamp.
    """
    # Versioned name prevents an earlier continuous-colour cache from being
    # served after the operational cell-threshold palette changes.
    output = root / 'data' / 'serving' / f'cappi_2km_display_v4_{token}.png'
    if output.exists():
        return output
    source = root / 'data' / 'gold' / 'cappi' / f'time={token}' / 'height=2000m_dbzh.zarr'
    if not source.exists():
        raise FileNotFoundError(source)
    ds = xr.open_zarr(source)
    grid = ds.DBZH.values.astype(float)
    coverage = ds.coverage.values.astype(bool)
    # Preserve all valid meteorological echoes in the CAPPI.  The 40/45/55 dBZ
    # bands are for cell classification, not a filter that hides weaker echoes.
    grid[(~coverage) | (grid < 5)] = np.nan
    cmap = ListedColormap(['#1677d2', '#14b8a6', '#42c95a', '#ffe600', '#ff8c00', '#ed1c24', '#9b59ff'])
    cmap.set_bad((0, 0, 0, 0))
    norm = BoundaryNorm([5, 20, 30, 40, 45, 55, 65, np.inf], cmap.N)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Preserve NaNs as masked values; passing plain NaNs through BoundaryNorm
    # can otherwise map them to the final (red) colour bin.
    masked = np.ma.masked_invalid(grid)
    mpl_image.imsave(output, cmap(norm(masked)), origin='lower')
    return output
