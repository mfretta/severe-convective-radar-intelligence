"""Header-level quality checks that require no inferred radar parameters."""
from __future__ import annotations

from pathlib import Path
import json

from sc_sentinel.ingestion.file_inventory import build_inventory


def assess_archive(source_root: str | Path) -> dict:
    inventory = build_inventory(source_root)
    expected_sweeps = None
    rows = []
    seen = set()
    for record in inventory["records"]:
        sweeps = len(record["elevations_deg"])
        expected_sweeps = expected_sweeps or sweeps
        flags = []
        if sweeps != expected_sweeps:
            flags.append("inconsistent_sweep_count")
        if record["range_step_km"] is None or record["range_step_km"] <= 0:
            flags.append("invalid_range_step")
        if record["latitude_deg"] is None or record["longitude_deg"] is None:
            flags.append("missing_site_geolocation")
        if any(r != 360 for r in record["azimuth_counts"]):
            flags.append("nonstandard_azimuth_count")
        key = (record["timestamp_token"], record["moment_from_name"])
        if key in seen:
            flags.append("duplicate_timestamp_moment")
        seen.add(key)
        rows.append({"timestamp_token": record["timestamp_token"], "moment": record["moment_from_name"], "status": "PASS" if not flags else "WARN", "flags": flags})
    return {"file_count": inventory["file_count"], "failed_headers": inventory["failed_file_count"], "expected_sweep_count": expected_sweeps, "rows": rows}


def write_quality_report(source_root: str | Path, output: str | Path) -> dict:
    result = assess_archive(source_root)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


RADAR_VARIABLES = {"DBZH", "DBTH", "ZDR", "KDP", "RHOHV", "PHIDP", "VRADH", "WRADH", "uPhiDP"}


def assess_decoded_volume(zarr_path: str | Path) -> dict:
    """Evaluate actual decoded gate ranges without discarding scientific data."""
    import numpy as np
    import xarray as xr

    zarr_path = Path(zarr_path)
    manifest = json.loads((zarr_path / "sc_sentinel_manifest.json").read_text(encoding="utf-8"))
    results = []
    for group in manifest["groups"]:
        dataset = xr.open_zarr(zarr_path, group=group)
        for name in sorted(set(dataset.data_vars) & RADAR_VARIABLES):
            values = np.asarray(dataset[name].values, dtype=float)
            finite = values[np.isfinite(values)]
            flags = []
            if not finite.size:
                flags.append("no_finite_gates")
            elif name == "RHOHV" and (finite.min() < -0.05 or finite.max() > 1.05):
                flags.append("rhohv_outside_physical_tolerance")
            results.append({"group": group, "variable": name, "finite_gate_count": int(finite.size), "min": float(finite.min()) if finite.size else None, "max": float(finite.max()) if finite.size else None, "status": "WARN" if flags else "PASS", "flags": flags})
    return {"zarr_path": str(zarr_path.as_posix()), "results": results}
