from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.pipelines.silver import decode_timestamp  # noqa: E402

if __name__ == "__main__":
    timestamp = sys.argv[1] if len(sys.argv) > 1 else "2026083000420400"
    result = decode_timestamp(ROOT / "data" / "bronze" / "radar", timestamp, ROOT / "data" / "silver" / "radar")
    print(f"status={result['status']} sweeps={result['sweep_count']} groups={len(result['groups'])}")
