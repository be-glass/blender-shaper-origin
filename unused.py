from mathutils import Vector


def polygon_angles(self):
    angles = []
    m = self.obj.data
    corners = len(m.vertices)
    for i in range(corners):
        ab, cd = [e for e in m.edges if e.vertices[0] == i or e.vertices[1] == i]
        a, b = ab.vertices
        d, c = cd.vertices
        v_ab = Vector(m.vertices[a].co) - Vector(m.vertices[b].co)
        v_cd = Vector(m.vertices[c].co) - Vector(m.vertices[d].co)
        angles.append(v_ab.angle(v_cd))
    return angles


def polygon_count(self):
    return len(self.obj.data.polygons)
