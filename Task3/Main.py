from SecurityPlanner import SecurityPlanner
from MapProcessor import MapProcessor

class Main(object):
    def __init__(self):
        self._segments = [
            ((153, 92), (953, 92)),
            ((153, 500), (953, 500)),
            ((153, 92), (153, 500)),
            ((953, 92), (953, 500)),

            ((354, 92), (354, 173)),
            ((554, 92), (554, 173)),
            ((754, 92), (754, 173)),

            ((354, 500), (354, 335)),
            ((455, 395), (455, 335)),
            ((554, 500), (554, 275)),
            ((754, 500), (754, 335)),

            ((153, 335), (270, 335)),
            ((320, 335), (354, 335)),
            ((455, 335), (587, 335)),
            ((638, 335), (754, 335)),

            ((754, 335), (790, 315)),
            ((855, 278), (953, 218))
        ]

        self._mp = MapProcessor(Main.find_cameras, self)

    def main(self):
        # blue_points = {0: (295, 335), 1: (455, 435), 2: (615, 335), 3: (819, 297)}

        self._mp.draw_segments(self._segments)
        self._mp.show()

    def find_cameras(self):
        print('Ready!')
        sp = SecurityPlanner(self._segments, self._mp.blue_points)

        cam_pos = sp.find_cameras_positions()

        if cam_pos is not None:
            print('cam pos 1: (%d, %d)' % (cam_pos[0][0], cam_pos[0][1]))
            print('cam pos 2: (%d, %d)' % (cam_pos[1][0], cam_pos[1][1]))
            self._mp.draw_cameras(cam_pos)
        else:
            print('No solutions!')

if __name__ == "__main__":
    main = Main()
    main.main()
