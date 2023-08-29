from typing import Optional, TypeVar
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
    readonly: Optional[str] = element(tag="ReadOnly")
    meta_parameters: Optional[list[MetaParameter]] = element(tag="MetaParameter")
    meta_parameter_groups: Optional[list[TMetaParameterGroup]] = element(tag="MetaParameterGroup")


class Meta(BaseXmlModel):
    """Main node for meta"""

    meta_parameter_groups: list[MetaParameterGroup] = element(tag="MetaParameterGroup")
