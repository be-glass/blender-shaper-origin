import bpy

from . import constant, helper


def dimensions(context, selection):

    x0, y0, z0, x1, y1, z1 = helper.boundaries(selection)
    scale = context.scene.unit_settings.scale_length
    w = (x1-x0) * scale
    h = (y1-y0) * scale

    # debug:
    # helper.add_Empty_at(x0, y0, z0)
    # helper.add_Empty_at(x1, y1, z1)

    return x0, y0, x1, y1, w, h


def vector2string(vector):
    return constant.svg_coords.format(vector[0], vector[1])


def svg_header(context, selection, bl_info):
    version = '.'.join([str(i) for i in bl_info['version']])
    (x0, y0, x1, y1, w, h) = dimensions(context, selection)

    return constant.svg_header_template.format(
        x0=x0, w=x1-x0, y0=-y1, h=y1-y0,
        width=w*1000, height=h*1000, unit="mm",
        version=version, author=bl_info['author'],
    )


def svg_footer():
    return '</svg>\n'


def svg_path(obj, points, is_closed):
    source = ''
    path_cmd = 'M'
    for point in points:
        vector = helper.transform_if_needed(obj, point.co)
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






def svg_polygon(obj, vertices, polygon):
    points = [vertices[i] for i in polygon.vertices]
    return svg_path(obj, points, is_closed=True)


def svg_mesh(obj):
    return ''.join([
        svg_polygon(obj, obj.data.vertices, p) for p in obj.data.polygons
    ])


def svg_curve(obj):
    return ''.join([
        svg_path(obj, s.points, is_closed=False) for s in obj.data.splines
    ])


def svg_object(obj):
    if obj.type == 'MESH':
        content = svg_mesh(obj)
    elif obj.type == 'CURVE':
        content = svg_curve(obj)
    else:
        return ''

    return \
        f'<g id="{obj.name_full}" class="{obj.type}">' + \
        ''.join(content) + \
        '</g>'


def svg_body(selection):
    return \
        '<g transform="scale(1,-1)">' + \
        ''.join([
            svg_object(obj) for obj in selection
        ]) + '</g>'


def svg_content(context, selection, bl_info):
    return \
        svg_header(context, selection, bl_info) + \
        svg_body(selection) + \
        svg_footer()
