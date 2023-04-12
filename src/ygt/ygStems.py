# import copy
from typing import Optional, List, TYPE_CHECKING
# if TYPE_CHECKING:
from .ygModel import ygPoint, ygGlyph


class stemFinder:
    def __init__(self, p1: ygPoint, p2: ygPoint, yg_glyph: ygGlyph):
        self.yg_glyph = yg_glyph
        self.contours = []
        contour = []
        points = yg_glyph.points()
        for p in points:
            contour.append(p)
            if p.end_of_contour:
                self.contours.append(contour)
                contour = []
        self.high_point = p1
        self.low_point = p2
        if self.yg_glyph.current_axis() == "y":
            if self.high_point.font_y < self.low_point.font_y:
                self.high_point, self.low_point = self.low_point, self.high_point
        else:
            if self.high_point.font_x > self.low_point.font_x:
                self.high_point, self.low_point = self.low_point, self.high_point

    def find_point_by_index(self, i: int, c: List[ygPoint]) -> Optional[ygPoint]:
        """ Find the point with index i in contour c. Returns None if not found.
        """
        for p in c:
            if p.index == i:
                return p

    def next_point(self, p: ygPoint, c: List[ygPoint]) -> ygPoint:
        """ p a ygPoint object; c a contour
        """
        last_point = c[-1].index
        if p.index < last_point:
            return self.find_point_by_index(p.index + 1, c)
        else:
            return c[0]

    def which_contour(self, pt: ygPoint) -> Optional[List[ygPoint]]:
        """ Return the contour (list of ygPoint objects) containing pt.
        """
        for c in self.contours:
            if pt in c:
                return c
        return None
    
    def x_direction(self, pt: ygPoint) -> str:
        """ Find the x direction of a line or curve at the location of
            point pt. Returns "left," "right," or "same" if this pt
            has the same x location as the next pt.
        """
        next_point = self.next_point(pt, self.which_contour(pt))
        # print("This point index: " + str(pt.index))
        # print("Next point index: " + str(next_point.index))
        if self.yg_glyph.current_axis() == "y":
            next_x = next_point.font_x
            this_x = pt.font_x
            if next_x > this_x:
                return "right"
            elif this_x > next_x:
                return "left"
            else:
                return "same"
        
    def y_direction(self, pt: ygPoint) -> str:
        """ Find the y direction of a line or curve at the location of
            point pt. Returns "up," "down," or "same" if this pt
            has the same y location as the next pt.
        """
        next_point = self.next_point(pt, self.which_contour(pt))
        next_y = next_point.font_y
        this_y = pt.font_y
        if next_y > this_y:
            return "up"
        elif this_y > next_y:
            return "down"
        else:
            return "same"
        
    def get_color(self) -> str:
        result = "graydist"
        if self.yg_glyph.current_axis() == "x":
            high_y_dir = self.y_direction(self.high_point)
            low_y_dir = self.y_direction(self.low_point)
            print("high_y_dir: " + high_y_dir)
            print("low_y_dir: " + low_y_dir)
            if high_y_dir == "up" and low_y_dir == "down":
                result = "blackdist"
            elif high_y_dir == "down" and low_y_dir == "up":
                result = "whitedist"
        else:
            high_x_dir = self.x_direction(self.high_point)
            low_x_dir  = self.x_direction(self.low_point)
            if high_x_dir == "right" and low_x_dir == "left":
                result = "blackdist"
            elif high_x_dir == "left" and low_x_dir == "right":
                result = "whitedist"
        return result

