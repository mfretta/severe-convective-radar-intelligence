"""Generate the real-file Rainbow metadata inventory."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.ingestion.file_inventory import write_inventory  # noqa: E402


if __name__ == "__main__":
    archive = ROOT / "2026-08-30"
    result = write_inventory(archive, ROOT / "data" / "metadata" / "radar_inventory.json")
    print(f"files={result['file_count']} decoded={result['decoded_file_count']} failures={result['failed_file_count']}")
    print(f"timestamps={result['timestamp_count']} moments={', '.join(result['moments_by_filename'])}")
