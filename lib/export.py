from ..__init__ import bl_info
from .constant import SVG_HEADER_TEMPLATE
from .helper.other import project_name, write
from .helper.op_export_svg import dimensions
from . import svg_object


class Export:

    def __init__(self, context):
        self.context = context

    def run(self):

        items = self.list_export_items()
        dir_name = self.context.scene.so_cut.export_path

        if self.context.scene.so_cut.separate_files:
            selection_set = {}
            for obj in items:
                name = obj.name
                selection_set[obj.name] = [obj]
        else:
            name = project_name()
            selection_set = {name: items}

        if not selection_set:
            return "Nothing to export"

        for name, selection in selection_set.items():
            content = self.svg_content(selection)
            file_name = f'{dir_name}/{name}.svg'
            write(content, file_name)

        return "Export Done"

    def list_export_items(self):
        if self.context.scene.so_cut.selected_only:
            items = self.context.selected_objects
        else:
            items = self.context.scene.objects
        return [o for o in items if o.soc_object_type == 'Cut']

    def svg_content(self, selection):
        return \
            self.svg_header(selection) + \
            self.svg_body(selection) + \
            self.svg_footer()

    def svg_header(self, selection):
        version = '.'.join([str(i) for i in bl_info['version']])

        (x0, y0, x1, y1, w, h) = dimensions(self.context, selection)

        # frame = Preview(self.context) # TODO

        return SVG_HEADER_TEMPLATE.format(
            x0=x0, w=x1 - x0, y0=-y1, h=y1 - y0,
            width=w * 1000, height=h * 1000, unit="mm",
            version=version, author=bl_info['author'],
        )

    def svg_footer(self):
        return '</svg>\n'

    def svg_body(self, selection):
        svg_objs = [svg_object.create(self.context, obj) for obj in selection]

        return \
            '<g transform="scale(1,-1)">' + \
            ''.join([
                o.svg() for o in svg_objs
            ]) + '</g>'
