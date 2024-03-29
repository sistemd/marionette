from __future__ import annotations

import enum
from builtins import bool
from typing import NamedTuple

import math


class Line(NamedTuple):
    origin: complex
    offset: complex

    @staticmethod
    def from_to(origin: complex, end: complex) -> Line:
        return Line(origin, end - origin)

    @property
    def end(self) -> complex:
        return self.origin + self.offset

    @property
    def is_vertical(self) -> bool:
        return self.offset.real == 0

    @property
    def is_horizontal(self) -> bool:
        return self.offset.imag == 0

    def intersects(self, other: Line) -> bool:
        def check_cross_products(first: Line, second: Line) -> bool:
            p1 = cross_product(second.origin - first.origin, first.offset)
            p2 = cross_product(second.end - first.origin, first.offset)
            return (p1 >= 0 >= p2 or p2 >= 0 >= p1) and not (math.isclose(p1, 0) and math.isclose(p2, 0))

        return check_cross_products(self, other) and check_cross_products(other, self)

    @property
    def left_real(self) -> float:
        return min(self.origin.real, self.end.real)

    @property
    def right_real(self) -> float:
        return max(self.origin.real, self.end.real)

    @property
    def upper_imag(self) -> float:
        return min(self.origin.imag, self.end.imag)

    @property
    def lower_imag(self) -> float:
        return max(self.origin.imag, self.end.imag)

    @property
    def bounding_box_width(self) -> float:
        return abs(self.offset.real)

    @property
    def bounding_box_height(self) -> float:
        return abs(self.offset.imag)

    def overlaps_on_real_axis(self, other: Line) -> bool:
        if self.bounding_box_width >= other.bounding_box_width:
            return (self.left_real <= other.left_real <= self.right_real or
                    self.left_real <= other.right_real <= self.right_real)
        return (other.left_real <= self.left_real <= other.right_real or
                other.left_real <= self.right_real <= other.right_real)

    def overlaps_on_imag_axis(self, other: Line) -> bool:
        if self.bounding_box_height >= other.bounding_box_height:
            return (self.upper_imag <= other.upper_imag <= self.lower_imag or
                    self.upper_imag <= other.lower_imag <= self.lower_imag)
        return (other.upper_imag <= self.upper_imag <= other.lower_imag or
                other.upper_imag <= self.lower_imag <= other.lower_imag)


@enum.unique
class Corner(enum.Enum):
    UPPER_LEFT = enum.auto()
    UPPER_RIGHT = enum.auto()
    LOWER_LEFT = enum.auto()
    LOWER_RIGHT = enum.auto()


class Rectangle:
    __slots__ = 'upper_left', 'dimensions'

    def __init__(self, upper_left: complex, dimensions: complex) -> None:
        self.upper_left = upper_left
        self.dimensions = dimensions

    def get_point(self, corner: Corner) -> complex:
        if corner is Corner.UPPER_LEFT:
            return self.upper_left
        if corner is Corner.UPPER_RIGHT:
            return self.upper_right
        if corner is Corner.LOWER_LEFT:
            return self.lower_left
        if corner is Corner.LOWER_RIGHT:
            return self.lower_right
        assert False

    @property
    def left_real(self) -> float:
        return self.upper_left.real

    @left_real.setter
    def left_real(self, value: float) -> None:
        self.upper_left = value + self.upper_imag * 1j

    @property
    def right_real(self) -> float:
        return self.upper_left.real + self.dimensions.real

    @right_real.setter
    def right_real(self, value: float) -> None:
        self.upper_left = value - self.dimensions.real + self.upper_imag * 1j

    @property
    def upper_imag(self) -> float:
        return self.upper_left.imag

    @upper_imag.setter
    def upper_imag(self, value: float) -> None:
        self.upper_left = self.left_real + value * 1j

    @property
    def lower_imag(self) -> float:
        return self.upper_left.imag + self.dimensions.imag

    @lower_imag.setter
    def lower_imag(self, value: float) -> None:
        self.upper_left = self.left_real + (value - self.dimensions.imag) * 1j

    @property
    def upper_right(self) -> complex:
        return self.upper_left + self.dimensions.real

    @property
    def lower_left(self) -> complex:
        return self.upper_left + self.dimensions.imag * 1j

    @property
    def lower_right(self) -> complex:
        return self.upper_left + self.dimensions

    @property
    def center(self) -> complex:
        return self.upper_left + self.dimensions / 2

    @center.setter
    def center(self, value: complex) -> None:
        self.upper_left = value - self.dimensions / 2

    @property
    def top_line(self) -> Line:
        return Line.from_to(origin=self.upper_left, end=self.upper_right)

    @property
    def bottom_line(self) -> Line:
        return Line.from_to(origin=self.lower_left, end=self.lower_right)

    @property
    def left_line(self) -> Line:
        return Line.from_to(origin=self.upper_left, end=self.lower_left)

    @property
    def right_line(self) -> Line:
        return Line.from_to(origin=self.upper_right, end=self.lower_right)

    # TODO Test me
    def overlaps(self, other: Rectangle) -> bool:
        return self.overlaps_on_real_axis(other) and self.overlaps_on_imag_axis(other)

    def overlaps_on_real_axis(self, other: Rectangle) -> bool:
        if self.dimensions.real >= other.dimensions.real:
            return (self.left_real <= other.left_real <= self.right_real or
                    self.left_real <= other.right_real <= self.right_real)
        return (other.left_real <= self.left_real <= other.right_real or
                other.left_real <= self.right_real <= other.right_real)

    def overlaps_on_imag_axis(self, other: Rectangle) -> bool:
        if self.dimensions.imag >= other.dimensions.imag:
            return (self.upper_imag <= other.upper_imag <= self.lower_imag or
                    self.upper_imag <= other.lower_imag <= self.lower_imag)
        return (other.upper_imag <= self.upper_imag <= other.lower_imag or
                other.upper_imag <= self.lower_imag <= other.lower_imag)

    def contains_point(self, point: complex) -> bool:
        return (self.left_real <= point.real <= self.right_real and
                self.upper_imag <= point.imag <= self.lower_imag)


def normalized(c: complex) -> complex:
    if c == 0:
        return 0
    intensity = abs(c)
    return c / intensity


def magnitude_squared(c: complex) -> float:
    return c.real * c.real + c.imag * c.imag


def cross_product(c1: complex, c2: complex) -> float:
    return c1.real * c2.imag - c1.imag * c2.real


def dot_product(c1: complex, c2: complex) -> float:
    return c1.real * c2.real + c1.imag * c2.imag


@enum.unique
class Direction(enum.IntEnum):
    NONE = 0
    LEFT = -1
    RIGHT = 1
