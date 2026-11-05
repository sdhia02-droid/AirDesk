"""MediaPipe Tasks adapter. Download model using scripts/download_model.py."""
from __future__ import annotations
from pathlib import Path
from .geometry import Point

class HandTracker:
    def __init__(self, model_path: str):
        import mediapipe as mp
        self.mp = mp
        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f"Model not found: {path}. Run python scripts/download_model.py")
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(path)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=1, min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55, min_tracking_confidence=0.5)
        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.last_timestamp = -1

    def detect(self, rgb_frame, timestamp_ms: int) -> list[Point] | None:
        timestamp_ms = max(timestamp_ms, self.last_timestamp + 1)
        self.last_timestamp = timestamp_ms
        image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.detector.detect_for_video(image, timestamp_ms)
        if not result.hand_landmarks:
            return None
        return [Point(lm.x, lm.y) for lm in result.hand_landmarks[0]]

    def close(self) -> None:
        self.detector.close()
