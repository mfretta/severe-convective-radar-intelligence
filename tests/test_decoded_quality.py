from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@unittest.skipUnless((ROOT / "data" / "silver" / "radar" / "time=2026083023540400.zarr" / "sc_sentinel_manifest.json").exists(), "full decoded scan unavailable")
class DecodedQualityTests(unittest.TestCase):
    def test_real_full_volume_has_expected_moments_and_physical_rhohv(self):
        from sc_sentinel.quality.scan_quality import assess_decoded_volume
        report = assess_decoded_volume(ROOT / "data" / "silver" / "radar" / "time=2026083023540400.zarr")
        variables = {row["variable"] for row in report["results"]}
        self.assertTrue({"DBZH", "ZDR", "KDP", "RHOHV", "VRADH"}.issubset(variables))
        self.assertFalse(any("rhohv_outside_physical_tolerance" in row["flags"] for row in report["results"]))
