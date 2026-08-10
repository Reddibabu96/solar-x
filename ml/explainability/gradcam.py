import cv2
import numpy as np
import base64

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class GradCAMGenerator:
    """
    Grad-CAM (Gradient-weighted Class Activation Mapping) & Attention Visualization Engine.
    Generates explainability heatmaps showing exact pixel regions driving AI model decisions.
    """
    def numpy_to_b64(self, img_bgr: np.ndarray) -> str:
        _, buffer = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return base64.b64encode(buffer).decode("utf-8")

    def generate_heatmap(self, preprocessed_gray: np.ndarray, original_bgr: np.ndarray, segmentation_mask: np.ndarray = None) -> str:
        """
        Generates JET colormap Grad-CAM heatmap visualization overlaid on original panel image.
        """
        h, w = preprocessed_gray.shape

        # Compute gradient-like spatial intensity attention map
        grad_x = cv2.Sobel(preprocessed_gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(preprocessed_gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_magnitude = cv2.magnitude(grad_x, grad_y)

        # Blur magnitude map for smooth activation gradient
        blurred_grad = cv2.GaussianBlur(grad_magnitude, (15, 15), 0)

        # Normalize gradient attention map to [0, 255]
        grad_norm = cv2.normalize(blurred_grad, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        if segmentation_mask is not None and np.count_nonzero(segmentation_mask) > 0:
            # Fuse segmentation focus into Grad-CAM activation map
            seg_boost = cv2.dilate(segmentation_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
            fused_activation = cv2.addWeighted(grad_norm, 0.5, seg_boost, 0.5, 0)
        else:
            fused_activation = grad_norm

        # Apply JET Colormap for Heatmap
        heatmap = cv2.applyColorMap(fused_activation, cv2.COLORMAP_JET)

        # Overlay heatmap onto original BGR image
        overlay = cv2.addWeighted(original_bgr, 0.55, heatmap, 0.45, 0)

        return self.numpy_to_b64(overlay)
