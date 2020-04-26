from .constant import SVG_HEADER_TEMPLATE
from .generator import create_cut
from .helper.gen_helper import boundaries
from .helper.other import project_name, write
from ..__init__ import bl_info


class Export:

    def __init__(self, context):
        self.context = context

    def run(self):

        items = self.list_export_items()
        dir_name = self.context.scene.so_cut.export_path

        if self.context.scene.so_cut.separate_files:
            selection_set = {}
            for obj in items:
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

        (x0, y0, _), (x1, y1, _) = boundaries(self.context)  # TODO: respect selection

        scale = self.context.scene.unit_settings.scale_length
        w = (x1 - x0) * scale
        h = (y1 - y0) * scale

        return SVG_HEADER_TEMPLATE.format(
            x0=x0, w=x1 - x0, y0=-y1, h=y1 - y0,
            width=w * 1000, height=h * 1000, unit="mm",
            version=version, author=bl_info['author'],
        )

    def svg_footer(self):
        return '</svg>\n'

    def svg_body(self, selection):
        groups = self.perimeter_groups(selection)
        content = [self.svg_perimeter_group(name_and_group) for name_and_group in groups]
        return '<g transform="scale(1,-1)">' + ''.join(content) + '</g>'

    def perimeter_groups(self, selection):
        orphans = set(selection)
        perimeter_objs = [o for o in selection if o.soc_mesh_cut_type == 'Perimeter']

        groups = []
        for perimeter in perimeter_objs:
            collection_name = perimeter.users_collection[0].name
            siblings = set(perimeter.users_collection[0].objects)
            group = siblings & orphans
            orphans -= group
            if group:
                groups.append([collection_name, group])
        if orphans:
            groups.append(['orphans', orphans])
        return groups

    def svg_perimeter_group(self, name_and_group):
        name, objs = name_and_group
        cuts = [create_cut(self.context, obj) for obj in objs]
        content = [cut.svg() for cut in cuts]
        content_sorted = [item[1] for item in sorted(content, reverse=False)]
        return f'<g class="Collection" id="{name}">' + ''.join(content_sorted) + '</g>'
