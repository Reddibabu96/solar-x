import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestEndToEndPipeline(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_full_inspection_to_maintenance_workflow(self):
        # 1. Trigger Preset Critical Inspection
        res = self.client.post("/api/predict", data={"preset": "critical", "panel_code": "PNL-017"})
        self.assertEqual(res.status_code, 200)
        predict_data = res.json()

        # 2. Verify AI Decision Outputs
        self.assertEqual(predict_data["panel_code"], "PNL-017")
        self.assertIn(predict_data["defect_type"], ["inactive_region", "crack", "hotspot", "micro-crack", "delamination"])

        self.assertLess(predict_data["health_score"], 60.0)
        self.assertIn("P", predict_data["priority_code"])
        self.assertIsNotNone(predict_data["heatmap_b64"])
        self.assertIsNotNone(predict_data["segmentation_b64"])

        # 3. Verify Digital Twin Database Synchronization
        p_res = self.client.get("/api/panels/PNL-017")
        self.assertEqual(p_res.status_code, 200)
        panel_profile = p_res.json()["panel"]
        self.assertEqual(panel_profile["panel_code"], "PNL-017")
        self.assertIn("P", panel_profile["current_priority"])


        # 4. Verify Inspection Report Generation Endpoint
        rep_res = self.client.post("/api/reports/generate", data={"panel_code": "PNL-017"})
        self.assertEqual(rep_res.status_code, 200)
        self.assertIn("SOLARGUARD X", rep_res.text)
        self.assertIn("PNL-017", rep_res.text)
        self.assertIn("P", rep_res.text)


if __name__ == "__main__":
    unittest.main()
