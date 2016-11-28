import matplotlib.pyplot as plt
import numpy as np
import skimage
from skimage.draw import line

class MapProcessor(object):
    def __init__(self, callback, main):
        self.img = np.ndarray((650, 1100, 3), np.dtype('uint8'))
        self.img.fill(255)
        self._fig = plt.figure(figsize=(20, 10))
        self._ax = self._fig.gca()
        self._cid = self._fig.canvas.mpl_connect('button_press_event', self.__onclick__)
        self._max_blue_points_count = 4
        self.blue_points = {}
        self._callback = callback
        self._main = main

    def draw_segments(self, segments):
        for s in segments:
            rr, cc = line(s[0][1], s[0][0], s[1][1], s[1][0])
            self.img[rr, cc, :] = 0

    def draw_cameras(self, points):
        for p in points:
            self._ax.plot(p[0], p[1], 'ro')
            self._fig.canvas.draw()

    def show(self):
        plt.imshow(self.img)
        plt.show()

    def __onclick__(self, click):
        point = (click.xdata, click.ydata)
        print(point)
        self._ax.plot(point[0], point[1], 'bo')
        self._fig.canvas.draw()
        self.blue_points[len(self.blue_points)] = point
        if len(self.blue_points) >= self._max_blue_points_count:
            self._fig.canvas.mpl_disconnect(self._cid)
            print(self.blue_points)
            self._callback(self._main)
