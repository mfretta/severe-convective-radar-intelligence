"""Render a real lowest-elevation DBZH PPI for the browser from Silver Zarr."""
from pathlib import Path
import sys
import numpy as np
import xarray as xr
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import image as mpl_image

ROOT=Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    token=sys.argv[1] if len(sys.argv)>1 else '2026083023540400'
    source=ROOT/'data'/'silver'/'radar'/f'time={token}.zarr'
    ds=xr.open_zarr(source,group='sweep_0/dBZ')
    dbzh=ds.DBZH.values; az=ds.azimuth.values; ranges=ds.range.values
    extent=float(ranges.max()); axis=np.linspace(-extent,extent,800); east,north=np.meshgrid(axis,axis)
    bearing=(np.degrees(np.arctan2(east,north))+360)%360; distance=np.hypot(east,north)
    # Native rays/ranges are regular (360 rays, 250 m gates); use direct
    # nearest-index arithmetic rather than allocating a 800×800×960 array.
    ai=np.mod(np.rint((bearing-float(az[0]))/(360/len(az))).astype(int),len(az))
    ri=np.clip(np.rint((distance-float(ranges[0]))/float(np.median(np.diff(ranges)))).astype(int),0,len(ranges)-1)
    grid=dbzh[ai,ri].astype(float); grid[distance>ranges.max()]=np.nan; grid[grid<-10]=np.nan
    colors=['#102a59','#1767aa','#16a6dc','#2dd45a','#e8e334','#f3a126','#e94d37','#bd2458','#ffffff']
    cmap=LinearSegmentedColormap.from_list('radar',colors); cmap.set_bad((0.02,0.07,0.12,1))
    rgba=cmap(np.clip((grid-0)/70,0,1)); out=ROOT/'data'/'serving';out.mkdir(parents=True,exist_ok=True)
    mpl_image.imsave(out/f'ppi_dbzh_{token}.png',rgba,origin='lower')
    (out/f'ppi_dbzh_{token}.json').write_text(__import__('json').dumps({'timestamp_token':token,'field':'DBZH','sweep':0,'elevation_deg':float(ds.sweep_fixed_angle.values),'range_km':extent/1000,'projection':'radar-centric east/north Cartesian nearest-gate PPI','source':'real Rainbow dBZ volume'},indent=2),encoding='utf-8')
    print(out/f'ppi_dbzh_{token}.png')
