def get_bevel_object(self):
    if self.obj.soc_bevel_name:
        bevel_obj = get_object_safely(self.obj.soc_bevel_name, report_error=False)
        if bevel_obj:
            return bevel_obj

    collection = get_helper_collection(self.context)
    name = f'{PREFIX}{self.obj.name}.bevel'
    bevel_obj = add_nurbs_square(collection, name, self.obj.soc_curve_cut_type)
    bevel_obj.soc_object_type = 'Helper'
    bevel_obj.hide_set(True)
    self.obj.soc_bevel_name = bevel_obj.name

    return bevel_obj
