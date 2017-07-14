#!/usr/bin/python3

import stl
from math import pi, sin, cos, sqrt
from jpgParser import jpg_parser


class sphere(object):
    """create a shpere around 0,0,0"""
    def __init__(self, r, angel_steps, tmp_file, func=None):
        self._stl_cont = stl.stl_container(tmp_file)
        self._r = r
        self._angel_steps = angel_steps
        if func is None:
            self._func = (lambda *x:1.0)
        else:
            self._func = func
        for i in range(angel_steps):
            print("%d of %d" % (i, angel_steps))
            for j in range(angel_steps*2):
                try:
                    self._stl_cont.add_facet(
                        stl.facet(
                            (self.gen_point(self.gen_lat(i), self.gen_long(j)),
                            self.gen_point(self.gen_lat(i), self.gen_long(j+1)),
                            self.gen_point(self.gen_lat(i+1), self.gen_long(j+1)))
                        )
                    )
                except ZeroDivisionError as e:
                    # we do not need 2 facets near top and button, this catches
                    # an exception thrown from the calculation of a normal to a
                    # "facet" of size 0
                    pass
                try:
                    self._stl_cont.add_facet(
                        stl.facet(
                            (self.gen_point(self.gen_lat(i), self.gen_long(j)),
                            self.gen_point(self.gen_lat(i+1), self.gen_long(j+1)),
                            self.gen_point(self.gen_lat(i+1), self.gen_long(j)))
                        )
                    )
                except ZeroDivisionError as e:
                    pass
            self._stl_cont.flush()


    def gen_lat(self, step):
        alpha = pi*step/self._angel_steps - pi/2
        if (step == self._angel_steps):
        # verify "nice" behaviour in edge
            alpha = pi/2
        return alpha


    def gen_long(self, step):
        theta = 2*pi*step/(self._angel_steps*2) - pi
        # verify "nice" behaviour in edge
        if (step == self._angel_steps*2):
            theta = pi
        return theta


    def gen_point(self, alpha, theta):
        # verify a singular point in edge
        if (alpha == -pi/2):
            return stl.vector(0,0,-self._r)
        if (alpha == pi/2):
            return stl.vector(0,0,self._r)
        r = self._r*self._func(alpha, theta, pi/self._angel_steps, pi/self._angel_steps)
        x = r*cos(theta)*cos(alpha)
        y = r*sin(theta)*cos(alpha)
        z = r*sin(alpha)
        return stl.vector(x,y,z)


    def get_cont(self):
        return self._stl_cont

        

def create_hollow_sphere(r, angel_steps, thickness, func=None):
    s1 = sphere(r, angel_steps, "tmp1.tmp", func).get_cont()
    # radius is negative => normal points inside
    negative_radius_of_internall_wall = thickness - r
    s2 = sphere(negative_radius_of_internall_wall, angel_steps, "tmp2.tmp").get_cont()
    s1.add_cont(s2)
    return s1
    

def main():
    # translating vector to pixel: _x == R, _y == G, _z == B
    def color_to_bool(color):
        r = color._x
        g = color._y
        b = color._z
        if (g>250): # we are on white!
            raise Exception("Image parsing error!")
            pass
        return r+g>b

    image = jpg_parser("CBR2.jpg", color_to_bool)

    cache = {}
    def cached_image_read_pixel(*args):
        if args in cache.keys():
            return cache[args]
        result = image.read_pixel(*args)
        cache[args] = result
        return result

    f1 = lambda *args: 0.995 if cached_image_read_pixel(*args) else 1.005
    f2 = lambda *args: 0.995 if not cached_image_read_pixel(*args) else 1.005
    s = create_hollow_sphere(50, 500, 1, f1)
    open("out1.stl", 'wb').write(s.serialize())
    s = create_hollow_sphere(50, 500, 1, f2)
    open("out2.stl", 'wb').write(s.serialize())

    
main()

