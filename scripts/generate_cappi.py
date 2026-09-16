from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.radar.cappi import write_cappi  # noqa: E402
if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else "2026083023540400"
    source = ROOT / "data" / "silver" / "radar" / f"time={token}.zarr"
    header = ROOT / "2026-08-30" / f"{token}dBZ.vol"
    result = write_cappi(source, header, ROOT / "data" / "gold" / "cappi" / f"time={token}" / "height=1000m_dbzh.zarr")
    print(result)
