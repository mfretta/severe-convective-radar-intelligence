from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
class ApiTests(unittest.TestCase):
    def test_health_contract(self):
        try:
            from fastapi.testclient import TestClient
            from backend.app.main import app
        except ImportError as exc:
            self.skipTest(str(exc))
        response=TestClient(app).get('/health')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['status'],'ok')

    def test_real_volume_and_replay_routes(self):
        from fastapi.testclient import TestClient
        from backend.app.main import app
        client=TestClient(app)
        self.assertEqual(client.get('/api/volume/2026083023540400').status_code,200)
        self.assertEqual(client.get('/api/replay/status').json()['mode'],'archived')
        archive=client.get('/api/archive/tracks')
        self.assertEqual(archive.status_code,200)
        self.assertGreater(len(archive.json()['track_points']),0)
