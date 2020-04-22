import bpy
from mathutils import Matrix, Vector

from .constant import FACE_COLOR
from .helper.gen_helper import get_reference, boundaries
from .helper.preview_helper import transform_preview
from .helper.mesh import apply_mesh_scale, create_object
from .helper.other import (
    length, get_preview_collection, find_cuts, get_soc_collection, warning_msg, get_object_safely
)


class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.bounding = self.get_bounding_frame()
        self.cut_objs = find_cuts()
        self.perimeters = [o for o in self.cut_objs if o.soc_mesh_cut_type == 'Perimeter']

    def get_bounding_frame(self):
        name = 'Bounding Frame'
        if name in bpy.data.objects.keys():
            return bpy.data.objects[name]
        else:
            return None

    def create(self):
        if self.perimeters:
            self.bounding = self.update_bounding_frame()

            for perimeter in self.perimeters:
                for obj in perimeter.users_collection[0].objects:
                    self.add_object(perimeter, obj)

            self.set_viewport()
        else:
            self.bounding = None

    def set_viewport(self):
        for area in self.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'OBJECT'

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)
        self.hide_bounding_frame()

    def hide_bounding_frame(self):
        collection = get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            search[0].hide_set(True)

    def update_bounding_frame(self):
        collection = get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            mw = search[0].matrix_world.copy()
            bpy.data.objects.remove(search[0])
        else:
            mw = Matrix()

        c0, c1 = boundaries(self.context, self.perimeters)

        z = -0.1
        d = length(self.context, '10mm')  # margin of preview sheet

        m0 = Vector([c1.x + d, c0.y - d, z])
        m1 = Vector([c1.x + d, c1.y + d, z])
        m2 = Vector([c0.x - d, c1.y + d, z])
        m3 = Vector([c0.x - d, c0.y - d, z])

        quad = [m0, m1, m2, m3]

        frame = create_object(quad, collection, "Bounding Frame")
        frame.matrix_world = mw
        frame.soc_object_type = "Bounding"
        return frame

    def add_object(self, perimeter, cut_obj):

        if cut_obj.scale != Vector([1, 1, 1]):
            warning_msg(
                f'Please apply scale to object "{cut_obj.name}" to avoid unexpected results in preview and export!')

        if cut_obj.soc_preview_name:
            name = cut_obj.soc_preview_name
        else:
            name = cut_obj.name + '.preview'

        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name])

        preview_obj = cut_obj.copy()
        preview_obj.data = cut_obj.data.copy()
        self.collection.objects.link(preview_obj)

        # apply_mesh_scale(self.context, preview_obj)    # TODO: is this needed? for mesh? for curve?

        preview_obj.matrix_world = transform_preview(self.context, self.bounding, perimeter, cut_obj)
        preview_obj.name = name
        cut_obj.soc_preview_name = preview_obj.name
        preview_obj.soc_preview_name = ""
        preview_obj.soc_known_as = preview_obj.name
        preview_obj.soc_object_type = 'Preview'
        preview_obj.display_type = 'TEXTURED'

        if cut_obj.soc_mesh_cut_type != 'None':
            preview_obj.color = FACE_COLOR[cut_obj.soc_mesh_cut_type]
        elif cut_obj.soc_curve_cut_type != 'None':
            preview_obj.color = FACE_COLOR[cut_obj.soc_curve_cut_type]

        return preview_obj

    def transform_reference(self, preview_obj):
        matches = [o for o in bpy.data.objects if o.soc_preview_name == preview_obj.name]
        if matches:
            obj = matches[0]

            reference_obj = get_reference(self.context, obj)

            if reference_obj is not None:
                frame_1 = self.bounding.matrix_world.copy()
                frame_1.invert()
                # frame_1 = self.bounding.matrix_world.inverted()

                reference_obj.matrix_world = frame_1 @ preview_obj.matrix_world
                reference_obj.location.z = 0

    def transform_siblings(self, perimeter_preview):

        perimeters = [o for o in bpy.data.objects if o.soc_preview_name == perimeter_preview.name]
        if not perimeters:
            return
        perimeter = perimeters[0]

        for obj in perimeter.users_collection[0].objects:
            if obj.soc_mesh_cut_type != 'Perimeter':
                m = transform_preview(self.context, self.bounding, perimeter, obj)
                preview_obj = get_object_safely(obj.soc_preview_name)
                preview_obj.matrix_world = m

    def transform_previews(self, context, frame_obj):

        for perimeter in self.perimeters:
            for obj in perimeter.users_collection[0].objects:

                if obj.soc_object_type == 'Cut':
                    matrix = transform_preview(context, frame_obj, perimeter, obj)
                    preview_obj = get_object_safely(obj.soc_preview_name)
                    preview_obj.matrix_world = matrix
