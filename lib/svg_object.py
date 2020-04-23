from .helper.other import err_implementation
from .helper.preview_helper import transform_export
from .helper.svg import svg_material_attributes
from .helper.op_export_svg import vector2string


def create(context, obj):
    if obj.type == 'MESH':
        return SvgMesh(context, obj)
    elif obj.type == 'CURVE':
        return SvgCurve(context, obj)
    else:
        err_implementation(context)
        return None


class SvgObject:
    def __init__(self, context, obj):
        self.obj = obj
        self.context = context

    def svg_path(self, points, is_closed):
        source = ''
        path_cmd = 'M'
        for point in points:
            vector = transform_export(self.context, self.obj) @ point.co
            source += path_cmd + vector2string(vector)
            path_cmd = 'L'
        if is_closed:
            source += 'Z'
        return f'<path d="{source}"/>'

    def svg_object(self, content, attributes):
        return \
            f'<g id="{self.obj.name_full}" class="{self.obj.type}" {attributes}>' + \
            ''.join(content) + \
            '</g>'


class SvgMesh(SvgObject):

    def svg(self):
        content = ''.join([
            self.svg_polygon(self.obj, self.obj.data.vertices, p) for p in self.obj.data.polygons
        ])
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
        return self.svg_object(content, attributes)

    def svg_polygon(self, obj, vertices, polygon):
        points = [vertices[i] for i in polygon.vertices]
        return self.svg_path(points, is_closed=True)


class SvgCurve(SvgObject):

    def svg(self):
        content = ''.join([
            self.svg_path(s.points, is_closed=s.use_cyclic_u) for s in self.obj.data.splines
        ])
        attributes = svg_material_attributes(self.obj.soc_curve_cut_type)
        return self.svg_object(content, attributes)
        # TODO check if cyclic switch is working
