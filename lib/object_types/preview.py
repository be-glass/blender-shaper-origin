import bpy
from mathutils import Vector, Matrix

from .bounding import Bounding
from .reference import Reference
from ..constant import PREVIEW_STACK_DELTA, STACK_Z, FACE_COLOR, PREFIX
from ..blender.compartment import Compartment, Collect
from ..blender.project import Project
from ..blender.fillet import Fillet
from ..helper.other import length, warning_msg, move_obj, remove_object, find_first_perimeter, set_viewport
from ..shape.perimeter import Perimeter


class Preview:

    def __init__(self, obj=None):
        self.obj = obj
        self.compartment = Compartment.by_enum(Collect.Preview)
        self.bounding = Bounding()
        self.cut_obj = None
        self.name = None
        if obj:
            self.cut_obj = self.find_cut_obj(obj.name)
            self.name = PREFIX + self.cut_obj.name + '.preview'

    @classmethod
    def add(cls, cut_obj):
        Preview().setup(cut_obj)

    def setup(self, cut_obj):
        self.cut_obj = cut_obj
        self.name = PREFIX + self.cut_obj.name + '.preview'
        self.add_object()
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
            transform_reference(reference)
            bounding = Bounding()

            for shape in perimeter.others():
                shape.transform_others(perimeter.matrix().inverted(), reference.matrix(), bounding.matrix())

            bounding.reset()  # TODO: should it go above?

    def add_object(self):
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
            # o.soc_mesh_cut_type = mct   # TODO:   enable this line  (it's causing a recursion loop)
            pass

        elif cct != 'None':
            o.color = FACE_COLOR[cct]
            o.soc_curve_cut_type = cct

    def transform_reference(self, reference):
        obj = reference.get()
        obj.matrix_world = Bounding().matrix_inverted() @ self.obj.matrix_world
        obj.location.z = 0

    @classmethod
    def create(cls):
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

    def delete(self):
        for obj in self.compartment.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.compartment)
        self.bounding.hide()
    #
    #
    # def matrix_ref_bound(self, perimeter_mw, bounding_mw):
    #
    #     reference_mw = Reference(perimeter)
    #
    #     m3 = reference.matrix_world if reference else Matrix()
    #     m4 = bounding_mw if bounding_mw else Matrix()
    #
    #     return m4 @ m3


def check_scale(cut_obj):
    if cut_obj.scale != Vector([1, 1, 1]):
        warning_msg(
            f'Please apply scale to object "{cut_obj.name}" to avoid unexpected results in preview and export!')


def create_preview_object(cut_obj):
    if cut_obj.type == 'MESH':
        is_perimeter = True if cut_obj.soc_mesh_cut_type == 'Perimeter' else False
        fillet = Fillet(cut_obj)  # TODO: is this ok? what was cut_obj1 ? 
        obj = fillet.create(rounded=False, outside=is_perimeter)

    else:
        obj = cut_obj.copy()
        obj.data = cut_obj.data.copy()
        obj.soc_curve_cut_type = cut_obj.soc_curve_cut_type
    return obj
