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

from ..constant import PREFIX
from .other import delete_object

from ..collection import Collection, Collect
from ..modifier import Modifier


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
    for o in Collection.by_enum(Collect.Solid).objects():
        if o.name == PREFIX + obj.name + ".fillets":
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup_meshes(mesh_name):
    for o in Collection.by_enum(Collect.Solid).objects():
        if o.name.startswith(mesh_name):
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup(obj):
    if obj.soc_known_as != obj.name:
        return

    Modifier(obj).delete_all()

    delete_solid_objects(obj)
    obj.display_type = 'TEXTURED'

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
