PREFIX = "SOC_"

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

PREVIEW_Z = {
    'Guide': "0.3 mm",
    'Cutout': "0.2 mm",
    'Interior': "0.2 mm",
    'Exterior': "0.2 mm",
    'Online': "0.2 mm",
    'Pocket': "0.1 mm",
    'Perimeter': "0.0 mm",
}

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
