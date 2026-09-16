from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.radar.geometry import beam_height_m, gate_geolocation


class GeometryTests(unittest.TestCase):
    def test_beam_altitude_increases_with_range(self):
        self.assertGreater(beam_height_m(50_000, 0.5, 822), beam_height_m(10_000, 0.5, 822))

    def test_northeast_gate_is_northeast_of_radar(self):
        lat, lon, altitude = gate_geolocation(-27.048790, -52.603740, 822, 50_000, 45, 0.5)
        self.assertGreater(lat, -27.048790)
        self.assertGreater(lon, -52.603740)
        self.assertGreater(altitude, 822)
