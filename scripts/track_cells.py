from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.storms.tracking import track_pair  # noqa: E402

if __name__ == "__main__":
    previous_token, current_token = (sys.argv[1:3] if len(sys.argv) >= 3 else ("2026083023480400", "2026083023540400"))
    base = ROOT / "data" / "gold" / "cells"
    previous = json.loads((base / f"time={previous_token}.json").read_text(encoding="utf-8"))
    current = json.loads((base / f"time={current_token}.json").read_text(encoding="utf-8"))
    assignments = track_pair(previous, current)
    by_component = {item["component_id"]: item for item in assignments}
    for cell in current["cells"]:
        cell.update(by_component[cell["component_id"]])
    current["tracking"] = {"previous_timestamp_token": previous_token, "method": "hungarian_distance_intensity", "assignments": assignments}
    output = base / f"time={current_token}.json"
    output.write_text(json.dumps(current, indent=2), encoding="utf-8")
    tracks = ROOT / "data" / "gold" / "storm_tracks.json"
    tracks.write_text(json.dumps({"latest_timestamp_token": current_token, "assignments": assignments}, indent=2), encoding="utf-8")
    print(f"matched={sum(a['state'] == 'matched' for a in assignments)} new={sum(a['state'] == 'new' for a in assignments)}")
