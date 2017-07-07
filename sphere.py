#!/usr/bin/python3

import stl
from math import pi, sin, cos, sqrt
from jpgParser import jpg_parser
from random import random

class sphere(object):
    """create a shpere around 0,0,0"""
    def __init__(self, r, angel_steps, func=None):
        self._stl_cont = stl.stl_container()
        self._r = r
        self._angel_steps = angel_steps
        if func is None:
            self._func = (lambda *x:1.0)
        else:
            self._func = func
        for i in range(angel_steps):
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
    s1 = sphere(r, angel_steps, func).get_cont()
    # radius is negative => normal points inside
    negative_radius_of_internall_wall = thickness - r
    s2 = sphere(negative_radius_of_internall_wall, angel_steps).get_cont()
    # offset to keep all points non-negative
    offset = stl.vector(r,r,r)
    s1.add_offset(offset)
    s2.add_offset(offset)
    s1.add_cont(s2)
    return s1
    

def main():
    # translating vector to pixel: _x == R, _y == G, _z == B
    def color_to_bool(color):
        r = color._x
        g = color._y
        b = color._z
        if (g>200): # we are on white!
            raise Exception("Image parsing error!")
        return r>b

    image = jpg_parser("CBR.jpg", color_to_bool)
    f1 = lambda *args: 0.99 if image.read_pixel(*args) else 1.01
    f2 = lambda *args: 0.99 if not image.read_pixel(*args) else 1.01
    s = create_hollow_sphere(20, 500, 4, f1)
    open("out1.stl", 'wb').write(s.serialize())
    s = create_hollow_sphere(20, 500, 4, f2)
    open("out2.stl", 'wb').write(s.serialize())

    
main()

