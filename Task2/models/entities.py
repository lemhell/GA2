from typing import List, Dict

from math import sin, cos, pi

from utils.geometric import Point, Polygon, Segment, get_visible_border_from, \
    get_polygon_of_visible_border


class EntitiesTypes:
    ENEMIES = "enemies"
    TURRETS = "turrets"
    OBSTACLES = "obstacles"
    E_TANK = "tank"
    E_CARRIER = "carrier"
    T_TURRET = "turret"
    O_ROUND = "round"
    O_SQUARE = "square"


class BaseEntity:
    def __init__(self, number: int, top_left: Point, width: int = None, height: int = None, radius: int = None):
        self.radius = radius
        self.width = width
        self.height = height
        self.top_left = top_left
        self.number = number

    def polygon(self):
        segments = [Segment(self.top_left,
                            Point(self.top_left.x + self.width, self.top_left.y)),
                    Segment(Point(self.top_left.x + self.width, self.top_left.y),
                            Point(self.top_left.x + self.width, self.top_left.y + self.height)),
                    Segment(Point(self.top_left.x + self.width, self.top_left.y + self.height),
                            Point(self.top_left.x, self.top_left.y + self.height)),
                    Segment(Point(self.top_left.x, self.top_left.y + self.height),
                            self.top_left)]

        return Polygon(segments)

    def __str__(self):
        return str(self.number)


class Tank(BaseEntity):
    _width, _height = 4, 5

    def __init__(self, number: int, top_left_corner: Point):
        BaseEntity.__init__(self, number, top_left_corner, self._width, self._height)


class Carrier(BaseEntity):
    _width, _height = 3, 8

    def __init__(self, number: int, top_left_corner: Point):
        BaseEntity.__init__(self, number, top_left_corner, self._width, self._height)


class Obstacle(BaseEntity):

    _round_edges = 100

    def __init__(self, number: int, top_left_corner: Point, radius: int = None, width: int = None, height: int = None):

        if None not in (width, height):  # init squared
            BaseEntity.__init__(self, number, top_left_corner, width, height)
        else:  # init rounded
            BaseEntity.__init__(self, number, top_left_corner, radius=radius)

    def polygon(self):
        if self.radius:
            return self._rounded_polygon()
        return BaseEntity.polygon(self)

    def _rounded_polygon(self):
        segments = []
        curr_angle = 0
        angle_diff = 2 * pi / float(self._round_edges)

        curr_point = self._point_of_circle(curr_angle)
        for i in range(0, self._round_edges):

            next_point = self._point_of_circle(curr_angle + angle_diff)

            segments.append(Segment(curr_point, next_point))

            curr_angle += angle_diff
            curr_point = next_point

        return Polygon(segments)

    def _point_of_circle(self, curr_angle):
        return Point(self.top_left.x + self.radius * cos(curr_angle), self.top_left.y + self.radius * sin(curr_angle))


class Turret(BaseEntity):
    _width, _height = 1, 1
    view_angle = pi / 3

    def __init__(self, number: int, top_left_corner: Point):
        BaseEntity.__init__(self, number, top_left_corner, self._width, self._height)


class Field:
    def __init__(self, width: int, height: int, entities: Dict):
        self.height = height
        self.width = width
        self._parse_entities(entities)

    @classmethod
    def _parse_entity(cls, e):

        if e["type"] == EntitiesTypes.E_CARRIER:
            return Carrier(e["number"], Point(e["x"], e["y"]))

        elif e["type"] == EntitiesTypes.E_TANK:
            return Tank(e["number"], Point(e["x"], e["y"]))

        elif e["type"] == EntitiesTypes.T_TURRET:
            return Turret(e["number"], Point(e["x"], e["y"]))

        elif e["type"] == EntitiesTypes.O_SQUARE:
            return Obstacle(e["number"], Point(e["x"], e["y"]), width=e["width"], height=e["height"])

        elif e["type"] == EntitiesTypes.O_ROUND:
            return Obstacle(e["number"], Point(e["x"], e["y"]), radius=e["radius"])

        else:
            raise ValueError("Unknown entity type")

    def _parse_entities(self, entities: Dict):

        # Parse Turrets
        self.turrets = list(map(self._parse_entity, entities[EntitiesTypes.TURRETS]))

        # Parse enemies (Tanks and Carriers)
        self.enemies = list(map(self._parse_entity, entities[EntitiesTypes.ENEMIES]))

        # Parse Obstacles
        self.obstacles = list(map(self._parse_entity, entities[EntitiesTypes.OBSTACLES]))

        self.fire_segments = []

    def solve(self, accuracy: int):

        turrets_goals = {}
        border_y = 0  # TODO: make it = min(enemies.y)

        # Consider every turret
        for t in self.turrets:

            # Get visible border (segment) from the turret, and polygon, that can be visible
            visible_border = get_visible_border_from(t.top_left, Turret.view_angle, border_y)
            visible_polygon = get_polygon_of_visible_border(t.top_left, visible_border)

            # Scan enemies and find enemies that are potentially achievable from the turret
            possible_enemies = []
            for e in self.enemies:
                if visible_polygon.is_intersect(e.polygon()):
                    possible_enemies.append(e)

            # Try to fire to each point from border with the given accuracy
            achievable_enemies = []
            for destination_x in range(int(visible_border.p1.x), int(visible_border.p2.x + accuracy), accuracy):
                fire_segment = Segment(t.top_left, Point(destination_x, border_y))

                achievable_enemy = self._has_entity_achievable_from(possible_enemies, fire_segment)
                if achievable_enemy and achievable_enemy not in achievable_enemies:

                    # Is fire segment overlaps by an obstacle?
                    achievable_obstacle = self._has_entity_achievable_from(self.obstacles, fire_segment)

                    # If obstacle exists, is enemy closer than an obstacle?
                    if not achievable_obstacle or self._is_entity1_closer_to(t.top_left,
                                                                             achievable_enemy,
                                                                             achievable_obstacle):
                        achievable_enemies.append(achievable_enemy)
                        self.fire_segments.append(fire_segment)

            # Fix achievable enemies for the turret
            turrets_goals[t.number] = achievable_enemies

        return turrets_goals

    @classmethod
    def _is_entity1_closer_to(cls, p: Point, e1: BaseEntity, e2: BaseEntity):

        return Segment(p, e1.top_left).length() < Segment(p, e2.top_left).length()

    @classmethod
    def _has_entity_achievable_from(cls, entities: List[BaseEntity], segment: Segment):

        # Is fire segment achieve any enemy?
        achievable_entity = None
        for e in entities:
            if segment.is_intersect_polygon(e.polygon()):
                achievable_entity = e
                break

        return achievable_entity

    def draw(self, canvas):

        for t in self.turrets:
            canvas.create_oval(t.top_left.x - 1, t.top_left.y - 1,
                               t.top_left.x + 1, t.top_left.y + 1)

        for e in self.enemies:
            canvas.create_rectangle(e.top_left.x, e.top_left.y,
                                    e.top_left.x + e.width, e.top_left.y + e.height)

        for o in self.obstacles:
            if o.radius:
                canvas.create_oval(o.top_left.x - o.radius, o.top_left.y - o.radius,
                                   o.top_left.x + o.radius, o.top_left.y + o.radius)
            else:
                canvas.create_rectangle(o.top_left.x, o.top_left.y,
                                        o.top_left.x + o.width, o.top_left.y + o.height)

        for s in self.fire_segments:
            canvas.create_line(s.p1.x, s.p1.y,
                               s.p2.x, s.p2.y,
                               fill="red",
                               dash=(1, 1))
