import bpy

from . import constant


def dimensions(scale):
    if constant.sheet_name in bpy.data.objects.keys():
        sheet = bpy.data.objects[constant.sheet_name]
        (w, h, zz) = sheet.dimensions
        (x0, y0, z0) = sheet.data.vertices[0].co
        (x1, y1, z1) = sheet.data.vertices[3].co
        # TODO: warn if Z is not zero
    else:
        (x0, y0, x1, y1) = (0, 0, 1000, 1000)
        (w, h) = (300, 200)
    return x0, y0, x1, y1, w*scale, h*scale


# def scale(context):
#     return context.scene.unit_settings.scale_length



def vector2string(vector):
    return constant.svg_coords.format(vector[0], vector[1])


def svg_header(context, bl_info):
    version = '.'.join([str(i) for i in bl_info['version']])
    (x0, y0, x1, y1, w, h) = dimensions(bpy.context.scene.unit_settings.scale_length)

    return constant.svg_header_template.format(
        x0=x0, w=x1-x0, y0=y0, h=y1-y0,
        width=w, height=h, unit="m",   # TODO fix unit handling
        version=version, author=bl_info['author'],
    )


def svg_footer():
    return '</svg>\n'


def svg_path(context, points, is_closed):
    source = ''
    path_cmd = 'M'
    for point in points:
        vector = context.object.matrix_world @ point.co
        source += path_cmd + vector2string(vector)
        path_cmd = 'L'
    if is_closed:
        source += 'Z'
    return f'<path d="{source}"/>'




# def svg_group_attributes(id):
#     (stroke, fill) = constant.cut_encoding[id]
#     return f'stroke="{stroke}" fill="{fill}"'

# def svg_group_material(context, material_id):
#     source = ''
#
#     for object in bpy.data.objects:
#         if material_id in object.data.materials.keys():
#             source += svg_group_object(context, object)
#
#     if source:
#         id = material_id.replace(constant.prefix, '')
#         attributes = svg_group_attributes(id)
#         return f'<g id="{id}" class="material" {attributes}>{source}</g>\n'
#     else:
#         return ""






def svg_polygon(context, vertices, polygon):
    points = [vertices[i] for i in polygon.vertices]
    return svg_path(context, points, is_closed=True)


def svg_mesh(context, obj):
    return ''.join([
        svg_polygon(context, obj.data.vertices, p) for p in obj.data.polygons
    ])


def svg_curve(context, obj):
    return ''.join([
        svg_path(context, s.points, is_closed=False) for s in obj.data.splines
    ])


def svg_object(context, obj):
    if obj.type == 'MESH':
        content = svg_mesh(context, obj)
    elif obj.type == 'CURVE':
        content = svg_curve(context, obj)
    else:
        return ''

    return \
        f'<g id="{obj.name_full}" class="{obj.type}">' + \
        ''.join(content) + \
        '</g>'


def svg_body(context, selection):
    return \
        '<g transform="scale(1,-1)">' + \
        ''.join([
            svg_object(context, obj) for obj in selection
        ]) + '</g>'


def svg_content(context, selection, bl_info):
    return \
        svg_header(context, bl_info) + \
        svg_body(context, selection) + \
        svg_footer()
