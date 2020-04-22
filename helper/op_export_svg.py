from ..constant import SVG_COORD_FORMAT, SVG_HEADER_TEMPLATE, CUT_ENCODING
from .gen_helper import boundaries


def dimensions(context, selection):
    minimum, maximum = boundaries(context, selection)
    x0, y0, z0 = minimum
    x1, y1, z1 = maximum

    scale = context.scene.unit_settings.scale_length
    w = (x1 - x0) * scale
    h = (y1-y0) * scale

    # debug:
    # helper.add_Empty_at(x0, y0, z0)
    # helper.add_Empty_at(x1, y1, z1)

    return x0, y0, x1, y1, w, h


def vector2string(vector):
    return SVG_COORD_FORMAT.format(vector[0], vector[1])


