from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.hazards.warnings import warning_features
class WarningTests(unittest.TestCase):
    def test_medium_hazard_generates_closed_polygon(self):
        cells=[{'component_id':1,'bbox_grid':[0,0,1,1],'hazards':{'heavy_rain':{'level':'MEDIUM'}}}]
        result=warning_features(cells,[0,2000],[0,2000],-27,-52)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['geometry']['coordinates'][0][0],result[0]['geometry']['coordinates'][0][-1])
