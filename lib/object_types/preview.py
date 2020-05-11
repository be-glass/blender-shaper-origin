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

from typing import TypeVar, Union

import bpy
from bpy.types import Object, BlendDataObjects
from mathutils import Vector, Matrix

from .bounding import Bounding
from .reference import Reference
from ..blender.compartment import Compartment, Collect
from ..blender.fillet import Fillet
from ..blender.project import Project
from ..constant import PREVIEW_STACK_DELTA, FACE_COLOR, PREFIX
from ..helper.other import length, warning_msg, remove_object, find_first_perimeter, set_viewport, z_lift
from ..shape.perimeter import Perimeter

T = TypeVar('T', bound='Preview')


class Preview:

    def __init__(self, obj=None, bounding=None) -> None:
        self.obj = obj
        self.compartment = Compartment.by_enum(Collect.Preview)
        self.bounding = bounding if bounding else Bounding()
        self.cut_obj = None
        self.name = None
        if obj:
            self.cut_obj = self.find_cut_obj(obj.name)
            self.name = self.get_name()

    def setup(self, cut_obj) -> None:
        self.cut_obj = cut_obj
        self.name = self.get_name()
        self.add_object()
        self.cut_obj.soc_preview_name = self.obj.name

    @classmethod
    def find(cls, cut_obj, bounding=None) -> Union[T, None]:
        name = cut_obj.soc_preview_name
        if name:
            if name in bpy.data.objects.keys():
                obj = bpy.data.objects[name]
                return cls(obj, bounding=bounding)
        return None

    @classmethod
    def add(cls, cut_obj) -> None:
        Preview().setup(cut_obj)

    def get_name(self) -> str:
        return PREFIX + self.cut_obj.name + '.preview'

    def transform_others(self, perimeter_mw_1, reference_mw, frame_mw) -> None:
        if self.obj:
            self.obj.matrix_world = frame_mw \
                                    @ reference_mw \
                                    @ self.lift() \
                                    @ perimeter_mw_1 \
                                    @ self.cut_obj.matrix_world


    # private

    def find_cut_obj(self, name) -> Union[BlendDataObjects, None]:
        match = [o for o in Project.cut_objs() if o.soc_preview_name == name]
        if match:
            return match[0]
        else:
            return None

    def lift(self) -> Matrix:
        zlift = z_lift(self.cut_obj)
        lift = Vector([0, 0, zlift * length(PREVIEW_STACK_DELTA)])
        return Matrix.Translation(lift)

    def transform(self) -> None:

        if self.cut_obj.soc_mesh_cut_type == 'Perimeter':
            perimeter = Perimeter(self.cut_obj)

            reference = Reference(perimeter)
            self.transform_reference(reference)
            bounding = Bounding()

            for obj in perimeter.sibling_objs():
                preview = Preview()
                preview.setup(obj)
                preview.transform_others(
                    perimeter.matrix().inverted(),
                    reference.matrix(),
                    bounding.matrix()
                )

            bounding.reset()  # TODO: should it go above?

    def add_object(self) -> None:
        check_scale(self.cut_obj)
        remove_object(self.name)
        self.obj = create_preview_object(self.cut_obj)
        self.compartment.move(self.obj)

        if self.cut_obj.soc_mesh_cut_type != 'Perimeter':
            self.obj.hide_select = True

        # apply_mesh_scale(self.preview_obj)    # TODO: is this needed? for mesh? for curve?

        perimeter = Perimeter(find_first_perimeter(self.cut_obj))

        self.transform_others(perimeter.matrix().inverted(), Reference(perimeter).matrix(), self.bounding.matrix())
        self.configure()

    def configure(self) -> None:
        o = self.obj
        o.name = self.name
        o.soc_preview_name = ""
        o.soc_known_as = self.name
        o.soc_object_type = 'Preview'
        o.display_type = 'TEXTURED'

        mct = self.cut_obj.soc_mesh_cut_type
        cct = self.cut_obj.soc_curve_cut_type

        if mct != 'None':
            o.color = FACE_COLOR[mct]
            # o.soc_mesh_cut_type = mct   # TODO:   enable this line  (it's causing a recursion loop)
            pass

        elif cct != 'None':
            o.color = FACE_COLOR[cct]
            o.soc_curve_cut_type = cct

    def transform_reference(self, reference) -> None:
        obj = reference.get()
        obj.matrix_world = Bounding().matrix_inverted() @ self.obj.matrix_world
        obj.location.z = 0

    def remove(self) -> None:
        if self.name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[self.name])

    @classmethod
    def create(cls) -> None:
        bounding = Bounding()
        perimeters = Perimeter.all()
        if perimeters:
            bounding.reset()

            for perimeter in perimeters:
                for shape in perimeter.shapes():
                    cls.add(shape.obj)

            set_viewport()
        else:
            bounding.hide()

    @classmethod
    def delete(self) -> None:

        objs = Project.cut_objs()
        for o in objs:
            remove_object(o.soc_preview_name)
            o.soc_preview_name = ""
        Bounding().hide()


def check_scale(cut_obj) -> None:
    if cut_obj.scale != Vector([1, 1, 1]):
        warning_msg(
            f'Please apply scale to object "{cut_obj.name}" to avoid unexpected results in preview and export!')


def create_preview_object(cut_obj) -> Object:
    if cut_obj.type == 'MESH':
        is_perimeter = True if cut_obj.soc_mesh_cut_type == 'Perimeter' else False
        fillet = Fillet(cut_obj)  # TODO: is this ok? what was cut_obj1 ? 
        obj = fillet.create(rounded=False, outside=is_perimeter)

    else:
        obj = cut_obj.copy()
        obj.data = cut_obj.data.copy()
        obj.soc_object_type = 'Preview'
        obj.soc_curve_cut_type = cut_obj.soc_curve_cut_type
    return obj
