from ..helper.other import vector2string


def svg_object(self, content, attributes):
    return \
        f'<g id="{self.cut_obj.name_full}" class="{self.cut_obj.type}" {attributes}>' + \
        ''.join(content) + \
        '</g>'


def svg_polygon(self, polygon):
    points = [self.cut_obj.data.vertices[i] for i in polygon.vertices]
    return self.svg_path(points, is_closed=True)


def svg_path(self, points, is_closed):
    source = ''
    path_cmd = 'M'
    for point in points:
        vector = transform_export(self.cut_obj, self.perimeter_objs) @ point.co
        source += path_cmd + vector2string(vector)
        path_cmd = 'L'
    if is_closed:
        source += 'Z'
    return f'<path d="{source}"/>'


def svg_mesh(self):
    content = ''
    for polygon in self.cut_obj.data.polygons:
        c = self.svg_polygon(polygon)
        content += c

    return content
