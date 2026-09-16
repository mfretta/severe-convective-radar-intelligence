from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.quality.scan_quality import write_quality_report  # noqa: E402

if __name__ == "__main__":
    result = write_quality_report(ROOT / "2026-08-30", ROOT / "data" / "quality" / "2026-08-30" / "scan_quality.json")
    warnings = sum(row["status"] == "WARN" for row in result["rows"])
    print(f"files={result['file_count']} header_failures={result['failed_headers']} warnings={warnings}")
