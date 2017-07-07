#!/ust/bin/python3

import PIL.Image as im
from math import pi, sin, cos, floor, sqrt
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
        self._phi_results = {}
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
        w,h = self._mellowide_projection(alpha, theta)
        h *= (self._radius - 1)
        w *= (self._radius - 1)
        h += self._center[0]
        w += self._center[1]
        h,w = (floor(h), floor(w))
        # global min_h
        # global min_w
        # global max_h
        # global max_w
        # if h < min_h:
        #     min_h = h
        # if w < min_w:
        #     min_w = w
        # if h > max_h:
        #     max_h = h
        # if w > max_w:
        #     max_w = w
        # print("") # new line
        # print("h range:", h,min_h,max_h)
        # print("w range:", w,min_w,max_w)
        # print("alpha, theta:", alpha, theta)
        # luckily pixels is a 3-vector
        result = vector(*self._pixels[w,h])
        return result


    # calculating using Newton–Raphson iteration (see wikipedia)
    def _mellowide_projection(self, alpha, theta, epsillon=1e-12):
        if alpha in self._phi_results.keys():
            phi = self._phi_results[alpha]
        else:
            phi = self._mellowide_calc_phi(alpha, epsillon)
            self._phi_results[alpha] = phi
        if (theta > pi):
            theta -= 2*pi
        x = 2/pi*theta*cos(phi)
        y = sin(phi)
        #print("phi", phi)
        return (x,y)


    def _mellowide_calc_phi(self, alpha, epsillon):
        if abs(abs(alpha) - pi/2) < epsillon:
            return alpha
        phi = alpha
        while True:
            old_phi = phi
            phi = old_phi - (2*old_phi + sin(2*old_phi) - pi*sin(alpha))/(2 + 2*cos(2*old_phi))
            if (abs(old_phi - phi) < epsillon):
                return phi

# min_h = 1000
# max_h = 0
# min_w = 1000
# max_w = 0
