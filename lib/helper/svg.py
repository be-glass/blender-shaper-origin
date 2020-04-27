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

from ..constant import SO_CUT_ENCODING


def svg_material_attributes(key):
    style_map = {
        'Exterior': 'Exterior',
        'Interior': 'Interior',
        'Online': 'Online',
        'Pocket': 'Pocket',
        'Cutout': 'Pocket',
        'Perimeter': 'Exterior',
        'GuideArea': 'Guide',
        'GuidePath': 'Guide',
    }

    style = style_map[key]
    (stroke, fill) = SO_CUT_ENCODING[style]
    return f'stroke="{stroke}" fill="{fill}"'
