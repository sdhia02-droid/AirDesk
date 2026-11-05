"""Pure geometry functions, independent of camera and MediaPipe."""
from __future__ import annotations
from dataclasses import dataclass
from math import hypot

@dataclass(frozen=True)
class Point:
    x: float
    y: float


def distance(a: Point, b: Point) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def interpolate(a: Point, b: Point, alpha: float) -> Point:
    return Point(a.x + alpha * (b.x - a.x), a.y + alpha * (b.y - a.y))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalized_pinch(points: list[Point]) -> float:
    """Thumb-to-index distance divided by palm width for scale invariance."""
    if len(points) < 21:
        raise ValueError("Expected 21 hand landmarks")
    return distance(points[4], points[8]) / max(distance(points[5], points[17]), 1e-6)


def index_extended(points: list[Point]) -> bool:
    """Simple orientation-agnostic extension heuristic using joint distances."""
    if len(points) < 21:
        raise ValueError("Expected 21 hand landmarks")
    return distance(points[8], points[5]) > distance(points[6], points[5]) * 1.35
