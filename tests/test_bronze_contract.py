from pathlib import Path
import sys
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.pipelines.bronze import stage_bronze


@unittest.skipUnless((ROOT / "2026-08-30").exists(), "real Rainbow archive not available")
class BronzeContractTests(unittest.TestCase):
    def test_restage_is_idempotent(self):
        sample = next((ROOT / "2026-08-30").glob("*KDP.vol"))
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            source.mkdir()
            shutil.copy2(sample, source / sample.name)
            target = Path(temp) / "bronze" / "radar"
            first = stage_bronze(source, target)
            second = stage_bronze(source, target)
            self.assertEqual(first["files"], second["files"])
            self.assertEqual(second["copied"], 0)
            self.assertEqual(second["verified_existing"], second["files"])
