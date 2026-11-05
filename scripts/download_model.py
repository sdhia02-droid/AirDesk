"""Download Google's official MediaPipe hand landmarker model."""
from pathlib import Path
from urllib.request import urlretrieve

URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
TARGET = Path(__file__).resolve().parents[1] / "assets" / "hand_landmarker.task"
if __name__ == "__main__":
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        print(f"Already present: {TARGET}")
    else:
        print("Downloading official MediaPipe model...")
        urlretrieve(URL, TARGET)
        print(f"Saved {TARGET} ({TARGET.stat().st_size:,} bytes)")
