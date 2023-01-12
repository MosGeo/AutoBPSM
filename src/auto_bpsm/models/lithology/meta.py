from typing import Optional
from pydantic import BaseModel
from bs4.element import Tag
from auto_bpsm.models.helpers import model_from_dict, tag_from_model
from bs4 import BeautifulSoup


class MetaParameter(BaseModel):
    """MetaParameter node"""

    Id: str
    Name: str
    ValueType: str
    DefaultValue: Optional[str]
    PetrelTemplate: Optional[str]
    ReadOnly: str


class MetaParameterGroup(BaseModel):
    """MetaParameterGroup node"""

    Id: str
    Name: str
    ReadOnly: str
    MetaParameters: list[MetaParameter] = []
    MetaParameterGroups: list = []

    _SIMPLE_VARIABLE_NAMES = ["Id", "Name", "ReadOnly"]

    def from_xml(xml_node: Tag):

        name = xml_node.findChild("Name", recursive=False).string
        id = xml_node.findChild("Id", recursive=False).string
        read_only = xml_node.findChild("ReadOnly", recursive=False).string

        meta_parameters_nodes = xml_node.findChildren("MetaParameter", recursive=False)
        meta_parameter_groups_nodes = xml_node.findChildren("MetaParameterGroup", recursive=False)

        meta_parameter_groups = []
        for meta_parameter_groups_node in meta_parameter_groups_nodes:
            meta_parameter_group: MetaParameterGroup = MetaParameterGroup.from_xml(meta_parameter_groups_node)
            meta_parameter_groups.append(meta_parameter_group)

        meta_parameters = []
        for meta_parameter_node in meta_parameters_nodes:
            meta_parameter: MetaParameter = model_from_dict(MetaParameter, meta_parameter_node)
            meta_parameters.append(meta_parameter)

        return MetaParameterGroup(
            Name=name,
            Id=id,
            ReadOnly=read_only,
            MetaParameters=meta_parameters,
            meta_parameter_groups=meta_parameter_groups,
        )

    def to_xml(self):
        """Converts the model into tag"""
        meta_parameter_group_tag = tag_from_model(self, MetaParameterGroup._SIMPLE_VARIABLE_NAMES)

        for meta_parameter in self.MetaParameters:
            child_tag = tag_from_model(meta_parameter)
            meta_parameter_group_tag.append(child_tag)

        for meta_parameter_group in self.MetaParameterGroups:
            child_tag = tag_from_model(meta_parameter_group, MetaParameterGroup._SIMPLE_VARIABLE_NAMES)
            meta_parameter_group_tag.append(child_tag)

        return meta_parameter_group_tag


class Meta(BaseModel):
    """Main node for meta"""

    MetaParameterGroups: list[MetaParameterGroup]

    def from_xml(xml_node: Tag):
        meta_parameter_groups_nodes = xml_node.findChildren("MetaParameterGroup", recursive=False)
        meta_parameter_groups = []
        for meta_parameter_group in meta_parameter_groups_nodes:
            meta_parameter_groups.append(MetaParameterGroup.from_xml(meta_parameter_group))
        return Meta(MetaParameterGroups=meta_parameter_groups)

    def to_xml(self):
        meta_tag = tag_from_model(self, [])
        for meta_parameter_group in self.MetaParameterGroups:
            child_tag = tag_from_model(meta_parameter_group, MetaParameterGroup._SIMPLE_VARIABLE_NAMES)
            meta_tag.append(child_tag)
        return meta_tag
