from .gen_helper import get_reference


def transform_preview(context, bounding_frame, perimeter, obj):
    reference = get_reference(context, perimeter)

    m = bounding_frame.matrix_world \
        @ reference.matrix_world \
        @ perimeter.matrix_world.inverted() \
        @ obj.matrix_world
    return m
