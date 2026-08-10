import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")

    def test_dashboard_summary(self):
        res = self.client.get("/api/dashboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_panels"], 100)
        self.assertIn("average_health", data)

    def test_get_panels(self):
        res = self.client.get("/api/panels")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 100)

    def test_demo_presets(self):
        res = self.client.get("/api/demo-presets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["presets"]), 4)

    def test_preset_predict(self):
        res = self.client.post("/api/predict", data={"preset": "hotspot", "panel_code": "PNL-017"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["panel_code"], "PNL-017")
        self.assertIn("health_score", data)
        self.assertIn("contribution_breakdown", data)
        self.assertIn("heatmap_b64", data)

if __name__ == "__main__":
    unittest.main()
