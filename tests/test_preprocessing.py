import unittest
import numpy as np
import cv2

from ml.preprocessing.pipeline import ImagePreprocessingPipeline

class TestImagePreprocessing(unittest.TestCase):
    def setUp(self):
        self.pipeline = ImagePreprocessingPipeline(target_size=(512, 512))
        # Generate dummy 512x512 synthetic BGR test image
        self.dummy_img = np.full((512, 512, 3), 150, dtype=np.uint8)
        _, buffer = cv2.imencode(".png", self.dummy_img)
        self.dummy_bytes = buffer.tobytes()

    def test_validation(self):
        res = self.pipeline.validate_image_bytes(self.dummy_bytes)
        self.assertTrue(res["valid"])
        self.assertEqual(res["width"], 512)
        self.assertEqual(res["height"], 512)

    def test_processing_pipeline(self):
        res = self.pipeline.process(self.dummy_bytes)
        self.assertIn("original_bgr", res)
        self.assertIn("preprocessed_gray", res)
        self.assertIn("quality", res)
        self.assertEqual(res["preprocessed_gray"].shape, (512, 512))
        self.assertGreaterEqual(res["quality"]["quality_score"], 0.0)

if __name__ == "__main__":
    unittest.main()
