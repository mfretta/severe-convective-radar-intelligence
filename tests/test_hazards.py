from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.hazards.scoring import score_cell
class HazardTests(unittest.TestCase):
    def test_missing_velocity_is_not_presented_as_rotation(self):
        result=score_cell({'max_dbzh':60,'area_km2':100})
        self.assertEqual(result['rotation']['level'],'NOT_ASSESSED')
        self.assertLessEqual(result['hail']['score'],.35)
