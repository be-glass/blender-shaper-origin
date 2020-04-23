from .helper.mesh import curve2mesh
from .helper.other import err_implementation, find_first_perimeter
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
    def __init__(self, context, obj, curve_obj=None):
        self.obj = obj
        self.context = context
        self.original = curve_obj if curve_obj else obj
        self.cut_type = curve_obj.soc_curve_cut_type if curve_obj else obj.soc_mesh_cut_type

    def svg_object(self, content, attributes):
        return \
            f'<g id="{self.original.name_full}" class="{self.original.type}" {attributes}>' + \
            ''.join(content) + \
            '</g>'


class SvgMesh(SvgObject):

    def svg(self):

        self.perimeter = find_first_perimeter(self.original)

        self.attributes = svg_material_attributes(self.cut_type)

        z = 0
        content = ''
        for p in self.obj.data.polygons:
            c, z = self.svg_polygon(self.obj, self.obj.data.vertices, p)
            content += c

        return z, self.svg_object(content, self.attributes)

    def svg_polygon(self, obj, vertices, polygon):
        points = [vertices[i] for i in polygon.vertices]
        return self.svg_path(points, is_closed=True)

    def svg_path(self, points, is_closed):
        source = ''
        path_cmd = 'M'
        z = 0
        for point in points:
            vector = transform_export(self.context, self.original, self.perimeter) @ point.co
            source += path_cmd + vector2string(vector)
            path_cmd = 'L'
            z = vector[2]
        if is_closed:
            source += 'Z'
        return f'<path d="{source}"/>', z


class SvgCurve(SvgObject):

    def svg(self):
        mesh_obj = curve2mesh(self.context, self.obj, add_face=True)
        svg_obj = SvgMesh(self.context, mesh_obj, curve_obj=self.obj)

        return svg_obj.svg()
