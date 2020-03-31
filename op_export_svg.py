import bpy

from . import constant


def dimensions():
    if constant.sheet_name in bpy.data.objects.keys():
        sheet = bpy.data.objects[constant.sheet_name]
        (w, h, zz) = sheet.dimensions
        (x0, y0, z0) = sheet.data.vertices[0].co
        (x1, y1, z1) = sheet.data.vertices[3].co
        # TODO: warn if Z is not zero
    else:
        (x0, y0, x1, y1) = (0, 0, 1000, 1000)
        (w, h) = (300, 200)
    return x0, y0, x1, y1, w, h


# def scale(context):
#     return context.scene.unit_settings.scale_length


def vector2string(vector):
    return '{:.2f} {:.2f}'.format(vector[0], vector[1])


def svg_header(bl_info):
    version = '.'.join([str(i) for i in bl_info['version']])
    (x0, y0, x1, y1, w, h) = dimensions()

    return constant.svg_header_template.format(
        x0=x0, w=x1-x0, y0=y0, h=y1-y0,
        width=w, height=h, unit="mm",   # TODO fix unit handling
        version=version, author=bl_info['author'],
    )


def svg_path(context, points, closed):
    source = '<path d="'
    path_cmd = 'M'
    for point in points:
        vector = context.object.matrix_world @ point.co
        source += path_cmd + vector2string(vector)
        path_cmd = 'L'
    if closed:
        source += 'Z'
    source += '"/>'
    return source


def svg_footer():
    return '</svg>\n'


def svg_group_attributes(id):
    (stroke, fill) = constant.cut_encoding[id]
    return f'stroke="{stroke}" fill="{fill}"'


def svg_group_object(context, obj):
    source = ''
    if obj.type == 'MESH':
        vertices = obj.data.vertices
        polygons = obj.data.polygons
        for polygon in polygons:
            points = [vertices[i] for i in polygon.vertices]
            source += svg_path(context, points, closed=True)

    elif obj.type == 'CURVE':
        splines = obj.data.splines
        for spline in splines:
            source += svg_path(context, spline.points, closed=False)

    if source:
        id = obj.name_full
        return f'<g id="{id}" class="{obj.type}">{source}</g>'
    else:
        return ''


def svg_group_material(context, material_id):
    source = ''

    for object in bpy.data.objects:
        if material_id in object.data.materials.keys():
            source += svg_group_object(context, object)

    if source:
        id = material_id.replace(constant.prefix, '')
        attributes = svg_group_attributes(id)
        return f'<g id="{id}" class="material" {attributes}>{source}</g>\n'
    else:
        return ""


def svg_body(context):
    source = ''
    for type in constant.cut_face_color.keys():
        material_id = constant.prefix + type
        source += svg_group_material(context, material_id)
    return f'<g transform="scale(1,-1)">{source}</g>'

