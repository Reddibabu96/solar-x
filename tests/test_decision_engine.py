import unittest
from ml.inference.decision_engine import SolarDecisionEngine

class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SolarDecisionEngine()

    def test_healthy_evaluation(self):
        detection = {
            "defect_type": "healthy",
            "display_name": "Healthy Panel",
            "confidence": 0.98,
            "affected_area_pct": 0.0,
            "defect_count": 0
        }
        res = self.engine.evaluate(detection)
        self.assertGreaterEqual(res["health_score"], 90.0)
        self.assertEqual(res["priority_code"], "P4 — LOW")
        self.assertIn("optimal", res["ai_summary"])

    def test_critical_hotspot_evaluation(self):
        detection = {
            "defect_type": "inactive_region",
            "display_name": "Inactive Cell Sub-Region",
            "confidence": 0.95,
            "affected_area_pct": 22.5,
            "defect_count": 3
        }
        res = self.engine.evaluate(detection)
        self.assertLess(res["health_score"], 40.0)
        self.assertGreaterEqual(res["risk_score"], 70.0)
        self.assertIn("P1", res["priority_code"])
        self.assertIn("severity_contribution", res["contribution_breakdown"])
        self.assertIn("what_is_damaged", res)
        self.assertIn("remediation_method", res)



if __name__ == "__main__":
    unittest.main()
