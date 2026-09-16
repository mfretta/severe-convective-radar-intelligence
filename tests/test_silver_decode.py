from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@unittest.skipUnless((ROOT / "data" / "bronze" / "radar").exists(), "Bronze data not staged")
class SilverDecodeTests(unittest.TestCase):
    def test_real_kdp_volume_decodes_to_sweep_aware_zarr(self):
        from sc_sentinel.pipelines.silver import decode_timestamp
        with tempfile.TemporaryDirectory() as temp:
            result = decode_timestamp(ROOT / "data" / "bronze" / "radar", "2026083000420400", Path(temp))
            self.assertEqual(result["status"], "decoded")
            self.assertEqual(result["sweep_count"], 14)
            self.assertIn("sweep_0/KDP", result["groups"])
