"""Create a provenance-preserving inventory from real Rainbow headers."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .rainbow_header import NAME_PATTERN, RainbowHeaderError, read_rainbow_header


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_inventory(source: str | Path, include_checksums: bool = False) -> dict:
    source = Path(source)
    files = sorted([p for p in source.rglob("*") if p.is_file() and p.suffix.lower() == ".vol"])
    records, failures = [], []
    for path in files:
        try:
            header = read_rainbow_header(path)
            record = asdict(header)
            record["path"] = str(path.as_posix())
            record["file_size_bytes"] = path.stat().st_size
            if include_checksums:
                record["sha256"] = _sha256(path)
            records.append(record)
        except RainbowHeaderError as exc:
            failures.append({"path": str(path.as_posix()), "error": str(exc)})
    timestamps = sorted({record["timestamp_token"] for record in records})
    moments = Counter(record["moment_from_name"] for record in records)
    representative = []
    if timestamps:
        for stamp in (timestamps[0], timestamps[(len(timestamps) - 1) // 2], timestamps[-1]):
            representative.extend(record for record in records if record["timestamp_token"] == stamp)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source.resolve().as_posix()),
        "file_count": len(files),
        "decoded_file_count": len(records),
        "failed_file_count": len(failures),
        "timestamp_count": len(timestamps),
        "first_timestamp_token": timestamps[0] if timestamps else None,
        "last_timestamp_token": timestamps[-1] if timestamps else None,
        "moments_by_filename": dict(sorted(moments.items())),
        "representative_headers": representative,
        "records": records,
        "failures": failures,
    }


def write_inventory(source: str | Path, output: str | Path, include_checksums: bool = False) -> dict:
    inventory = build_inventory(source, include_checksums=include_checksums)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory, indent=2, sort_keys=True), encoding="utf-8")
    return inventory
