import bpy
from mathutils import Vector, Matrix

from .bounding import Bounding
from .reference import Reference
from ..collection import Collection, Collect
from ..constant import PREVIEW_STACK_DELTA, STACK_Z, FACE_COLOR, PREFIX
from ..fillet import Fillet
from ..helper.other import length, warning_msg, move_object, remove_object, find_first_perimeter
from ..project import Project
from ..shape.perimeter import Perimeter


class Preview:

    def __init__(self, obj=None):
        self.obj = obj
        self.collection = Collection(Collect.Preview)
        self.bounding = Bounding()
        self.cut_obj = None
        self.name = None
        if obj:
            self.cut_obj = self.find_cut_obj(obj.name)
            self.name = PREFIX + self.cut_obj.name + '.preview'

    def setup(self, cut_obj):

        self.cut_obj = cut_obj
        self.obj = self.add_object()
        self.cut_obj.soc_preview_name = self.obj.name

    def transform_others(self, perimeter_mw_1, reference_mw, frame_mw):
        if self.obj:
            self.obj.matrix_world = frame_mw \
                                    @ reference_mw \
                                    @ self.lift() \
                                    @ perimeter_mw_1 \
                                    @ self.cut_obj.matrix_world

        def clean(self):
            if self.obj:
                bpy.data.objects.remove(self.obj)

    # private

    def find_cut_obj(self, name):
        match = [o for o in Project.cuts() if o.soc_preview_name == name]
        if match:
            return match[0]
        else:
            return None

    def lift(self):

        if self.cut_obj.soc_mesh_cut_type != 'None':
            z = STACK_Z[self.cut_obj.soc_mesh_cut_type]
        elif self.cut_obj.soc_curve_cut_type != 'None':
            z = STACK_Z[self.cut_obj.soc_curve_cut_type]
        else:
            z = 0

        lift = Vector([0, 0, z * length(PREVIEW_STACK_DELTA)])
        return Matrix.Translation(lift)

    def transform(self):

        if self.cut_obj.soc_mesh_cut_type == 'Perimeter':
            perimeter = Perimeter(self.cut_obj)

            reference = Reference(perimeter)
            reference.transform(self.obj)
            bounding = Bounding()

            for shape in perimeter.others():
                shape.transform_others(perimeter.matrix().inverted(), reference.matrix(), bounding.matrix())

            bounding.reset()  # TODO: should it go above?

    def add_object(self):

        self.check_scale()
        remove_object(self.name)

        obj = self.create_preview_object()

        move_object(obj, self.collection)
        if self.cut_obj.soc_mesh_cut_type != 'Perimeter':
            obj.hide_select = True

        # apply_mesh_scale(self.preview_obj)    # TODO: is this needed? for mesh? for curve?

        perimeter = Perimeter(find_first_perimeter(self.cut_obj))

        self.transform_others(perimeter.matrix().inverted(), perimeter.reference.matrix(), self.bounding.matrix())
        self.configure()

        return obj

    def create_preview_object(self):
        if self.cut_obj.type == 'MESH':
            is_perimeter = True if self.cut_obj.soc_mesh_cut_type == 'Perimeter' else False
            fillet = Fillet(self.cut_obj)  # TODO: is this ok? what was cut_obj1 ? 
            obj = fillet.create(reset=False, rounded=False, outside=is_perimeter)

        else:
            obj = self.cut_obj.copy()
            obj.data = self.cut_obj.data.copy()
            obj.soc_curve_cut_type = self.cut_obj.soc_curve_cut_type
        return obj

    def check_scale(self):
        if self.cut_obj.scale != Vector([1, 1, 1]):
            warning_msg(
                f'Please apply scale to object "{self.cut_obj.name}" to avoid unexpected results in preview and export!')

    def configure(self):
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
            o.soc_mesh_cut_type = mct

        elif cct != 'None':
            o.color = FACE_COLOR[cct]
            o.soc_curve_cut_type = cct
