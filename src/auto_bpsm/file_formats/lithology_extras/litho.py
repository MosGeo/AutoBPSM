from typing import Optional, TypeVar
from pydantic_xml import BaseXmlModel, element


class Parameter(BaseXmlModel):
    meta_parameter_id: str = element(tag="MetaParameterId")
    value: Optional[str] = element(tag="Value")


class ParameterGroup(BaseXmlModel):
    meta_parameter_group_id: str = element(tag="MetaParameterGroupId")
    parameters: list[Parameter] = element(tag="Parameter")


class LithologyComponent(BaseXmlModel):
    lithology_id: str = element(tag="LithologyId")
    fraction: float = element(tag="Fraction")


class Mixing(BaseXmlModel):
    thermal_conductivity: str = element(tag="ThermalConductivity")
    permeability: str = element(tag="Permeability")
    # capillary_entry_pressure: Optional[str] = element(tag="CapillaryEntryPressure")
    readonly: str = element(tag="ReadOnly")
    lithology_components: list[LithologyComponent] = element(tag="LithologyComponent")


class Lithology(BaseXmlModel):

    id: str = element(tag="Id")
    name: str = element(tag="Name")
    creator: Optional[str] = element(tag="Creator")
    readonly: str = element(tag="ReadOnly")
    petromod_id: str = element(tag="PetroModId")
    pattern: str = element(tag="Pattern")
    color: str = element(tag="Color")
    mixing: Optional[Mixing] = element(tag="Mixing")
    parameter_groups: list[ParameterGroup] = element(tag="ParameterGroup")


TLithologyGroup = TypeVar("TLithologyGroup", bound="LithologyGroup")


class LithologyGroup(BaseXmlModel):
    id: str = element(tag="Id")
    name: str = element(tag="Name")
    readonly: str = element(tag="ReadOnly")
    petromod_id: str = element(tag="PetroModId")
    lithology_groups: list[TLithologyGroup] = element(tag="LithologyGroup")
    lithologies: list[Lithology] = element(tag="Lithology")

    # def get_lithology(self, lithology_name: str):
    #     """retrieves a lithology by its name"""
    #     lithologies = []
    #     for lithology in self.lithologies:
    #         if lithology.name.lower() == lithology_name.lower():
    #             lithologies.append(lithology)
    #     for lithology_group in self.lithology_groups:
    #         lithologies.extend(lithology_group.get_lithology(lithology_name=lithology_name))
    #     return lithologies
