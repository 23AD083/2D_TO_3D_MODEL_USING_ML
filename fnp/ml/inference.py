import os
from typing import Dict, Any, List, Optional, Tuple

import numpy as np

# Optional imports: OpenCV and ONNX Runtime. Do not fail at import time if unavailable.
try:
    import cv2
    HAS_CV2 = True
except Exception:
    cv2 = None
    HAS_CV2 = False

try:
    import onnxruntime as ort
    HAS_ORT = True
except Exception:
    ort = None
    HAS_ORT = False


def _load_image_bgr(path: str) -> np.ndarray:
    if not HAS_CV2:
        raise ImportError("opencv-python is required to load images but is not installed")
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Failed to load image: {path}")
    return img


def _prepare_input(img: np.ndarray, input_size: int = 1024) -> Tuple[np.ndarray, Dict[str, Any]]:
    h, w = img.shape[:2]
    scale = input_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    pad_top = (input_size - new_h) // 2
    pad_left = (input_size - new_w) // 2
    padded = cv2.copyMakeBorder(
        resized,
        pad_top,
        input_size - new_h - pad_top,
        pad_left,
        input_size - new_w - pad_left,
        cv2.BORDER_CONSTANT,
        value=(255, 255, 255)
    )
    if not HAS_CV2:
        raise ImportError("opencv-python is required for preprocessing but is not installed")
    x = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    x = np.transpose(x, (2, 0, 1))[None, ...]
    meta = {
        "orig_h": h,
        "orig_w": w,
        "pad_top": pad_top,
        "pad_left": pad_left,
        "scale": scale,
        "input_size": input_size
    }
    return x, meta


def _mask_to_polygons(mask: np.ndarray, meta: Dict[str, Any]) -> List[List[List[float]]]:
    if not HAS_CV2:
        return []
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys: List[List[List[float]]] = []
    s = meta["scale"]
    pt = meta["pad_top"]
    pl = meta["pad_left"]
    for c in contours:
        if cv2.contourArea(c) < 200:
            continue
        poly: List[List[float]] = []
        for p in c.reshape(-1, 2):
            x_in = float(p[0])
            y_in = float(p[1])
            x_unpad = x_in - pl
            y_unpad = y_in - pt
            x_orig = x_unpad / s
            y_orig = y_unpad / s
            poly.append([x_orig, y_orig])
        if len(poly) >= 3:
            polys.append(poly)
    return polys


def detect_rooms_and_objects(image_path: str, model_path: Optional[str] = None, task: str = "rooms") -> Dict[str, Any]:
    # If runtime or model missing, or OpenCV unavailable, gracefully return empty ML result.
    if not HAS_ORT or not model_path or not os.path.exists(model_path) or not HAS_CV2:
        return {"rooms": [], "windows": [], "doors": [], "labels": []}

    img = _load_image_bgr(image_path)
    x, meta = _prepare_input(img)

    sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    inp_name = sess.get_inputs()[0].name
    outputs = sess.run(None, {inp_name: x})

    room_mask_logits = outputs[0]
    room_mask = np.squeeze(room_mask_logits)
    if room_mask.ndim == 3:
        room_mask = room_mask[0]
    room_mask = (room_mask > 0.5).astype(np.uint8)

    rooms_px = _mask_to_polygons(room_mask, meta)
    return {"rooms": rooms_px, "windows": [], "doors": [], "labels": []}


