from .base import Generator
from ..helper.gen_helper import *
from ..helper.other import find_first_perimeter


class Proxy(Generator):

    def setup_proxy(self, source_obj):
        reference = get_reference(self.context, source_obj)
        self.obj.soc_reference_name = reference.name
        self.perimeter = find_first_perimeter(source_obj)
        self.obj.soc_object_type = 'Proxy'
