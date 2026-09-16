from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from sc_sentinel.replay.scheduler import ReplayState
class ReplayTests(unittest.TestCase):
 def test_replay_preserves_source_timestamp_order(self):
  r=ReplayState(['a','b']);r.play();self.assertEqual(r.step(),'b');r.reset();self.assertEqual(r.current(),'a');self.assertFalse(r.playing)
