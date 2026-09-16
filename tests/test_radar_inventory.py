from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sc_sentinel.ingestion.file_inventory import build_inventory
from sc_sentinel.ingestion.rainbow_header import read_rainbow_header


ARCHIVE = ROOT / "2026-08-30"


@unittest.skipUnless(ARCHIVE.exists(), "real Rainbow archive not available")
class RadarInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = build_inventory(ARCHIVE)

    def test_every_file_has_a_parseable_xml_header(self):
        self.assertGreater(self.inventory["file_count"], 0)
        self.assertEqual(self.inventory["failed_file_count"], 0, self.inventory["failures"][:3])

    def test_archive_has_multiple_times_and_expected_native_moments(self):
        self.assertGreater(self.inventory["timestamp_count"], 2)
        self.assertIn("KDP", self.inventory["moments_by_filename"])
        self.assertIn("V", self.inventory["moments_by_filename"])

    def test_representative_header_has_real_geometry(self):
        header = read_rainbow_header(ARCHIVE / "2026083000420400KDP.vol")
        self.assertEqual(header.native_moment, "KDP")
        self.assertGreaterEqual(len(header.elevations_deg), 1)
        self.assertIsNotNone(header.latitude_deg)
        self.assertIsNotNone(header.longitude_deg)
        self.assertIsNotNone(header.range_step_km)
