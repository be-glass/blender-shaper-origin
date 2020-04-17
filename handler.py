import bpy

from . import generator


def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(post_ob_updated)


def unregister():
    bpy.app.handlers.depsgraph_update_post.clear()  # TODO: remove instead of clear?


@bpy.app.handlers.persistent
def post_ob_updated(scene, depsgraph):
    obj = bpy.context.object
    if obj is not None:
        if obj.soc_object_type != 'None':
        # if obj.soc_mesh_cut_type != 'None' or obj.soc_curve_cut_type != 'None':
            for u in depsgraph.updates:
                if u.is_updated_geometry:
                    generator.update(bpy.context, obj, reset=True)
                if u.is_updated_transform:
                    generator.transform(bpy.context, obj)


