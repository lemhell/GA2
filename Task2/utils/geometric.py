from math import sqrt, cos, asin
from typing import List


class Point:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(str(self))


class Segment:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def length(self):
        """
        Euclidean distance between points of the segment
        :return: euclidean distance
        """
        return pow(self.p1.x - self.p2.x, 2) * pow(self.p1.y - self.p2.y, 2)

    def orientation(self, other_point):
        slope = (self.p2.y - self.p1.y) * (other_point.x - self.p2.x) - \
                (other_point.y - self.p2.y) * (self.p2.x - self.p1.x)

        if slope > 0:
            return 1
        elif slope < 0:
            return -1
        else:
            return 0

    def is_intersect(self, other_segment):
        # TODO: implement special case
        return self.orientation(other_segment.p1) != self.orientation(other_segment.p2) \
               and other_segment.orientation(self.p1) != other_segment.orientation(self.p2)

    def is_intersect_polygon(self, polygon):

        for s in polygon.segments:
            if self.is_intersect(s):
                return True

        return False


class Polygon:

    def __init__(self, segments: List[Segment]):
        self.segments = segments

    def points(self):
        all_points = set()

        for s in self.segments:
            all_points.add(s.p1)
            all_points.add(s.p2)

        return list(all_points)

    def is_intersect(self, other_polygon):

        # If current polygon contains another - they intersect
        if self.is_contain(other_polygon):
            return True

        # If pair of the polygons' segments intersect - they intersect
        for s1 in self.segments:
            for s2 in other_polygon.segments:
                if s1.is_intersect(s2):
                    return True

        # Otherwise - not
        return False

    def is_contain(self, other_polygon):

        for p in other_polygon.points():

            # Test whether every point of another polygon is inside of the polygon
            test_segment = Segment(p, Point(p.x + 1000, p.y))
            intersections_count = 0

            for s in self.segments:
                if s.is_intersect(test_segment):
                    intersections_count += 1

            # If even intersections count - point is outside
            if intersections_count % 2 == 0:
                return False

        return True


def get_visible_border_from(p: Point, viewing_angle: int, y_threshold=0, orientation={0, -1}) -> Segment:
    """
    Returns the "horizons border" that can be visible from the point p with vision_angle and orientation as a Segment.
    Segment bordered by y coordinate y_threshold.
    :param p: point of view
    :param viewing_angle: viewing angle
    :param y_threshold: y coordinate of the farthest points (default 0)
    :param orientation: orientation of the point (doesn't implemented, default for {0, -1}
    :return: polygon of two segments: from the point p to the farthest left and right points
    """
    # TODO: implement orientation
    # calculated by formula
    abs_x_diff = (p.y - y_threshold) * sqrt(1 / pow(cos(viewing_angle / 2), 2) - 1)

    return Segment(Point(p.x - abs_x_diff, y_threshold), Point(p.x + abs_x_diff, y_threshold))


def get_polygon_visible_from(p: Point, viewing_angle: int, y_threshold=0, orientation={0, -1}) -> Polygon:
    """
    Returns the polygon that represents visible area from the point p with angle = view_angle and orientation.
    :param p: point of view
    :param viewing_angle: viewing angle
    :param y_threshold: y coordinate of the farthest points (default 0)
    :param orientation: orientation of the point (doesn't implemented, default for {0, -1}
    :return: polygon of two segments: from the point p to the farthest left and right points
    """

    visible_border = get_visible_border_from(p, viewing_angle, y_threshold, orientation)

    return get_polygon_of_visible_border(p, visible_border)


def get_polygon_of_visible_border(view_point: Point, visible_border: Segment) -> Polygon:
    """

    :param view_point:
    :param visible_border:
    :return:
    """
    return Polygon([Segment(view_point, visible_border.p1), visible_border, Segment(view_point, visible_border.p2)])


def get_overlapping_angle_for_circle(p: Point, circle_center: Point, radius: int):
    """
    Returns angle, by which circle with circle_center and radius overlaps view from the point p
    :param p: point of view
    :param circle_center: center of the circle
    :param radius: circle radius
    :return: angle in degrees
    """
    # TODO: implement special case
    return 2 * asin(radius / Segment(p, circle_center).length())
