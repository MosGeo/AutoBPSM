from typing import Optional, TypeVar
import pandas as pd
from pydantic_xml import BaseXmlModel, element


class MetaParameter(BaseXmlModel):
    """MetaParameter node"""

    id: str = element(tag="Id")
    name: str = element(tag="Name")
    value_type: str = element(tag="ValueType")
    default_value: Optional[str] = element(tag="DefaultValue")
    petrel_template: Optional[str] = element(tag="PetrelTemplate")
    petromod_unit: Optional[str] = element(tag="PetroModUnit")
    readonly: str = element(tag="ReadOnly")


TMetaParameterGroup = TypeVar("TMetaParameterGroup", bound="MetaParameterGroup")


class MetaParameterGroup(BaseXmlModel):
    """MetaParameterGroup node"""

    id: str = element(tag="Id")
    name: str = element(tag="Name")
    readonly: str = element(tag="ReadOnly")
    meta_parameters: Optional[list[MetaParameter]] = element(tag="MetaParameter")
    meta_parameter_groups: Optional[list[TMetaParameterGroup]] = element(tag="MetaParameterGroup")


class Meta(BaseXmlModel):
    """Main node for meta"""

    meta_parameter_groups: list[MetaParameterGroup] = element(tag="MetaParameterGroup")

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

    # def get_meta_parameter_group_by_id(self, id: str, meta_parameter_group: MetaParameterGroup = None):
    #     """Get meta_parameter_group by id"""
    #     if meta_parameter_group is not None and meta_parameter_group.id == id:
    #         return meta_parameter_group

    #     for meta_parameter_group in meta_parameter_group.meta_parameter_groups:
    #         meta_parameter_group = self.get_meta_parameter_group_by_id(id, meta_parameter_group)
    #         if meta_parameter_group:
    #             return meta_parameter_group

    #     return None

    # def get_meta_parameter_by_id(self, id: str, meta_parameter_group: MetaParameterGroup = None):
    #     """Gets a meta parameter"""
    #     for meta_parameter in meta_parameter_group.meta_parameters:
    #         if meta_parameter.id == id:
    #             return meta_parameter

    #     for meta_parameter_group in meta_parameter_group.meta_parameter_groups:
    #         meta_parameter = self.get_meta_parameter_by_id(id, meta_parameter_group)
    #         if meta_parameter:
    #             return meta_parameter

    #     return None
