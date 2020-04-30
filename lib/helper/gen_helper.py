#  This file is part of Blender_Shaper_Origin.
#
#  Blender_Shaper_Origin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Blender_Shaper_Origin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Blender_Shaper_Origin.  If not, see <https://www.gnu.org/licenses/>.

import bpy
from mathutils import Matrix, Vector

from ..constant import PREFIX
from .other import delete_object, find_cuts, get_object_safely

from ..collection import Collection, Collect


def find_siblings_by_type(cut_types, sibling=None, collection=None):
    if not (sibling or collection):
        return []

    if not collection:
        collection = sibling.users_collection[0]

    cutables = [o for o in collection.objects if o.type in ['MESH', 'CURVE']]
    return [o for o in cutables if (o.soc_mesh_cut_type in cut_types) or (o.soc_curve_cut_type in cut_types)]


def perimeter_thickness(obj):
    perimeters = find_siblings_by_type(['Perimeter'], sibling=obj)
    if perimeters:
        return perimeters[0].soc_cut_depth
    else:
        return None




def delete_solid_objects(obj):
    solid_collection = get_solid_collection()
    for o in solid_collection.objects:
        if o.name == PREFIX + obj.name + ".fillets":
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup_meshes(mesh_name):
    solid_collection = get_solid_collection()
    for o in solid_collection.objects:
        if o.name.startswith(mesh_name):
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup(obj):
    if obj.soc_known_as != obj.name:
        return

    delete_modifiers(obj)
    delete_solid_objects(obj)
    obj.display_type = 'TEXTURED'

    cleanup_boolean_modifiers(obj)

    if obj.type == 'CURVE':
        obj.data.bevel_object = None

    delete_object(obj.soc_reference_name)
    delete_object(obj.soc_preview_name)
    delete_object(obj.soc_solid_name)
    delete_object(obj.soc_bevel_name)
    obj.soc_reference_name = ''
    obj.soc_preview_name = ''
    obj.soc_solid_name = ''
    obj.soc_bevel_name = ''




def get_reference(obj):
    collection = get_reference_collection()

    name = obj.soc_reference_name

    if not name:
        name = PREFIX + obj.users_collection[0].name + '.reference'

    if name in bpy.data.objects.keys():
        return bpy.data.objects[name]
    else:
        reference = bpy.data.objects.new(name, None)
        reference.location = obj.location
        reference.matrix_world = obj.matrix_world
        reference.matrix_world.identity()
        collection.objects.link(reference)
        reference.empty_display_size = 5
        reference.empty_display_type = 'PLAIN_AXES'
        reference.soc_object_type = 'Reference'
        obj.soc_reference_name = reference.name
        reference.hide_set(True)
        return reference


def boundaries():
    x = []
    y = []
    z = []
    for obj in find_cuts():

        reference = get_reference(obj)

        user = reference.matrix_world
        scale = Matrix.Diagonal(obj.matrix_world.to_scale()).to_4x4()

        bb = obj.bound_box
        for p in range(8):
            v_local = Vector([bb[p][0], bb[p][1], bb[p][2]])

            v = user @ scale @ v_local

            x.append(v[0])
            y.append(v[1])
            z.append(v[2])

    minimum = Vector([min(x), min(y), min(z)])
    maximum = Vector([max(x), max(y), max(z)])
    return minimum, maximum
