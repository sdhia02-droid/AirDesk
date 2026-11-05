"""Gesture recognition with hysteresis, dwell and smoothed pointer position."""
from __future__ import annotations
from dataclasses import dataclass
from .geometry import Point, interpolate, normalized_pinch, index_extended

@dataclass(frozen=True)
class Gesture:
    pointer: Point
    pinching: bool
    pinch_started: bool
    pinch_ended: bool
    pointing: bool


class GestureEngine:
    def __init__(self, smoothing: float = 0.38, pinch_on: float = 0.34,
                 pinch_off: float = 0.53, dwell_frames: int = 2):
        if not 0 < smoothing <= 1:
            raise ValueError("smoothing must be in (0,1]")
        if not 0 < pinch_on < pinch_off:
            raise ValueError("pinch_on must be less than pinch_off")
        self.smoothing = smoothing
        self.pinch_on = pinch_on
        self.pinch_off = pinch_off
        self.dwell_frames = max(1, dwell_frames)
        self.pointer: Point | None = None
        self.pinching = False
        self._candidate = False
        self._candidate_frames = 0

    def reset(self) -> None:
        self.pointer = None
        self.pinching = False
        self._candidate = False
        self._candidate_frames = 0

    def update(self, points: list[Point]) -> Gesture:
        if len(points) != 21:
            raise ValueError("Expected 21 hand landmarks")
        raw = points[8]
        self.pointer = raw if self.pointer is None else interpolate(self.pointer, raw, self.smoothing)
        ratio = normalized_pinch(points)
        desired = ratio < (self.pinch_off if self.pinching else self.pinch_on)
        if desired != self._candidate:
            self._candidate = desired
            self._candidate_frames = 1
        else:
            self._candidate_frames += 1
        before = self.pinching
        if self._candidate_frames >= self.dwell_frames:
            self.pinching = desired
        return Gesture(self.pointer, self.pinching,
                       not before and self.pinching, before and not self.pinching,
                       index_extended(points))
