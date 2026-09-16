"""Coverage-aware constant-altitude plan-position indicator generation."""
from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import xarray as xr

from .geometry import beam_height_m
from sc_sentinel.ingestion.rainbow_header import read_rainbow_header


FIELD_MAP = {"dBZ": "DBZH", "dBuZ": "DBTH", "V": "VRADH", "W": "WRADH", "RhoHV": "RHOHV", "PhiDP": "PHIDP", "KDP": "KDP", "ZDR": "ZDR"}


def generate_cappi(zarr_path: str | Path, header_path: str | Path, variable: str = "dBZ", height_m: float = 1000, grid_spacing_m: float = 2000, max_height_difference_m: float = 750) -> xr.Dataset:
    """Nearest-beam CAPPI with explicit coverage rather than extrapolation."""
    zarr_path = Path(zarr_path)
    header = read_rainbow_header(header_path)
    field = FIELD_MAP[variable]
    max_range = max(header.bin_counts) * header.range_step_km * 1000
    axis = np.arange(-max_range, max_range + grid_spacing_m, grid_spacing_m)
    east, north = np.meshgrid(axis, axis)
    horizontal_range = np.hypot(east, north)
    bearing = (np.degrees(np.arctan2(east, north)) + 360) % 360
    selected = np.full(east.shape, -1, dtype=np.int16)
    separation = np.full(east.shape, np.inf)
    for sweep, elevation in enumerate(header.elevations_deg):
        beam = np.vectorize(beam_height_m)(horizontal_range, elevation, header.altitude_m or 0.0)
        difference = np.abs(beam - height_m)
        update = difference < separation
        selected[update] = sweep
        separation[update] = difference[update]
    values = np.full(east.shape, np.nan, dtype=np.float32)
    for sweep in range(len(header.elevations_deg)):
        group = f"sweep_{sweep}/{variable}"
        try:
            source = xr.open_zarr(zarr_path, group=group)[field].values
        except (KeyError, FileNotFoundError):
            continue
        source_azimuth = xr.open_zarr(zarr_path, group=group).azimuth.values
        source_range = xr.open_zarr(zarr_path, group=group).range.values
        mask = (selected == sweep) & (separation <= max_height_difference_m) & (horizontal_range <= source_range.max())
        az_idx = np.abs(((bearing[..., None] - source_azimuth + 180) % 360) - 180).argmin(axis=-1)
        range_idx = np.abs(horizontal_range[..., None] - source_range).argmin(axis=-1)
        values[mask] = source[az_idx[mask], range_idx[mask]]
    coverage = np.isfinite(values)
    return xr.Dataset(
        {field: (("northing_m", "easting_m"), values), "coverage": (("northing_m", "easting_m"), coverage), "contributing_sweep": (("northing_m", "easting_m"), selected)},
        coords={"northing_m": axis, "easting_m": axis},
        attrs={"height_m_asl": height_m, "grid_spacing_m": grid_spacing_m, "maximum_beam_height_difference_m": max_height_difference_m, "method": "nearest_valid_beam", "source_zarr": str(zarr_path.as_posix())},
    )


def write_cappi(zarr_path: str | Path, header_path: str | Path, output: str | Path, **kwargs) -> dict:
    dataset = generate_cappi(zarr_path, header_path, **kwargs)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_zarr(output, mode="w", zarr_format=3)
    meta = {"coverage_fraction": float(dataset.coverage.values.mean()), **dataset.attrs}
    (output / "sc_sentinel_cappi.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta
