from typing import Union

from .bounding import Bounding
from .cut import Cut
from .inactive import Inactive
from .preview import Preview


def type_factory(obj) -> Union[None, Cut, Preview, Bounding, Inactive]:
    sot = obj.soc_object_type
    if sot in ['None', 'Cut']:
        item = Cut(obj)
    elif sot == 'Preview':
        item = Preview(obj)
    elif sot == 'Bounding':
        item = Bounding()
    else:
        item = Inactive()
    return item
