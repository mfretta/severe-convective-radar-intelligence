from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.storms.tracking import track_pair
class TrackingTests(unittest.TestCase):
    def test_nearby_cell_is_matched_and_distant_cell_is_new(self):
        old={"timestamp_token":"2026083023480400","cells":[{"component_id":1,"centroid_grid_x":1,"centroid_grid_y":1,"max_dbzh":50}]}
        new={"timestamp_token":"2026083023540400","cells":[{"component_id":1,"centroid_grid_x":2,"centroid_grid_y":1,"max_dbzh":51},{"component_id":2,"centroid_grid_x":100,"centroid_grid_y":100,"max_dbzh":45}]}
        result=track_pair(old,new)
        self.assertEqual(result[0]["state"],"matched")
        self.assertEqual(result[1]["state"],"new")
