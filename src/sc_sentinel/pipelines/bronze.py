"""Immutable-copy Bronze staging for native radar files."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid

from sc_sentinel.ingestion.rainbow_header import read_rainbow_header


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stage_bronze(source_root: str | Path, bronze_root: str | Path) -> dict:
    """Copy source files once; reject an existing destination with different bytes."""
    source_root, bronze_root = Path(source_root), Path(bronze_root)
    run_id = str(uuid.uuid4())
    records, copied, verified = [], 0, 0
    for source in sorted(source_root.rglob("*.vol")):
        header = read_rainbow_header(source)
        token = header.timestamp_token
        destination = bronze_root / f"year={token[:4]}" / f"month={token[4:6]}" / f"day={token[6:8]}" / f"hour={token[8:10]}" / source.name
        source_hash = _sha256(source)
        if destination.exists():
            if _sha256(destination) != source_hash:
                raise RuntimeError(f"Bronze immutability violation: {destination}")
            verified += 1
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            if _sha256(destination) != source_hash:
                destination.unlink(missing_ok=True)
                raise RuntimeError(f"Checksum mismatch after Bronze copy: {source}")
            copied += 1
        records.append({
            "original_path": str(source.as_posix()),
            "bronze_path": str(destination.as_posix()),
            "timestamp_token": token,
            "moment": header.moment_from_name,
            "file_size_bytes": source.stat().st_size,
            "sha256": source_hash,
            "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
            "ingestion_run_id": run_id,
        })
    manifest = bronze_root.parent / "radar_manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"run_id": run_id, "records": records}, indent=2), encoding="utf-8")
    return {"run_id": run_id, "files": len(records), "copied": copied, "verified_existing": verified, "manifest": str(manifest)}
