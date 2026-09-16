"""Full-domain lowest-elevation real DBZH PPI grid for cell objects."""
from pathlib import Path
import numpy as np
import xarray as xr

def dbzh_ppi_grid(zarr_path: str|Path, grid_size: int=241):
    ds=xr.open_zarr(zarr_path,group='sweep_0/dBZ')
    field,az,ranges=ds.DBZH.values,ds.azimuth.values,ds.range.values
    extent=float(ranges.max());axis=np.linspace(-extent,extent,grid_size);east,north=np.meshgrid(axis,axis);bearing=(np.degrees(np.arctan2(east,north))+360)%360;distance=np.hypot(east,north)
    ai=np.mod(np.rint((bearing-float(az[0]))/(360/len(az))).astype(int),len(az));ri=np.clip(np.rint((distance-float(ranges[0]))/float(np.median(np.diff(ranges)))).astype(int),0,len(ranges)-1)
    values=field[ai,ri].astype(float);coverage=distance<=ranges.max();values[~coverage]=np.nan;values[values<-10]=np.nan
    return values,coverage,axis
