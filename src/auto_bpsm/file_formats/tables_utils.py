import pandas as pd


def get_lithology_table(lithology_groups) -> pd.DataFrame:
    """Build the lithology table"""
    lithology_table_raw = []
    groups_to_analyze = [(lg, []) for lg in lithology_groups]

    while len(groups_to_analyze) != 0:
        lithology_group, history = groups_to_analyze.pop()
        new_history = history.copy()
        new_history.append(lithology_group.name)
        if lithology_group.lithology_groups is not None and len(lithology_group.lithology_groups) > 0:
            lg_to_add = [(mpg, new_history) for mpg in lithology_group.lithology_groups]
            groups_to_analyze.extend(lg_to_add)

        if lithology_group.lithologies:
            for litho in lithology_group.lithologies:
                row = [litho.id, litho.name, litho, new_history]
                lithology_table_raw.append(row)

    lithology_table = pd.DataFrame(data=lithology_table_raw, columns=["Id", "Name", "Lithology", "Group"])
    return lithology_table


def get_curve_table(curve_groups) -> pd.DataFrame:
    """Build the curve table"""
    curve_table_raw = []
    for curve_group in curve_groups:
        for curve in curve_group.curves:
            row = [curve.id, curve.name, curve, curve_group.name]
            curve_table_raw.append(row)
    curve_table = pd.DataFrame(data=curve_table_raw, columns=["Id", "Name", "Curve", "Curve Group"])
    return curve_table


def get_meta_parameter_table(self):
    """Gets the parameter table"""
    meta_table_raw = []
    groups_to_analyze = [(mpg, []) for mpg in self.meta_parameter_groups]

    while len(groups_to_analyze) != 0:
        meta_parameter_group, history = groups_to_analyze.pop()
        new_history = history.copy()
        new_history.append(meta_parameter_group.name)
        if (
            meta_parameter_group.meta_parameter_groups is not None
            and len(meta_parameter_group.meta_parameter_groups) > 0
        ):
            mpg_to_add = [(mpg, new_history) for mpg in meta_parameter_group.meta_parameter_groups]
            groups_to_analyze.extend(mpg_to_add)

        if meta_parameter_group.meta_parameters:
            for mp in meta_parameter_group.meta_parameters:
                row = [mp.id, mp.name, mp.default_value, new_history]
                meta_table_raw.append(row)
    meta_table = pd.DataFrame(data=meta_table_raw, columns=["Id", "Name", "Default", "Group"])
    return meta_table


def get_meta_parameter_group_table(self):
    meta_table_raw = []
    groups_to_analyze = [(mpg, []) for mpg in self.meta_parameter_groups]

    while len(groups_to_analyze) != 0:
        meta_parameter_group, history = groups_to_analyze.pop()
        new_history = history.copy()
        new_history.append(meta_parameter_group.name)
        if (
            meta_parameter_group.meta_parameter_groups is not None
            and len(meta_parameter_group.meta_parameter_groups) > 0
        ):
            mpg_to_add = [(mpg, new_history) for mpg in meta_parameter_group.meta_parameter_groups]
            groups_to_analyze.extend(mpg_to_add)

        row = [meta_parameter_group.id, meta_parameter_group.name, history]
        meta_table_raw.append(row)

    meta_table = pd.DataFrame(data=meta_table_raw, columns=["Id", "Name", "Group"])
    return meta_table


def get_lithology_parameters_table(self, lithology_name: str) -> pd.DataFrame:
    """Get lithology parameters"""
    lithology = self.get_lithology(lithology_name=lithology_name)

    parameters_table_raw = []
    for parameter_group in lithology.parameter_groups:
        for parameter in parameter_group.parameters:
            meta_parameter, _meta_parameter_group = self.get_meta_parameter(parameter.meta_parameter_id)
            parameters_table_raw.append([parameter.meta_parameter_id, meta_parameter.name, parameter.value])

    parameters_table = pd.DataFrame(data=parameters_table_raw, columns=["Id", "Name", "Value"])
    return parameters_table
