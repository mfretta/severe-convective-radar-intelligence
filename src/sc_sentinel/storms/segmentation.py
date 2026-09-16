"""Configurable reflectivity segmentation on coverage-aware CAPPI grids."""
from __future__ import annotations
import numpy as np


def segment_cells(dbzh: np.ndarray, coverage: np.ndarray, spacing_m: float, threshold_dbzh: float, minimum_area_km2: float) -> list[dict]:
    from scipy import ndimage
    candidate = np.asarray(coverage, dtype=bool) & np.isfinite(dbzh) & (dbzh >= threshold_dbzh)
    labels, count = ndimage.label(candidate, structure=np.ones((3, 3), dtype=int))
    cells = []
    for label in range(1, count + 1):
        mask = labels == label
        pixels = int(mask.sum())
        area_km2 = pixels * spacing_m**2 / 1_000_000
        if area_km2 < minimum_area_km2:
            continue
        y, x = np.where(mask)
        # Keep the actual connected CAPPI pixels.  This enables serving the
        # observed cell footprint, rather than a centroid circle or bbox.
        pixels_grid = [[int(px), int(py)] for py, px in zip(y, x)]
        cells.append({"component_id": len(cells) + 1, "pixel_count": pixels, "area_km2": area_km2, "max_dbzh": float(np.nanmax(dbzh[mask])), "mean_dbzh": float(np.nanmean(dbzh[mask])), "centroid_grid_y": float(y.mean()), "centroid_grid_x": float(x.mean()), "bbox_grid": [int(x.min()), int(y.min()), int(x.max()), int(y.max())], "grid_pixels": pixels_grid})
    return cells
