#!/usr/bin/python3

import stl
from math import pi, sin, cos, sqrt
from inverseMellowide import inverse_mellowide_jpg


class voxel_half_sphere(object):
    def __init__(self, r, width, angel_steps, tmp_files, alpha_0=-pi/2, func=None, transform=None):
        self._stl_cont_red = stl.stl_container(tmp_files[0])
        self._stl_cont_blue = stl.stl_container(tmp_files[1])
        self._r = r
        self._r_int = r - width
        self._angel_steps = angel_steps
        self._func = (lambda *args: 1) if (func is None) else func
        self._transform = (lambda x: x) if (transform is None) else transform

        for i in range(angel_steps//2):
            print ("%d of %d", i, angel_steps)
            alpha = alpha_0 + i*pi/angel_steps
            for j in range(angel_steps*2):
                theta = j*pi/angel_steps - pi
                red_red_height = self._func(alpha, theta, pi/angel_steps, pi/angel_steps)

                pts = [None]*12
                for i in range(12):
                    cur_r = r if i < 6 else self._r_int
                    cur_alpha = alpha if (i%6) < 2 else ((alpha + red_red_height*pi/angel_steps) if (i%6) < 4 else (alpha + pi/angel_steps))
                    cur_theta = theta if (i%2) == 0 else (theta + pi/angel_steps)
                    pts[i] = self.gen_point(cur_r, cur_alpha, cur_theta)

                pts = list(map(self._transform, pts))

                if (red_red_height > 0):
                    self._stl_cont_red.add_cube((pts[0], pts[1], pts[2], pts[3], pts[6], pts[7], pts[8], pts[9]))
                if (red_red_height < 1):
                    self._stl_cont_blue.add_cube((pts[2], pts[3], pts[4], pts[5], pts[8], pts[9], pts[10], pts[11]))

                self._stl_cont_red.flush()
                self._stl_cont_blue.flush()


    def gen_point(self, r, alpha, theta):
        if (alpha == -pi/2):
            return stl.vector(0,0,-self._r)
        if (alpha == pi/2):
            return stl.vector(0,0,self._r)
        x = r*cos(theta)*cos(alpha)
        y = r*sin(theta)*cos(alpha)
        z = r*sin(alpha)
        return stl.vector(x,y,z)


    def serialize(self, out_red, out_blue):
        open(out_red, 'wb').write(self._stl_cont_red.serialize())
        open(out_blue, 'wb').write(self._stl_cont_blue.serialize())


def main():
        # translating vector to pixel: _x == R, _y == G, _z == B
    def color_to_int(color):
        r = color._x
        g = color._y
        b = color._z
        if (g>250): # we are on white!
            raise Exception("Image parsing error!")
            pass
        return (r-b)


    image = inverse_mellowide_jpg("CBR2.jpg", color_to_int)

    
    global main_cache
    global main_below
    global main_above

    main_below = 0
    main_above = 0
    threshold = -135
    main_cache = {}

    def cached_image_read_pixel(*args):
        global main_cache
        global main_below
        global main_above
        if args in main_cache.keys():
            return main_cache[args]
        result = image.read_pixel(*args)
        if result < threshold:
            main_below += 1
            result = 0
        else:
            main_above += 1
            result = 1
        main_cache[args] = result
        return result


    resolution = 500
    vhs = voxel_half_sphere(50, 1, resolution, ("tmp1", "tmp2"), -pi/2, cached_image_read_pixel)
    vhs.serialize("red.low.%s.stl" % (resolution,), "blue.low.%s.stl" % (resolution,))

    def trans(p):
        x = p._x
        y = -p._y
        z = -p._z
        return stl.vector(x,y,z)


    vhs = voxel_half_sphere(50, 1, resolution, ("tmp1", "tmp2"), 0, cached_image_read_pixel, trans)
    vhs.serialize("red.high.%s.stl" % (resolution,), "blue.high.%s.stl" % (resolution,))

    print("_below, _above", main_below, main_above, "AROUND: ", threshold)

main()
