from pathlib import Path
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.quality.scan_quality import assess_decoded_volume  # noqa: E402

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else "2026083023540400"
    report = assess_decoded_volume(ROOT / "data" / "silver" / "radar" / f"time={token}.zarr")
    target = ROOT / "data" / "quality" / "2026-08-30" / f"decoded_{token}.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"variables={len(report['results'])} warnings={sum(row['status'] == 'WARN' for row in report['results'])}")
