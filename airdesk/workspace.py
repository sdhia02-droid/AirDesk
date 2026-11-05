"""State and interactions for the drawing canvas and draggable notes."""
from __future__ import annotations
from dataclasses import dataclass, field
from .geometry import Point, distance, clamp

PALETTE = [(255, 220, 90), (125, 245, 130), (100, 155, 255), (240, 120, 240)]  # BGR

@dataclass
class Note:
    x: float
    y: float
    w: int = 190
    h: int = 116
    title: str = "IDEA"
    subtitle: str = "Drag with a pinch"

    def contains(self, p: Point) -> bool:
        return self.x <= p.x <= self.x + self.w and self.y <= p.y <= self.y + self.h

@dataclass
class Workspace:
    width: int
    height: int
    mode: str = "draw"
    color_index: int = 0
    strokes: list[list[Point]] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    active_stroke: list[Point] | None = None
    selected_note: int | None = None
    drag_offset: Point = Point(0, 0)
    status: str = "READY"

    def __post_init__(self) -> None:
        if not self.notes:
            self.notes = [Note(self.width * .47, self.height * .32,
                               title="AIRDESK", subtitle="Touchless workspace"),
                          Note(self.width * .17, self.height * .57,
                               title="CREATE", subtitle="Pinch to move me")]

    def set_mode(self, mode: str) -> None:
        if mode not in ("draw", "move", "erase"):
            raise ValueError("Invalid mode")
        self.finish_action()
        self.mode = mode
        self.status = mode.upper()

    def finish_action(self) -> None:
        if self.active_stroke:
            self.strokes.append(self.active_stroke)
        self.active_stroke = None
        self.selected_note = None

    def undo(self) -> None:
        self.finish_action()
        if self.strokes:
            self.strokes.pop()
            self.status = "UNDONE"

    def clear(self) -> None:
        self.finish_action()
        self.strokes.clear()
        self.status = "CANVAS CLEARED"

    def interact(self, pointer: Point, pinching: bool, started: bool, ended: bool) -> None:
        if ended or not pinching:
            self.finish_action()
            return
        if self.mode == "draw":
            if started or self.active_stroke is None:
                self.active_stroke = [pointer]
            elif distance(pointer, self.active_stroke[-1]) > 2:
                self.active_stroke.append(pointer)
        elif self.mode == "erase":
            radius = 24
            self.strokes = [stroke for stroke in self.strokes
                            if not any(distance(p, pointer) < radius for p in stroke)]
            self.active_stroke = None
        elif self.mode == "move":
            if started:
                for i in reversed(range(len(self.notes))):
                    note = self.notes[i]
                    if note.contains(pointer):
                        self.selected_note = i
                        self.drag_offset = Point(pointer.x - note.x, pointer.y - note.y)
                        break
            if self.selected_note is not None:
                note = self.notes[self.selected_note]
                note.x = clamp(pointer.x - self.drag_offset.x, 0, max(0, self.width - note.w))
                note.y = clamp(pointer.y - self.drag_offset.y, 90, max(90, self.height - note.h))
