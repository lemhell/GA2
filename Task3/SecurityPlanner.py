from math import sqrt
from math import acos
from math import atan2


class SecurityPlanner(object):
    def __init__(self, segments, blue_points):
        self._step_through_segment = 1.0
        self._segments = segments
        self._blue_points = blue_points

    def find_cameras_positions(self):
        d = {}
        for segm in self._segments:
            for p in self._get_steps_for_segment(segm):
                d[p] = self._get_view_points(p, segm[0], segm[1])

        print('Visible sets calculated')

        for p1, vs1 in d.items():
            for p2, vs2 in d.items():
                if self._is_visible_sets_full(vs1, vs2):
                    return (p1, p2)

        return None

    def _is_visible_sets_full(self, vs1, vs2):
        for s1 in vs1:
            for s2 in vs2:
                if len(s1 | s2) == len(self._blue_points):
                    return True
        return False

    def _get_view_points(self, p, segm_a, segm_b):
        visible_points = {}
        for k, bp in self._blue_points.items():
            if not self._is_intersect_something((p, bp)):
                visible_points[k] = bp

        rvp = []

        for i, vp_i in visible_points.items():
            for j, vp_j in visible_points.items():
                if (i != j) and (SecurityPlanner._is_90_degrees_sector(p, vp_i, vp_j)):
                    if not (SecurityPlanner._is_in_sector(segm_a, p, vp_i, vp_j) and
                            SecurityPlanner._is_in_sector(segm_b, p, vp_i, vp_j)):
                        # Find points in sector (p, vp_i, vp_j)
                        sector_points = SecurityPlanner._get_points_in_sector(p, vp_i, vp_j, visible_points)
                        rvp.append(sector_points | {i, j})
                    elif SecurityPlanner._is_in_sector(segm_a, p, vp_i, vp_j):
                        # Find points in sectors (p, a, vp_i) and (p, a, vp_j) separately
                        sector_points = SecurityPlanner._get_points_in_sector(p, segm_a, vp_i, visible_points)
                        rvp.append(sector_points | {i})
                        sector_points = SecurityPlanner._get_points_in_sector(p, segm_a, vp_j, visible_points)
                        rvp.append(sector_points | {j})
                    elif SecurityPlanner._is_in_sector(segm_b, p, vp_i, vp_j):
                        # Find points in sectors (p, b, vp_i) and (p, b, vp_j) separately
                        sector_points = SecurityPlanner._get_points_in_sector(p, segm_b, vp_i, visible_points)
                        rvp.append(sector_points | {i})
                        sector_points = SecurityPlanner._get_points_in_sector(p, segm_b, vp_j, visible_points)
                        rvp.append(sector_points | {j})

        for k, vp in visible_points.items():
            # I know {k} may be already in rvp
            rvp.append({k})

        return rvp

    def _is_intersect_something(self, segm):
        for s in self._segments:
            if SecurityPlanner._is_intersect(segm, s):
                return True
        return False

    @staticmethod
    def _is_intersect(s1, s2):
        p1 = s1[0]
        q1 = s1[1]
        p2 = s2[0]
        q2 = s2[1]

        return (SecurityPlanner._calc_orientation(p1, q1, p2) !=
                SecurityPlanner._calc_orientation(p1, q1, q2)) and \
               (SecurityPlanner._calc_orientation(p2, q2, p1) !=
                SecurityPlanner._calc_orientation(p2, q2, q1))

    @staticmethod
    def _calc_orientation(p, q, t):
        orient_value = (q[1] - p[1]) * (t[0] - q[0]) - (t[1] - q[1]) * (q[0] - p[0])
        if orient_value > 0.0:
            return 1
        else:
            return -1

    # Assume that sector is <= 90 degrees
    @staticmethod
    def _is_in_sector(p, root, left, right):
        return (SecurityPlanner._calc_orientation(root, left, p) !=
                SecurityPlanner._calc_orientation(root, right, p))

    @staticmethod
    def _is_90_degrees_sector(root, left, right):
        a = (left[0] - root[0], left[1] - root[1])
        b = (right[0] - root[0], right[1] - root[1])
        return SecurityPlanner._calc_cross_product(a, b) > 0.0

    @staticmethod
    def _get_points_in_sector(root, left, right, points):
        sector_points = set()
        for k, p in points.items():
            if SecurityPlanner._is_in_sector(p, root, left, right):
                sector_points.add(k)
        return sector_points

    def _get_steps_for_segment(self, s):
        steps = []
        s_len = SecurityPlanner._calc_segment_length(s)
        step = self._step_through_segment
        d_t = 1.0 / (s_len / step)
        t = 0.0
        while t <= 1.0:
            steps.append((s[0][0] + t*(s[1][0] - s[0][0]), s[0][1] + t*(s[1][1] - s[0][1])))
            t += d_t

        return steps

    @staticmethod
    def _calc_cross_product(a, b):
        return a[0] * b[0] + a[1] * b[1]

    @staticmethod
    def _calc_segment_length(s):
        a = (s[1][0] - s[0][0], s[1][1] - s[0][1])
        return SecurityPlanner._calc_vector_length(a)

    @staticmethod
    def _calc_vector_length(a):
        return sqrt(a[0] * a[0] + a[1] * a[1])
