"""OpenCV UI renderer; no external GUI framework required."""
from __future__ import annotations
import cv2
import numpy as np
from .geometry import Point
from .workspace import Workspace, PALETTE

BG = (23, 22, 19)
WHITE = (240, 242, 245)
MUTED = (143, 151, 160)
ACCENT = (245, 198, 76)
CONNECTIONS = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
               (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),
               (15,16),(13,17),(17,18),(18,19),(19,20),(0,17)]

def text(img, value: str, x: int, y: int, scale=.55, color=WHITE, thickness=1):
    cv2.putText(img, value, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                thickness, cv2.LINE_AA)

def render(frame: np.ndarray, ws: Workspace, landmarks: list[Point] | None,
           pointer: Point | None, pinching: bool, fps: float, show_skeleton=True) -> np.ndarray:
    h, w = frame.shape[:2]
    tint = np.full_like(frame, BG)
    canvas = cv2.addWeighted(frame, .48, tint, .52, 0)
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0,0), (w,75), (14,16,20), -1)
    cv2.rectangle(overlay, (0,h-54), (w,h), (14,16,20), -1)
    canvas = cv2.addWeighted(overlay,.9,canvas,.1,0)
    text(canvas,"AIRDESK",20,35,.9,WHITE,2)
    text(canvas,"/ TOUCHLESS STUDIO",163,34,.48,MUTED)
    text(canvas,f"{fps:.0f} FPS",w-95,31,.52,ACCENT)
    text(canvas,"1 DRAW   2 MOVE   3 ERASE   C COLOR   U UNDO   X CLEAR   S SAVE   H HAND   Q QUIT",
         20,h-21,.43,MUTED)
    labels = ["DRAW","MOVE","ERASE"]
    for i, mode in enumerate(labels):
        x = 20+i*110
        active = ws.mode == mode.lower()
        cv2.rectangle(canvas,(x,49),(x+100,69),ACCENT if active else (57,59,62),-1)
        text(canvas,mode,x+18,64,.42,BG if active else WHITE,1)
    for i,c in enumerate(PALETTE):
        x = w-215+i*43
        cv2.circle(canvas,(x,60),12,c,-1,cv2.LINE_AA)
        if ws.color_index==i:
            cv2.circle(canvas,(x,60),16,WHITE,2,cv2.LINE_AA)
    for note in ws.notes:
        x,y = int(note.x),int(note.y)
        cv2.rectangle(canvas,(x+5,y+7),(x+note.w+5,y+note.h+7),(8,9,12),-1)
        cv2.rectangle(canvas,(x,y),(x+note.w,y+note.h),(39,44,51),-1)
        cv2.rectangle(canvas,(x,y),(x+note.w,y+4),ACCENT,-1)
        text(canvas,note.title,x+15,y+40,.65,WHITE,2)
        text(canvas,note.subtitle,x+15,y+69,.37,MUTED)
        text(canvas,"PINCH + DRAG",x+15,y+96,.35,ACCENT)
    for stroke in ws.strokes + ([ws.active_stroke] if ws.active_stroke else []):
        if not stroke:
            continue
        pts = np.array([(int(p.x),int(p.y)) for p in stroke],dtype=np.int32)
        if len(pts)==1:
            cv2.circle(canvas,tuple(pts[0]),3,PALETTE[ws.color_index],-1)
        else:
            cv2.polylines(canvas,[pts],False,PALETTE[ws.color_index],4,cv2.LINE_AA)
    if landmarks and show_skeleton:
        pts = [(int(p.x*w),int(p.y*h)) for p in landmarks]
        for a,b in CONNECTIONS:
            cv2.line(canvas,pts[a],pts[b],(100,155,145),2,cv2.LINE_AA)
        for i,p in enumerate(pts):
            cv2.circle(canvas,p,5,ACCENT if i in (4,8) else (190,215,220),-1,cv2.LINE_AA)
    if pointer:
        p=(int(pointer.x),int(pointer.y))
        cv2.circle(canvas,p,20 if pinching else 13,ACCENT if pinching else WHITE,2,cv2.LINE_AA)
        cv2.circle(canvas,p,4,ACCENT,-1,cv2.LINE_AA)
        text(canvas,"PINCH" if pinching else "TRACKING",p[0]+25,p[1]-13,.42,ACCENT)
    else:
        text(canvas,"SHOW YOUR HAND TO THE CAMERA",20,h-75,.55,ACCENT)
    text(canvas,ws.status,350,64,.43,WHITE)
    return canvas
