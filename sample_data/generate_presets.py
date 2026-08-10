import cv2
import numpy as np
import os

PRESET_DIR = os.path.dirname(os.path.abspath(__file__))

def create_base_solar_panel(width=512, height=512):
    """Creates a base Photovoltaic (PV) Electroluminescence (EL) panel image."""
    img = np.full((height, width), 160, dtype=np.uint8)
    
    # Add subtle background noise (sensor grain)
    noise = np.random.normal(0, 5, (height, width)).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Draw solar cell grid lines (6x6 cells)
    cell_w = width // 6
    cell_h = height // 6

    # Busbars (silver conductor lines)
    cv2.line(img, (width // 3, 0), (width // 3, height), 220, 3)
    cv2.line(img, (2 * width // 3, 0), (2 * width // 3, height), 220, 3)

    # Cell grid borders
    for r in range(1, 6):
        cv2.line(img, (0, r * cell_h), (width, r * cell_h), 60, 2)
    for c in range(1, 6):
        cv2.line(img, (c * cell_w, 0), (c * cell_w, height), 60, 2)

    # Solar cell texture / fingers
    for r in range(6):
        for finger_y in range(r * cell_h + 5, (r + 1) * cell_h, 8):
            cv2.line(img, (0, finger_y), (width, finger_y), 175, 1)

    return img

def generate_presets():
    os.makedirs(PRESET_DIR, exist_ok=True)

    # 1. Preset Healthy
    healthy_img = create_base_solar_panel()
    cv2.imwrite(os.path.join(PRESET_DIR, "preset_healthy.png"), healthy_img)

    # 2. Preset Micro-crack
    microcrack_img = create_base_solar_panel()
    # Draw micro-crack jagged lines
    pts = np.array([[120, 140], [150, 170], [190, 160], [240, 210], [280, 200]], np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(microcrack_img, [pts], False, 30, 2)
    
    pts2 = np.array([[310, 320], [350, 340], [380, 390]], np.int32)
    pts2 = pts2.reshape((-1, 1, 2))
    cv2.polylines(microcrack_img, [pts2], False, 35, 2)
    cv2.imwrite(os.path.join(PRESET_DIR, "preset_microcrack.png"), microcrack_img)

    # 3. Preset Hotspot (Thermal EL)
    hotspot_img = create_base_solar_panel()
    # Draw intense bright thermal hotspot
    cv2.circle(hotspot_img, (320, 240), 45, 255, -1)
    cv2.circle(hotspot_img, (320, 240), 65, 235, -1)
    cv2.GaussianBlur(hotspot_img, (15, 15), 0, dst=hotspot_img)
    cv2.imwrite(os.path.join(PRESET_DIR, "preset_hotspot.png"), hotspot_img)

    # 4. Preset Critical Multi-Defect
    critical_img = create_base_solar_panel()
    # Large inactive cell region (dark block)
    cell_w = 512 // 6
    cell_h = 512 // 6
    cv2.rectangle(critical_img, (1 * cell_w + 5, 2 * cell_h + 5), (3 * cell_w - 5, 4 * cell_h - 5), 25, -1)
    
    # Severe crack across adjacent cell
    pts_crit = np.array([[260, 100], [320, 180], [390, 250], [450, 310]], np.int32)
    cv2.polylines(critical_img, [pts_crit.reshape((-1, 1, 2))], False, 15, 4)
    cv2.imwrite(os.path.join(PRESET_DIR, "preset_critical.png"), critical_img)

    print("Successfully generated 4 demo preset images in:", PRESET_DIR)

if __name__ == "__main__":
    generate_presets()
