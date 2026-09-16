from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

@unittest.skipUnless((ROOT / "data" / "silver" / "radar" / "time=2026083023540400.zarr" / "sc_sentinel_manifest.json").exists(), "full decoded scan unavailable")
class CappiTests(unittest.TestCase):
    def test_real_cappi_has_coverage_and_declared_height(self):
        from sc_sentinel.radar.cappi import generate_cappi
        d = generate_cappi(ROOT / "data" / "silver" / "radar" / "time=2026083023540400.zarr", ROOT / "2026-08-30" / "2026083023540400dBZ.vol", grid_spacing_m=10_000)
        self.assertEqual(d.attrs["height_m_asl"], 1000)
        self.assertGreater(float(d.coverage.mean()), 0)
