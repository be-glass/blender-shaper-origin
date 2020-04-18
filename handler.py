import bpy

from . import generator
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
        if obj.soc_object_type == 'Cut':
            for u in depsgraph.updates:
                if u.is_updated_geometry:
                    generator.update(bpy.context, obj, reset=True)
                if u.is_updated_transform:
                    generator.transform(bpy.context, obj)

        elif obj.soc_object_type == 'Preview':
            for u in depsgraph.updates:
                if u.is_updated_transform:
                    Preview(bpy.context).transform_reference(obj)



        elif obj.soc_object_type == 'Reference':
            pass
            # for u in depsgraph.updates:
            #     if u.is_updated_transform:
            #         Preview(bpy.context).transform_reference(obj)



        else:
            pass



