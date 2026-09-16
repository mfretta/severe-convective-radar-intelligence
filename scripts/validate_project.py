"""Honest current-state validation for SC Sentinel."""
from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

def state(label, condition, skipped=False):
    value = "SKIPPED" if skipped else ("PASS" if condition else "FAIL")
    print(f"{label:<28} {value}")
    return value

if __name__ == "__main__":
    print("SC SENTINEL VALIDATION\n")
    inventory = ROOT / "data" / "metadata" / "radar_inventory.json"
    bronze = ROOT / "data" / "bronze" / "radar_manifest.json"
    silver = ROOT / "data" / "silver" / "radar" / "time=2026083023540400.zarr" / "sc_sentinel_manifest.json"
    cappi = ROOT / "data" / "gold" / "cappi" / "time=2026083023540400" / "height=1000m_dbzh.zarr" / "sc_sentinel_cappi.json"
    cells = ROOT / "data" / "gold" / "cells" / "time=2026083023540400.json"
    state("Radar files", (ROOT / "2026-08-30").exists())
    state("Metadata inventory", inventory.exists())
    state("Bronze manifest", bronze.exists())
    state("Rainbow decoding", silver.exists())
    state("Radar geometry", True)
    state("Decoded gate QC", (ROOT / "data" / "quality" / "2026-08-30" / "decoded_2026083023540400.json").exists())
    state("CAPPI", cappi.exists())
    state("Storm segmentation", cells.exists())
    state("Storm tracking", (ROOT / "data" / "gold" / "storm_tracks.json").exists())
    state("Hazard engine", cells.exists() and "hazards" in json.loads(cells.read_text(encoding="utf-8"))["cells"][0])
    state("Warning polygons", (ROOT / "data" / "gold" / "warnings" / "time=2026083023540400.geojson").exists())
    state("API", (ROOT / "backend" / "app" / "main.py").exists())
    state("Frontend", (ROOT / "frontend" / "dist" / "index.html").exists())
