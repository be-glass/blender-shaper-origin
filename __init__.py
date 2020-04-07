from . import ui, properties, operators

# https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo

bl_info = {
    "name": "SO Cutting Toolbox",
    "author": "Boris Glass 8)",
    "blender": (2, 80, 0),
    "version": (0, 0, 4),
    "location": "3D View > Sidebar",
    "description": "SVG Export Utilities for cutting lines",
    # "wiki_url": "https://docs.blender.org/manual/en/dev/addons/mesh/3d_print_toolbox.html",
    # "support": 'OFFICIAL',
    "category": "Mesh",
}

files = [ui, properties, operators]

operators.bl_info = bl_info


def register():
    [file.register() for file in files]

    # reg_handlers()


def unregister():
    [file.unregister() for file in files]
    # unreg_handlers()


import bpy




# def reg_handlers():
#     bpy.app.handlers.depsgraph_update_pre.clear()
#     bpy.app.handlers.depsgraph_update_post.clear()
#
#
# def unreg_handlers():
#
#     bpy.app.handlers.depsgraph_update_pre.append(pre_ob_updated)
#     bpy.app.handlers.depsgraph_update_pre.append(pre_ob_updated_data)
#     bpy.app.handlers.depsgraph_update_pre.append(pre_ob_data_updated)
#     bpy.app.handlers.depsgraph_update_pre.append(pre_ob_data_updated_data)
#     bpy.app.handlers.depsgraph_update_post.append(post_ob_updated)
#     bpy.app.handlers.depsgraph_update_post.append(post_ob_updated_data)
#     bpy.app.handlers.depsgraph_update_post.append(post_ob_data_updated)
#     bpy.app.handlers.depsgraph_update_post.append(post_ob_data_updated_data)
#
#
#
#
#
#
#
#
# # https://www.blender.org/forum/viewtopic.php?t=27498
#
#
# def pre_ob_updated(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.is_updated:
#     #     print("%s - Object is_updated (pre)" % ob.name)
#
#
# def pre_ob_updated_data(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.is_updated_data:
#     #     print("%s - Object is_updated_data (pre)" % ob.name)
#
#
# def pre_ob_data_updated(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.data.is_updated:
#     #     print("%s - Object data is_updated (pre)" % ob.data.name)
#
#
# def pre_ob_data_updated_data(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.data.is_updated_data:
#     #     print("%s - Object data is_updated_data (pre)" % ob.data.name)
#
#
# def post_ob_updated(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.is_updated:
#     #     print("%s - Object is_updated (post)" % ob.name)
#
#
# def post_ob_updated_data(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.is_updated_data:
#     #     print("%s - Object is_updated_data (post)" % ob.name)
#
#
# def post_ob_data_updated(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.data.is_updated:
#     #     print("%s - Object data is_updated (post)" % ob.data.name)
#
#
# def post_ob_data_updated_data(*args, **kwargs):
#     pass
#     # ob = scene.objects.active
#     # if ob is not None and ob.data.is_updated_data:
#     #     print("%s - Object data is_updated_data (post)" % ob.data.name)
#

