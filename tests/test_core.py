import pytest
from airdesk.geometry import Point, distance, normalized_pinch, clamp
from airdesk.gestures import GestureEngine
from airdesk.workspace import Workspace

def hand(ratio):
    points=[Point(0,0) for _ in range(21)]
    points[5]=Point(0,0)
    points[17]=Point(100,0)
    points[4]=Point(0,0)
    points[8]=Point(ratio*100,0)
    points[6]=Point(10,0)
    return points

def test_geometry():
    assert distance(Point(0,0),Point(3,4))==5
    assert clamp(12,0,10)==10
    assert normalized_pinch(hand(.2))==pytest.approx(.2)

def test_gesture_dwell_hysteresis():
    engine=GestureEngine(smoothing=1,dwell_frames=2)
    assert not engine.update(hand(.2)).pinching
    g=engine.update(hand(.2))
    assert g.pinching and g.pinch_started
    assert engine.update(hand(.4)).pinching
    assert engine.update(hand(.8)).pinching
    g=engine.update(hand(.8))
    assert not g.pinching and g.pinch_ended

def test_gesture_reset():
    engine=GestureEngine(dwell_frames=1)
    assert engine.update(hand(.2)).pinching
    engine.reset()
    assert not engine.pinching

def test_workspace_draw_undo_clear():
    ws=Workspace(800,600)
    ws.interact(Point(200,200),True,True,False)
    ws.interact(Point(210,210),True,False,False)
    ws.interact(Point(210,210),False,False,True)
    assert len(ws.strokes)==1 and len(ws.strokes[0])==2
    ws.undo()
    assert not ws.strokes
    ws.clear()
    assert not ws.strokes

def test_workspace_drag_clamped():
    ws=Workspace(800,600)
    ws.set_mode('move')
    n=ws.notes[0]
    ws.interact(Point(n.x+10,n.y+10),True,True,False)
    ws.interact(Point(900,900),True,False,False)
    assert n.x==610 and n.y==484
    ws.interact(Point(900,900),False,False,True)
    assert ws.selected_note is None

def test_invalid_mode():
    with pytest.raises(ValueError):
        Workspace(800,600).set_mode('invalid')
