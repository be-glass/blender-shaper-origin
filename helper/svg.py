from ..constant import CUT_ENCODING


def svg_material_attributes(id):
    style_map = {
        'Perimeter': 'Exterior',
        'Exterior': 'Exterior',
        'Cutout': 'Pocket',
        'Interior': 'Interior',
        'Pocket': 'Pocket',
        'Online': 'Online',
        'Guide': 'Guide',
    }

    style = style_map[id]
    (stroke, fill) = CUT_ENCODING[style]
    return f'stroke="{stroke}" fill="{fill}"'
