import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Dict, Any

class ImagePreprocessingPipeline:
    """
    Industrial solar inspection image preprocessing pipeline.
    Validates, resizes, denoises, and enhances contrast using CLAHE
    specifically tailored for Photovoltaic (PV) Electroluminescence (EL) and Thermal imaging.
    """
    def __init__(self, target_size: Tuple[int, int] = (512, 512)):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))

    def validate_image_bytes(self, image_bytes: bytes, max_size_mb: float = 15.0) -> Dict[str, Any]:
        """Validates file size, mime suitability, and decodability."""
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            return {"valid": False, "error": f"File size exceeds maximum allowed limit of {max_size_mb} MB (Received {size_mb:.2f} MB)"}
        
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            pil_img.verify()
            pil_img = Image.open(io.BytesIO(image_bytes))  # Reopen after verify
            width, height = pil_img.size
            if width < 32 or height < 32:
                return {"valid": False, "error": f"Image dimensions too small ({width}x{height}). Minimum requirement is 32x32."}
            return {
                "valid": True,
                "format": pil_img.format,
                "width": width,
                "height": height,
                "mode": pil_img.mode,
                "size_mb": round(size_mb, 3)
            }
        except Exception as e:
            return {"valid": False, "error": f"Corrupted or unsupported image file: {str(e)}"}

    def assess_quality(self, image_gray: np.ndarray) -> Dict[str, Any]:
        """Calculates image quality metrics (blurriness variance, contrast RMS, mean brightness)."""
        laplacian_var = cv2.Laplacian(image_gray, cv2.CV_64F).var()
        mean_brightness = float(np.mean(image_gray))
        rms_contrast = float(np.std(image_gray))

        is_blurry = bool(laplacian_var < 80.0)
        is_underexposed = bool(mean_brightness < 30.0)
        is_overexposed = bool(mean_brightness > 225.0)

        quality_score = 100.0
        if is_blurry:
            quality_score -= 25.0
        if is_underexposed or is_overexposed:
            quality_score -= 20.0
        if rms_contrast < 20.0:
            quality_score -= 15.0

        return {
            "blur_laplacian_var": float(round(laplacian_var, 2)),
            "mean_brightness": float(round(mean_brightness, 2)),
            "rms_contrast": float(round(rms_contrast, 2)),
            "is_blurry": is_blurry,
            "is_underexposed": is_underexposed,
            "is_overexposed": is_overexposed,
            "quality_score": float(max(0.0, round(quality_score, 1)))
        }


    def process(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Executes full preprocessing pipeline.
        Returns:
            - original_bgr: numpy array
            - preprocessed_gray: numpy array (CLAHE enhanced + Gaussian denoised)
            - normalized: numpy array [0, 1] float32
            - quality_metrics: dict
        """
        validation = self.validate_image_bytes(image_bytes)
        if not validation["valid"]:
            raise ValueError(validation["error"])

        # Decode image using PIL then convert to OpenCV format
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(pil_img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Resize to standard model input dimensions
        resized_bgr = cv2.resize(img_bgr, self.target_size, interpolation=cv2.INTER_AREA)

        # Convert to Grayscale for EL / Cell inspection
        gray = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2GRAY)

        # Assess original quality
        quality = self.assess_quality(gray)

        # Gaussian Denoising to eliminate sensor noise without distorting micro-cracks
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)

        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        enhanced = self.clahe.apply(denoised)

        # Min-Max Normalization to [0.0, 1.0]
        normalized = enhanced.astype(np.float32) / 255.0

        return {
            "validation": validation,
            "original_bgr": resized_bgr,
            "gray": gray,
            "preprocessed_gray": enhanced,
            "normalized": normalized,
            "quality": quality
        }
