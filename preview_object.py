from . import helper


class PreviewObject:

    def create(self, context, collection, cut_obj, reference):

        q = cut_obj.copy()
        q.data = cut_obj.data.copy()
        collection.objects.link(q)
        q.soc_object_type = 'Preview'
        helper.apply_scale(context, q)
        q.matrix_world = reference.matrix_world
