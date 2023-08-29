from typing import Optional
from pydantic_xml import BaseXmlModel, element
from auto_bpsm.utilities import decode_id_and_name, is_md5, items_lookup_return


class Parameter(BaseXmlModel, search_mode="unordered"):
    meta_parameter_id: str = element(tag="MetaParameterId")
    value: Optional[str] = element(tag="Value")

    @property
    def is_curve(self) -> bool:
        """Quickly check if it is curve"""
        is_curve_value = is_md5(self.value)
        return is_curve_value


class ParameterGroup(BaseXmlModel, search_mode="unordered"):
    meta_parameter_group_id: str = element(tag="MetaParameterGroupId")
    parameters: list[Parameter] = element(tag="Parameter")

    def get_parameter(self, id: str) -> Parameter | None:
        """Gets the paramter"""
        for parameter in self.parameters:
            if parameter.meta_parameter_id == id:
                return parameter
        return None


class LithologyComponent(BaseXmlModel, search_mode="unordered"):
    id: str = element(tag="LithologyId")
    fraction: float = element(tag="Fraction")


class Mixing(BaseXmlModel, search_mode="unordered"):
    lithology_components: list[LithologyComponent] = element(tag="LithologyComponent")
    thermal_conductivity: str = element(tag="ThermalConductivity")
    capillary_entry_pressure: Optional[str] = element(tag="CapillaryEntryPressure")
    permeability: str = element(tag="Permeability")
    readonly: str = element(tag="ReadOnly")


class Lithology(BaseXmlModel, search_mode="unordered"):
    id: str = element(tag="Id")
    name: str = element(tag="Name")
    creator: Optional[str] = element(tag="Creator")
    readonly: str = element(tag="ReadOnly")
    petromod_id: str = element(tag="PetroModId")
    pattern: str = element(tag="Pattern")
    color: str = element(tag="Color")
    mixing: Optional[Mixing] = element(tag="Mixing")
    parameter_groups: list[ParameterGroup] = element(tag="ParameterGroup")

    def get_parameter(self, id: str) -> Parameter | None:
        """Gets the paramter"""
        for parameter_group in self.parameter_groups:
            parameter = parameter_group.get_parameter(id=id)
            if parameter is not None:
                return parameter
        return None


class LithologyGroup(BaseXmlModel, search_mode="unordered"):
    id: str = element(tag="Id")
    name: str = element(tag="Name")
    creator: Optional[str] = element(tag="Creator")
    readonly: str = element(tag="ReadOnly")
    petromod_id: str = element(tag="PetroModId")
    lithologies: list[Lithology] = element(tag="Lithology", default_factory=list)

    @property
    def lithology_ids(self) -> list[str]:
        """Returns all the ids of the curves in the curve group"""
        ids = [lithology.id for lithology in self.lithologies]
        return ids

    def get_lithologies(
        self,
        identifier: str,
        is_unique: bool = False,
    ) -> Lithology | list[Lithology]:
        """Returns the lithology given the id or name"""
        id, name = decode_id_and_name(identifier)
        found_lithologies = []
        for lithology in self.lithologies:
            if lithology.id == id or lithology.name == name:
                found_lithologies.append([lithology, self])
        return items_lookup_return(found_lithologies, is_unique)

    def contains_lithology(self, lithology: Lithology):
        """Checks the lithology group if it contains the lithology"""
        # Stopping condition
        if self.lithologies is None:
            return False
        return lithology in self.lithologies


class MainLithologyGroup(BaseXmlModel, search_mode="unordered"):
    id: str = element(tag="Id")
    name: str = element(tag="Name")
    creator: Optional[str] = element(tag="Creator")
    readonly: str = element(tag="ReadOnly")
    petromod_id: str = element(tag="PetroModId")
    lithology_groups: list[LithologyGroup] = element(tag="LithologyGroup", default_factory=list)

    @property
    def lithology_group_ids(self) -> list[str]:
        """Returns all the ids of the curves in the curve group"""
        ids = [lithology_group.id for lithology_group in self.lithology_groups]
        return ids

    @property
    def lithology_ids(self) -> list[str]:
        """Return lithology ids"""
        ids = []
        for lithology_group in self.lithology_groups:
            ids.extend(lithology_group.lithology_ids)
        return ids

    def contains_lithology_group(self, lithology_group: LithologyGroup) -> bool:
        """Checks if it contains the lithology group"""
        return lithology_group in self.lithology_groups

    def get_lithologies(
        self,
        identifier: str,
        is_unique: bool = False,
    ) -> Lithology | list[Lithology]:
        """Returns the lithology given the id or name"""
        found_lithologies = []
        for lithology_group in self.lithology_groups:
            lithologies: list[list] = lithology_group.get_lithologies(identifier, False)
            for lithology in lithologies:
                lithology.append(self)
            found_lithologies.extend(lithologies)
        return items_lookup_return(found_lithologies, is_unique)

    def get_lithology_groups(
        self,
        identifier: str,
        is_unique: bool = False,
    ) -> LithologyGroup | list[LithologyGroup]:
        """Returns the lithology given the id or name"""
        id, name = decode_id_and_name(identifier)

        # Stopping condition
        if self.lithology_groups is None:
            return items_lookup_return([], is_unique)

        found_lithology_groups = []
        for lithology_group in self.lithology_groups:
            if lithology_group.name == name or lithology_group.id == id:
                found_lithology_groups.append([lithology_group, self])
        return items_lookup_return(found_lithology_groups, is_unique)

    def get_lithology_groups_for_lithology(
        self,
        lithology: Lithology,
        is_unique: bool = False,
    ) -> list:
        """Gets the lithology group"""

        # Stopping condition
        if self.lithology_groups is None:
            return items_lookup_return([], is_unique)

        found_lithology_groups = []
        for lithology_group in self.lithology_groups:
            if lithology_group.contains_lithology(lithology):
                found_lithology_groups.append([lithology_group, self])
        return items_lookup_return(found_lithology_groups, is_unique)
