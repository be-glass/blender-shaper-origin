import bpy
from mathutils import Matrix, Vector

from .constant import FACE_COLOR
from . import helper, gen_helper
from .helper import length, add_plane, get_preview_collection, select_active, apply_scale





class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.perimeters = [o for o in bpy.data.objects if
                           o.soc_object_type == 'Cut' and o.soc_mesh_cut_type == 'Perimeter']
        self.bounding = self.get_bounding_frame()

    def get_bounding_frame(self):
        name = 'Bounding Frame'
        if name in bpy.data.objects.keys():
            return bpy.data.objects[name]
        else:
            return None

    def create(self):
        if self.perimeters:
            self.bounding = self.update_bounding_frame()
            self.add_objects()
        else:
            self.bounding = None
        self.set_viewport()

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
        collection = helper.get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            search[0].hide_set(True)

    def update_bounding_frame(self):
        collection = helper.get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            mw = search[0].matrix_world.copy()
            bpy.data.objects.remove(search[0])
        else:
            mw = Matrix()

        c0, c1 = helper.boundaries(self.context, self.perimeters)

        z = -0.1
        d = length(self.context, '10mm')  # margin of preview sheet

        m0 = Vector([c1.x + d, c0.y - d, z])
        m1 = Vector([c1.x + d, c1.y + d, z])
        m2 = Vector([c0.x - d, c1.y + d, z])
        m3 = Vector([c0.x - d, c0.y - d, z])

        quad = [m0, m1, m2, m3]

        frame = helper.create_object(collection, quad, "Bounding Frame")
        frame.matrix_world = mw
        frame.soc_object_type = "Bounding"
        return frame

    def add_objects(self):
        for perimeter in self.perimeters:
            self.add_object(perimeter)

    def add_object(self, cut_obj):

        if cut_obj.soc_preview_name:
            name = cut_obj.soc_preview_name
        else:
            name = cut_obj.name + '.preview'

        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name])

        q = cut_obj.copy()
        q.data = cut_obj.data.copy()
        self.collection.objects.link(q)
        helper.apply_scale(self.context, q)

        reference = gen_helper.get_reference(self.context, cut_obj)

        m = reference.matrix_world @ self.bounding.matrix_world

        q.matrix_world = m
        q.name = name
        cut_obj.soc_preview_name = q.name
        q.soc_known_as = q.name
        q.soc_object_type = 'Preview'
        q.display_type = 'TEXTURED'

        q.color = FACE_COLOR[cut_obj.soc_mesh_cut_type]

        return q

    def transform_reference(self, preview_obj):
        matches = [o for o in bpy.data.objects if o.soc_preview_name == preview_obj.name]
        if matches:
            obj = matches[0]

            reference_obj = gen_helper.get_reference(self.context, obj)

            # reference_obj = helper.get_object_safely(obj.soc_reference_name, report_error=False)

            if reference_obj is not None:
                frame_1 = self.bounding.matrix_world.copy()
                frame_1.invert()

                reference_obj.matrix_world = frame_1 @ preview_obj.matrix_world
                reference_obj.location.z = 0
