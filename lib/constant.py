PREFIX = "SOC_"

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

# sheet_name = prefix + "Work Area"

FACE_COLOR = {
    'Cutout': (1, 1, 1, 1),
    'Perimeter': (0, 0, 0, 1),
    'Pocket': (.5, .5, .5, 1),
    'Guide': (0, 0, 1, 1),
    'Exterior': (0, 1, 1, 1),
    'Online': (1, 0, 1, 1),
    'Interior': (1, 1, 0, 1),
}

STACK_Z = {
    'Guide': 6,
    'Cutout': 5,
    'Pocket': 4,
    'Interior': 3,
    'Exterior': 2,
    'Online': 1,
    'Perimeter': 0,
}
PREVIEW_STACK_DELTA = "0.1 mm"

CUT_ENCODING = {'Interior': ('black', 'white'),
                'Exterior': ('black', 'black'),
                'Online': ('grey', 'none'),
                'Pocket': ('none', 'grey'),
                'Guide': ('blue', 'none')
                }

SVG_COORD_FORMAT = '{:.2f} {:.2f}'

DEFAULTS = {
    'cut_depth': ['0', '18 mm', '50 mm'],
    'tool_diameter': ['0.1 mm', '3 mm', '25 mm'],
}

FILLET_RESOLUTION = 8

SVG_HEADER_TEMPLATE = '''\
<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Blender SVG Export by {author} v{version})  -->
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
xml:space="preserve" style="background-color:#d0d0d0" stroke-width="5%"
width="{width:.2f}{unit}" height="{height:.2f}{unit}"          
viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}">
'''
