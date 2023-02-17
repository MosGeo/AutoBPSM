from pathlib import Path
from typing import Optional
import pandas as pd
from pydantic_xml import BaseXmlModel, element, attr
from auto_bpsm.file_formats.lithology_extras.meta import Meta
from auto_bpsm.file_formats.lithology_extras.curve import CurveGroup, Curve
from auto_bpsm.file_formats.lithology_extras.litho import LithologyGroup, Lithology


class LithologyCatalogue(BaseXmlModel, tag="Catalogue"):
    # xmlns_xsd: str = attr(name="xmlns:xsd")
    # xmlns_xsi: str = attr(name="xmlns:xsi")
    name: str = element(tag="Name")
    version: str = element(tag="Version")
    readonly: str = element(tag="ReadOnly")
    meta: Meta = element(tag="Meta")
    curve_groups: list[CurveGroup] = element(tag="CurveGroup")
    lithology_groups: list[LithologyGroup] = element(tag="LithologyGroup")

    # Accelerators
    _meta_parameter_group_table: pd.DataFrame = None
    _meta_parameter_table: pd.DataFrame = None
    _lithology_table: pd.DataFrame = None
    _curve_table: pd.DataFrame = None

    class Config:
        underscore_attrs_are_private = True

    @staticmethod
    def read_catalogue_file(filename: Path):
        """Reads the file"""
        with open(filename, "r", encoding="utf-8") as f:
            raw_xml = f.read()
        catalogue = LithologyCatalogue.from_xml(raw_xml)
        catalogue._meta_parameter_group_table = catalogue.meta.get_meta_parameter_group_table()
        catalogue._meta_parameter_table = catalogue.meta.get_meta_parameter_table()
        catalogue._lithology_table = catalogue.get_lithology_table()
        catalogue._curve_table = catalogue.get_curve_table()
        return catalogue

    def write_catalogue_file(self, filename: Path):
        """Writes the catalogue"""
        xml_byte = self.to_xml(skip_empty=True, pretty_print=True, encoding="utf-8")
        xml_string = xml_byte.decode(encoding="utf-8")
        xml_string = xml_string.replace("&gt;", ">")
        xml_string = xml_string.replace("&lt;", "<")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)

    def get_lithology_table(self) -> pd.DataFrame:
        """Build the lithology table"""
        lithology_table_raw = []
        groups_to_analyze = [(lg, []) for lg in self.lithology_groups]

        while len(groups_to_analyze) != 0:
            lithology_group, history = groups_to_analyze.pop()
            new_history = history.copy()
            new_history.append(lithology_group.name)
            if lithology_group.lithology_groups is not None and len(lithology_group.lithology_groups) > 0:
                lg_to_add = [(mpg, new_history) for mpg in lithology_group.lithology_groups]
                groups_to_analyze.extend(lg_to_add)

            for litho in lithology_group.lithologies:
                row = [litho.id, litho.name, litho, new_history]
                lithology_table_raw.append(row)

        lithology_table = pd.DataFrame(data=lithology_table_raw, columns=["Id", "Name", "Lithology", "Group"])
        return lithology_table

    def get_lithology(self, lithology_name: str) -> Lithology:
        """retrieves a lithology by its name"""

        to_search = self.lithology_groups.copy()

        found_lithologies = []
        while len(to_search):
            lithology_group = to_search.pop()
            for lithology in lithology_group.lithologies:
                if lithology.name.lower() == lithology_name.lower():
                    found_lithologies.append(lithology)
            to_search.extend(lithology_group.lithology_groups)

        if len(found_lithologies) == 0:
            raise NameError("Lithology not found.")
        if len(found_lithologies) == 1:
            lithology = found_lithologies[0]
        else:
            raise NameError("Multiple lithologies found.")

        return lithology

    def get_curve_table(self) -> pd.DataFrame:
        """Build the curve table"""
        curve_table_raw = []
        for curve_group in self.curve_groups:
            for curve in curve_group.curves:
                row = [curve.id, curve.name, curve, curve_group.name]
                curve_table_raw.append(row)
        curve_table = pd.DataFrame(data=curve_table_raw, columns=["Id", "Name", "Curve", "Curve Group"])
        return curve_table

    def get_curve(self, curve_name: str) -> Curve:
        """returns a curve using the curve name"""
        for curve_group in self.curve_groups:
            for curve in curve_group.curves:
                if curve.name == curve_name:
                    return curve
        return None

    def get_lithology_parameters_table(self, lithology_name: str) -> pd.DataFrame:
        """Get lithology parameters"""
        lithology = self.get_lithology(lithology_name=lithology_name)

        parameters_table_raw = []
        for parameter_group in lithology.parameter_groups:
            for parameter in parameter_group.parameters:
                meta_parameter_name = self.get_parameter_name_by_id(parameter.meta_parameter_id)
                parameters_table_raw.append([parameter.meta_parameter_id, meta_parameter_name, parameter.value])

        parameters_table = pd.DataFrame(data=parameters_table_raw, columns=["Id", "Name", "Value"])
        return parameters_table

    def get_parameter_name_by_id(self, id: str) -> str:
        """Gets the parameter name from id"""
        meta_parameter_table_index = self._meta_parameter_table["Id"] == id
        meta_parameter_name = self._meta_parameter_table.loc[meta_parameter_table_index]["Name"].values[0]
        return meta_parameter_name

    def get_parameter_id_by_name(self, name: str) -> str:
        meta_parameter_table_index = self._meta_parameter_table["Name"] == name
        meta_parameter_id = self._meta_parameter_table.loc[meta_parameter_table_index]["Id"].values[0]
        return meta_parameter_id

    def update_lithology_parameter(
        self, lithology_name: str, parameter_dict: dict[str, str], is_create_new_curves: bool = False
    ):
        lithology = self.get_lithology(lithology_name=lithology_name)

        # Construct the parameter dictionary with names
        parameter_id_value_dict = {}
        for parameter_name, value in parameter_dict.items():
            parameter_id = self.get_parameter_id_by_name(parameter_name)
            parameter_id_value_dict[parameter_id] = value

        for parameter_group in lithology.parameter_groups:
            for parameter in parameter_group.parameters:
                if parameter.meta_parameter_id in parameter_id_value_dict.keys():
                    parameter.value = str(parameter_id_value_dict[parameter.meta_parameter_id])

    def duplicate_lithology(
        self,
        source_lithology: str,
        distination_lithology: str,
        source_lithology_group: Optional[str] = None,
        distination_lithology_group: Optional[str] = None,
        set_modifiable: bool = True,
    ):
        """Duplicate a lithology"""
        return
