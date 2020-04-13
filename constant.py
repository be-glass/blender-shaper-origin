prefix = "SOC_"
Prefix = "SOC_"

# sheet_name = prefix + "Work Area"

# cut_face_color = {'Interior': (1, 1, 1, 1),
#                   'Exterior': (0, 0, 0, 1),
#                   'Online': (1, 0, 1, 1),
#                   'Pocket': (.5, .5, .5, 1),
#                   'Guide': (0, 0, 1, 1)}

cut_encoding = {'Interior': ('black', 'white'),
                'Exterior': ('black', 'black'),
                'Online': ('grey', 'none'),
                'Pocket': ('none', 'grey'),
                'Guide': ('blue', 'none')
                }

svg_header_template= '''\
<?xml version="1.0" encoding="utf-8"?>
<!-- Generator: Blender SVG Export by {author} v{version})  -->
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
xml:space="preserve" style="background-color:#d0d0d0" stroke-width="5%"
width="{width:.2f}{unit}" height="{height:.2f}{unit}"          
viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}">
'''

valid_types = ['MESH', 'CURVE']

svg_coords = '{:.2f} {:.2f}'

defaults = {
    'cut_depth': ['0', '18 mm', '50 mm'],
    'tool_diameter': ['0.1 mm', '3 mm', '25 mm'],
}

fillet_resolution = 8
