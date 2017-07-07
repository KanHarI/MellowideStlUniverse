#!/ust/bin/python3

import PIL.Image as im
from math import pi, sin, cos, floor
from stl import vector

class jpg_parser(object):
    """opens a jpg image as a spherical projection"""
    def __init__(self, path, func=None):
        self._image = im.open(path)
        self._pixels = self._image.load()
        w,h = self._image.size
        if (h%2 != 0) or (w%2 != 0):
            raise Exception("Image not suitable - odd number of pixels in either dimensions")
        self._radius = min(h//2,w//4)
        self._max_angular_resolution = (pi/self._radius)*2 # factor 4, better safe then sorry
        self._center = (h//2, w//2)
        if func is None:
            self._func = (lambda x:x)
        else:
            self._func = func

    def read_pixel(self, alpha, theta, d_a, d_t):
        """alpha in [-pi/2, pi/2], theta in [-pi, pi]"""
        n_reads = 0
        result = vector(0,0,0)
        a_it = alpha

        # assume squarish behaviour
        while a_it <= alpha + d_a:
            t_it = theta
            while t_it <= theta + d_t:
                result += self._read_pixel_single(a_it,t_it)
                t_it += self._max_angular_resolution
                n_reads += 1
            a_it += self._max_angular_resolution
        result /= n_reads
        return self._func(result)
        
    def _read_pixel_single(self, alpha, theta):
        h,w = (sin(alpha)*cos(theta/2), 2*cos(alpha)*sin(theta/2))
        h *= self._radius
        w *= self._radius
        h += self._center[0]
        w += self._center[1]
        h,w = (floor(h), floor(w))
        global min_h
        global min_w
        global max_h
        global max_w
        if h < min_h:
            min_h = h
        if w < min_w:
            min_w = w
        if h > max_h:
            max_h = h
        if w > max_w:
            max_w = w
        print(h,w,min_h,min_w,max_h,max_w)
        # luckily pixels is a 3-vector
        return vector(*self._pixels[w,h])

min_h = 1000
max_h = 0
min_w = 1000
max_w = 0
