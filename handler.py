import datetime

import bpy

from . import generator, helper
from .preview import Preview


def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(post_ob_updated)


def unregister():
    bpy.app.handlers.depsgraph_update_post.clear()  # TODO: remove instead of clear?


@bpy.app.handlers.persistent
def post_ob_updated(scene, depsgraph):
    obj = bpy.context.object

    if obj is not None:
        if obj.mode == 'OBJECT':
            if obj.soc_object_type != 'None':
                helper.check_duplication(obj)
                handle_object_types(obj, depsgraph)


def handle_object_types(obj, depsgraph):
    if obj.soc_object_type == 'Cut':
        for u in depsgraph.updates:
            print(str(datetime.datetime.now()) + obj.name)
            if u.is_updated_geometry:
                generator.update(bpy.context, obj, reset=True)
            elif u.is_updated_transform:
                generator.transform(bpy.context, obj)
            else:
                generator.update_hide_state(bpy.context, obj)

    elif obj.soc_object_type == 'Preview':
        for u in depsgraph.updates:
            if u.is_updated_transform:
                print(datetime.datetime.now())
                print(f"Handler - preview {obj.name}")
                # return  REMOVE
                preview = Preview(bpy.context)
                preview.transform_reference(obj)
                preview.update_bounding_frame()

    elif obj.soc_object_type == 'Reference':
        pass
        # for u in depsgraph.updates:
        #     if u.is_updated_transform:
        #         Preview(bpy.context).transform_reference(obj)

    elif obj.soc_object_type == 'Bounding':
        for u in depsgraph.updates:
            if u.is_updated_transform:
                print(datetime.datetime.now())
                print(f"Handler - bounding {obj.name}")
                generator.transform_previews(bpy.context, obj)





    else:
        print(str(datetime.datetime.now()) + " Something else...: " + obj.name)
        pass
