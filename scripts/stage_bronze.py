from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.pipelines.bronze import stage_bronze  # noqa: E402

if __name__ == "__main__":
    result = stage_bronze(ROOT / "2026-08-30", ROOT / "data" / "bronze" / "radar")
    print(result)
