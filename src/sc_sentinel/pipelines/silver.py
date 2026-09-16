"""Decode native Rainbow moment volumes into sweep-aware Zarr groups."""
from __future__ import annotations

from pathlib import Path
import json
import shutil

from sc_sentinel.ingestion.rainbow_header import NAME_PATTERN, read_rainbow_header


def decode_timestamp(source_root: str | Path, timestamp_token: str, output_root: str | Path, moments: set[str] | None = None) -> dict:
    """Decode each available native moment/sweep for one real timestamp.

    Groups are deliberately ragged by sweep because the source has different
    range-bin counts aloft. No interpolation or resampling occurs in Silver.
    """
    try:
        import xradar as xd
    except ImportError as exc:
        raise RuntimeError("xradar is required; install the radar extra") from exc
    source_root, output_root = Path(source_root), Path(output_root)
    sources = []
    for path in source_root.rglob("*.vol"):
        match = NAME_PATTERN.match(path.name)
        if match and match.group("stamp") == timestamp_token:
            sources.append(path)
    if moments is not None:
        sources = [path for path in sources if (match := NAME_PATTERN.match(path.name)) and match.group("moment") in moments]
    if not sources:
        raise FileNotFoundError(f"No requested native moments for timestamp {timestamp_token}")
    if not sources:
        raise FileNotFoundError(f"No native files for timestamp {timestamp_token}")
    destination = output_root / f"time={timestamp_token}.zarr"
    if destination.exists():
        # Idempotency: metadata records whether this exact timestamp was decoded.
        marker = destination / "sc_sentinel_manifest.json"
        if marker.exists():
            return json.loads(marker.read_text(encoding="utf-8"))
        raise RuntimeError(f"Existing Silver target lacks SC Sentinel manifest: {destination}")
    staging = output_root / f".time={timestamp_token}.staging.zarr"
    if staging.exists():
        shutil.rmtree(staging)
    staging.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for path in sorted(sources):
        header = read_rainbow_header(path)
        # xradar's Rainbow backend presently accepts a path string, not Path.
        tree = xd.io.open_rainbow_datatree(str(path), optional_groups=True)
        for sweep in range(len(header.elevations_deg)):
            dataset = tree[f"sweep_{sweep}"].to_dataset().load()
            dataset.attrs.update({
                "sc_sentinel_source_file": str(path.as_posix()),
                "sc_sentinel_native_moment": header.native_moment or header.moment_from_name,
                "sc_sentinel_timestamp_token": timestamp_token,
                "sc_sentinel_nyquist_velocity_ms": header.nyquist_velocity_ms[sweep] if sweep < len(header.nyquist_velocity_ms) else None,
            })
            group = f"sweep_{sweep}/{header.moment_from_name}"
            dataset.to_zarr(staging, group=group, mode="a", zarr_format=3)
            written.append(group)
    result = {
        "timestamp_token": timestamp_token,
        "source_files": [str(path.as_posix()) for path in sorted(sources)],
        "groups": written,
        "sweep_count": len(read_rainbow_header(sources[0]).elevations_deg),
        "status": "decoded",
    }
    (staging / "sc_sentinel_manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    staging.replace(destination)
    return result
