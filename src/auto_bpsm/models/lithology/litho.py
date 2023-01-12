from typing import Optional
from pydantic import BaseModel
from bs4.element import Tag
from auto_bpsm.models.helpers import model_from_dict


class Parameter(BaseModel):
    MetaParameterId: str
    Value: Optional[str] = None


class ParameterGroup(BaseModel):
    MetaParameterGroupId: str
    Parameters: list[Parameter] = []

    def from_xml(xml_node: Tag):
        parameter_group_id = xml_node.findChild("MetaParameterGroupId", recursive=False).string
        parameters = []
        parameters_nodes = xml_node.findChildren("Parameter", recursive=False)
        for parameter_node in parameters_nodes:
            parameter = model_from_dict(Parameter, parameter_node)
            parameters.append(parameter)

        return ParameterGroup(MetaParameterGroupId=parameter_group_id, Parameters=parameters)


class LithologyComponent(BaseModel):
    LithologyId: str
    Fraction: float


class Mixing(BaseModel):
    ThermalConductivity: str
    Permeability: str
    CapillaryEntryPressure: str
    ReadOnly: str
    LithologyComponents: list[LithologyComponent] = []

    def from_xml(xml_node: Tag):
        variables = list(Mixing.__fields__.keys())
        variables.remove("LithologyComponents")
        mixing: Mixing = model_from_dict(Mixing, xml_node, variables)

        lithology_components_nodes = xml_node.findChildren("LithologyComponents", recursive=False)
        for lithology_components_node in lithology_components_nodes:
            lithology_components = model_from_dict(LithologyComponent, lithology_components_node)
            mixing.LithologyComponents.append(lithology_components)


class Lithology(BaseModel):
    Id: str
    Name: str
    ReadOnly: str
    PetroModId: str
    Pattern: str
    Color: str
    Mixing: Optional[Mixing]
    ParameterGroups: list[ParameterGroup] = []

    def from_xml(xml_node: Tag):
        variables = list(Lithology.__fields__.keys())
        variables.remove("ParameterGroups")
        lithology: Lithology = model_from_dict(Lithology, xml_node, variables)

        # Mixing
        mixing_node = xml_node.findChild("Mixing")
        if mixing_node:
            lithology.Mixing = Mixing.from_xml(mixing_node)

        parameter_group_nodes = xml_node.findChildren("ParameterGroup", recursive=False)
        for parameter_group_node in parameter_group_nodes:
            lithology.ParameterGroups.append(ParameterGroup.from_xml(parameter_group_node))
        return lithology


class LithologyGroup(BaseModel):
    Id: str
    Name: str
    ReadOnly: str
    PetroModId: str
    LithologyGroups: list = []
    Lithologies: list[Lithology] = []

    def from_xml(xml_node: Tag):

        # Initial variable
        variables = list(LithologyGroup.__fields__.keys())
        variables.remove("LithologyGroups")
        variables.remove("Lithologies")
        lithology_group: LithologyGroup = model_from_dict(LithologyGroup, xml_node, variables)

        # Lithology groups
        lithology_group_nodes = xml_node.findChildren("LithologyGroup", recursive=False)
        for lithology_group_node in lithology_group_nodes:
            lithology_group = LithologyGroup.from_xml(lithology_group_node)
            lithology_group.LithologyGroups.append(lithology_group)

        # Lithologies
        lithology_nodes = xml_node.findChildren("Lithology", recursive=False)
        for lithology_node in lithology_nodes:
            lithology = Lithology.from_xml(lithology_node)
            lithology_group.Lithologies.append(lithology)

        return lithology_group
