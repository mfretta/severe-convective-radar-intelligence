from pathlib import Path
import sys
import unittest
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sc_sentinel.storms.segmentation import segment_cells
class SegmentationTests(unittest.TestCase):
    def test_threshold_and_minimum_area_are_respected(self):
        d = np.zeros((5, 5)); d[1:3, 1:3] = 45
        cells = segment_cells(d, np.ones_like(d, dtype=bool), 2000, 40, 10)
        self.assertEqual(len(cells), 1)
        self.assertEqual(cells[0]['area_km2'], 16)
