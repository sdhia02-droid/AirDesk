"""AirDesk application entry point."""
from __future__ import annotations
import argparse
import time
from datetime import datetime
from pathlib import Path
import cv2
from airdesk.geometry import Point
from airdesk.gestures import GestureEngine
from airdesk.workspace import Workspace, PALETTE
from airdesk.render import render
from airdesk.tracker import HandTracker

ROOT = Path(__file__).resolve().parent

def main() -> int:
    parser = argparse.ArgumentParser(description="AirDesk - touchless computer vision studio")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--model", default=str(ROOT / "assets" / "hand_landmarker.task"))
    args = parser.parse_args()
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"Cannot open camera {args.camera}; check permissions or try --camera 1")
        return 1
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,args.height)
    tracker = None
    try:
        tracker = HandTracker(args.model)
        engine = GestureEngine()
        workspace = None
        show_skeleton = True
        previous = time.perf_counter()
        start = previous
        missing_frames = 0
        while True:
            ok,frame=cap.read()
            if not ok:
                print("Camera stream ended")
                break
            frame=cv2.flip(frame,1)
            h,w=frame.shape[:2]
            if workspace is None:
                workspace=Workspace(w,h)
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            landmarks=tracker.detect(rgb,int((time.perf_counter()-start)*1000))
            gesture=None
            if landmarks:
                missing_frames=0
                pixel_points=[Point(p.x*w,p.y*h) for p in landmarks]
                gesture=engine.update(pixel_points)
                # Exclude toolbar from drawing / erasing and avoid unwanted strokes.
                if gesture.pointer.y>82 and gesture.pointer.y<h-60:
                    workspace.interact(gesture.pointer,gesture.pinching,
                                       gesture.pinch_started,gesture.pinch_ended)
                else:
                    workspace.finish_action()
            else:
                missing_frames+=1
                workspace.finish_action()
                if missing_frames>=3:
                    engine.reset()
            now=time.perf_counter()
            fps=1/max(now-previous,1e-6)
            previous=now
            output=render(frame,workspace,landmarks,
                          gesture.pointer if gesture else None,
                          gesture.pinching if gesture else False,fps,show_skeleton)
            cv2.imshow("AirDesk | Touchless Studio",output)
            key=cv2.waitKey(1)&0xFF
            if key in (ord('q'),27):
                break
            elif key==ord('1'):
                workspace.set_mode('draw')
            elif key==ord('2'):
                workspace.set_mode('move')
            elif key==ord('3'):
                workspace.set_mode('erase')
            elif key==ord('c'):
                workspace.color_index=(workspace.color_index+1)%len(PALETTE)
                workspace.status='COLOR CHANGED'
            elif key==ord('u'):
                workspace.undo()
            elif key==ord('x'):
                workspace.clear()
            elif key==ord('h'):
                show_skeleton=not show_skeleton
            elif key==ord('s'):
                target=ROOT/'exports'/f"airdesk_{datetime.now():%Y%m%d_%H%M%S}.png"
                target.parent.mkdir(exist_ok=True)
                if cv2.imwrite(str(target),output):
                    workspace.status=f"SAVED {target.name}"
                    print(f"Saved: {target}")
                else:
                    workspace.status="SAVE FAILED"
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc)
        return 1
    finally:
        if tracker is not None:
            tracker.close()
        cap.release()
        cv2.destroyAllWindows()
    return 0

if __name__=='__main__':
    raise SystemExit(main())
