# AIRDESK — Touchless Studio

A real-time webcam-powered creative workspace built with **OpenCV**, **MediaPipe Tasks**, and Python. Pinch to draw, erase or drag floating notes. Features a neon HUD, gesture hysteresis, landmark smoothing, snapshots, and automated unit tests.

> **Status:** v1.0 source release. Core logic has automated tests; webcam and UI require local hardware verification.

## Features

- Single-hand landmark tracking (21 landmarks) with Google's MediaPipe Hand Landmarker
- Scale-normalized pinch gesture with hysteresis and two-frame dwell
- Smoothed index-finger pointer
- Freehand air drawing, erase by proximity, undo, clear
- Drag floating note cards in Move mode
- Four drawing colors and on-screen HUD
- Mirrored webcam feed, skeleton toggle, screenshot export
- Safe cleanup on exit and useful startup errors

## Requirements

Python **3.11–3.13** recommended, a webcam, and internet access **once** to download the official model. Windows, macOS and Linux supported where MediaPipe wheels and a webcam are available.

## Installation

```bash
git clone https://github.com/sdhia02-droid/AirDesk.git
cd AirDesk
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

Install and download model:

```bash
python -m pip install -r requirements.txt
python scripts/download_model.py
python main.py
```

If the camera isn't index 0: `python main.py --camera 1`.

## Controls

| Key | Action |
| --- | --- |
| 1 | Draw mode: pinch and move to draw |
| 2 | Move mode: pinch a note and drag |
| 3 | Erase mode: pinch near a stroke |
| C | Cycle pen colors |
| U | Undo last stroke |
| X | Clear strokes |
| S | Save screenshot to `exports/` |
| H | Toggle hand skeleton |
| Q / Esc | Quit |

Pinch = touch thumb tip to index tip and hold for approximately two frames. Release to end the action. Gestures only act below the top toolbar and above the bottom status bar. Move mode only drags cards.

## How it works

```text
Webcam → mirror → BGR-to-RGB → MediaPipe Hand Landmarker (VIDEO)
       → 21 normalized landmarks → pixel coordinates
       → normalized pinch ratio → hysteresis + dwell → gesture events
       → workspace state machine → OpenCV HUD → display
```

The pinch distance is divided by palm width, helping gestures work at different distances from the camera. Separate thresholds for starting and ending a pinch reduce flicker. The pointer uses exponential smoothing. The gesture engine and workspace are pure Python, so they can be tested without a webcam.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Project structure

```text
AirDesk/
  airdesk/
    geometry.py    # Pure geometry
    gestures.py    # Gesture state machine
    workspace.py   # Canvas and notes state
    tracker.py     # MediaPipe adapter
    render.py      # OpenCV HUD
  scripts/download_model.py
  tests/test_core.py
  main.py
  requirements.txt
  requirements-dev.txt
```

## Limitations and roadmap

- Current version uses one hand; multi-hand gestures are future work.
- Card dragging and drawing require pinching. Keyboard chooses modes to avoid unreliable accidental mode changes.
- Drawing colors are selected globally at render time; changing the color recolors earlier strokes. Per-stroke colors are a planned improvement.
- Eraser removes an entire stroke when any sampled point is close to the cursor, rather than cutting a segment.
- Webcam quality, lighting, and hand occlusion affect tracking.
- MediaPipe model is downloaded separately and is not committed to Git.

Next steps: per-stroke colors, gesture-controlled toolbar, customizable gestures, resize handles, export canvas without camera background, benchmarks, CI and release demo.

## Privacy

Camera frames are processed locally. No video is uploaded by this application. Images are only saved when you press `S`.

## License

MIT. See `LICENSE`.