#   This file is part of Blender_Shaper_Origin.
#  #
#   Blender_Shaper_Origin is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  #
#   Blender_Shaper_Origin is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with Blender_Shaper_Origin.  If not, see <https://www.gnu.org/licenses/>.
#

import bpy
from mathutils import Matrix, Vector
from typing import List, Tuple

from .reference import Reference
from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..helper.mesh_helper import create_object, polygon2mesh
from ..helper.other import length, remove_object, get_object_safely
from ..shape.perimeter import Perimeter

BOUNDING_FRAME_NAME = PREFIX + 'Bounding Frame'


class Bounding:

    def __init__(self) -> None:
        self.compartment = Compartment.by_enum(Collect.Internal)
        self.name = BOUNDING_FRAME_NAME
        self.frame = bpy.data.objects[self.name] if self.name in bpy.data.objects.keys() else None

    def reset(self) -> None:
        quad = self.boundary_quad()
        mesh = polygon2mesh(quad)

        if self.frame:
            self.frame.data = mesh
        else:
            self.frame = bpy.data.objects.new(self.name, mesh)
            self.compartment.link_obj(self.frame)
            self.frame.soc_object_type = "Bounding"

        self.frame.hide_set(False)

    def transform(self) -> None:
        from .preview import Preview

        frame_mw = Bounding().matrix()
        self.reset()
        for perimeter in Perimeter.all():

            reference = Reference(perimeter)

            for preview_obj in perimeter.objects():
                preview = Preview.find(preview_obj, bounding=self)
                preview.transform_others(perimeter.matrix().inverted(), reference.matrix(), self.matrix())

    def hide(self) -> None:
        self.frame.hide_set(True)

    def matrix_inverted(self) -> Matrix:
        return self.frame.matrix_world.inverted()

    def matrix(self) -> Matrix:
        return self.frame.matrix_world.copy()

    # private

    def old_matrix(self) -> Matrix:
        if BOUNDING_FRAME_NAME in bpy.data.objects.keys():
            return bpy.data.objects[BOUNDING_FRAME_NAME].matrix_world.copy()
        else:
            return Matrix()

    def boundary_quad(self) -> List[Vector]:
        z = -0.1
        d = length('10mm')  # margin of preview sheet
        c0, c1 = boundaries()

        m0 = Vector([c1.x + d, c0.y - d, z])
        m1 = Vector([c1.x + d, c1.y + d, z])
        m2 = Vector([c0.x - d, c1.y + d, z])
        m3 = Vector([c0.x - d, c0.y - d, z])

        return [m0, m1, m2, m3]


# static

def boundaries() -> Tuple[Vector, Vector]:
    x = []
    y = []
    z = []

    for perimeter in Perimeter.all():

        reference = Reference(perimeter)
        user = reference.matrix()

        for obj in perimeter.objects():

            scale = Matrix.Diagonal(perimeter.matrix().to_scale()).to_4x4()

            bb = obj.bound_box
            for p in range(8):
                v_local = perimeter.matrix_1() @ obj.matrix_world @ Vector([bb[p][0], bb[p][1], bb[p][2]])

                v = user @ scale @ v_local

                x.append(v[0])
                y.append(v[1])
                z.append(v[2])

    minimum = Vector([min(x), min(y), min(z)])
    maximum = Vector([max(x), max(y), max(z)])
    return minimum, maximum
