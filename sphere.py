#!/usr/bin/python3

import stl
from math import pi, sin, cos, sqrt

class sphere(object):
    """create a shpere around 0,0,0"""
    def __init__(self, r, angel_steps):
        self._stl_cont = stl.stl_container()
        self._r = r
        self._angel_steps = angel_steps
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
                    

    def gen_long(self, step):
        theta = 2*pi*step/(self._angel_steps*2)
        # verify "nice" behaviour in edge
        if (step == self._angel_steps*2):
            theta = 0
        return theta

    def gen_lat(self, step):
        alpha = pi*step/self._angel_steps - pi/2
        if (step == self._angel_steps):
        # verify "nice" behaviour in edge
            alpha = pi/2
        return alpha

    def gen_point(self, alpha, theta):
        # verify a singular point in edge
        if (alpha == -pi/2):
            return stl.vector(0,0,-self._r)
        if (alpha == pi/2):
            return stl.vector(0,0,self._r)
        x = self._r*cos(theta)*cos(alpha)
        y = self._r*sin(theta)*cos(alpha)
        z = self._r*sin(alpha)
        return stl.vector(x,y,z)


def main():
    s = sphere(10, 20)
    open("out.stl", 'wb').write(s._stl_cont.serialize())
    
main()

