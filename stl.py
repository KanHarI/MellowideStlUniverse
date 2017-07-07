#!/usr/bin/python3

import struct
from functools import reduce
from math import sqrt

class stl_container(object):
    """"""
    HEADER_SIZE = 80

    def __init__(self):
        self._header = b'\x00'*stl_container.HEADER_SIZE
        self._facets = []

    def add_facet(self, facet):
        self._facets.append(facet)

    def add_offset(self, offset):
        map(lambda x: x.add_offset(offset), self._facets)

    def serialize(self):
        return self._header + struct.pack("i", len(self._facets)) + b''.join(map(lambda x: x.serialize(), self._facets))

class facet(object):
    """"""
    def __init__(self, vertices):
        self._vertices = vertices
        self._normal = self.calculate_normal(vertices)
        self._attribute = b'\x00\x00'

    def calculate_normal(self, vertices):
        a = vertices[0]
        b = vertices[1]
        c = vertices[2]
        v = []
        # averaged over every 2-combination to increase accuracy
        for i in range(3):
            v.append(vector(a._y*b._z-a._z*b._y, a._z*b._x-a._x*b._z, a._x*b._y-a._y*b._x))
            (a,b,c) = (b,c,a)
        v = reduce(lambda x,y: x+y, v)
        v /= v.euclidean_size()
        return v

    def add_offset(self, offset):
        for vertix in self._vertices:
            vertix += offset
    
    def serialize(self):
        return self._normal.serialize() + b''.join(map(lambda x: x.serialize(), self._vertices)) + self._attribute

class vector(object):
    """used as either point or normal vector"""
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    def euclidean_size(self):
        return sqrt(self._x**2 + self._y**2 + self._z**2)

    def serialize(self):
        return struct.pack("fff", self._x, self._y, self._z)

    def __imul__(self, other):
        """assume other is a scalar type"""
        self._x *= other
        self._y *= other
        self._z *= other
        return self

    def __add__(self, other):
        "assume other is a vector"""
        return vector(self._x + other._x, self._y + other._y, self._z + other._z)

    def __itruediv__(self, other):
        self *= (1/other)
        return self

