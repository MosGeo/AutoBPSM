from pathlib import Path
from typing import Optional
from typing_extensions import Self
from pydantic_xml import BaseXmlModel, element  # , attr
from auto_bpsm.file_formats.lithology_extras.meta import Meta, MetaParameter, MetaParameterGroup
from auto_bpsm.file_formats.lithology_extras.curve import CurveGroup, Curve
from auto_bpsm.file_formats.lithology_extras.litho import LithologyGroup, Lithology, MainLithologyGroup
from auto_bpsm.utilities import decode_id_and_name, generate_new_id, items_lookup_return, num_string_convert


class LithologyCatalogue(BaseXmlModel, tag="Catalogue"):
    # xmlns_xsd: str = attr(name="xmlns:xsd")
    # xmlns_xsi: str = attr(name="xsi")
    name: str = element(tag="Name")
    version: str = element(tag="Version")
    readonly: str = element(tag="ReadOnly")
    meta: Meta = element(tag="Meta")
    curve_groups: list[CurveGroup] = element(tag="CurveGroup")
    main_lithology_groups: list[MainLithologyGroup] = element(tag="LithologyGroup")

    class Config:
        underscore_attrs_are_private = True

    @property
    def lithology_ids(self):
        """Returns all the ids of the lithology in the lithology groups"""
        ids = []
        for main_lithology_group in self.main_lithology_groups:
            ids.extend(main_lithology_group.lithology_ids)
        return ids

    @property
    def lithology_group_ids(self):
        """Returns all the ids in the lithology groups"""
        ids = []
        for main_lithology_group in self.main_lithology_groups:
            ids.extend(main_lithology_group.lithology_group_ids)
        return ids

    @property
    def main_lithology_group_ids(self):
        """Return all the ids for main lithology groups"""
        ids = []
        for main_lithology_group in self.main_lithology_groups:
            ids.append(main_lithology_group.id)
        return ids

    @property
    def curve_ids(self):
        """Returns all the ids of the curves in the curve group"""
        ids = []
        for curve_group in self.curve_groups:
            ids.extend(curve_group.curve_ids)
        return ids

    @staticmethod
    def read_catalogue_file(filename: Path) -> Self:
        """Reads the file"""
        with open(filename, "r", encoding="utf-8") as f:
            raw_xml = f.read()
        catalogue = LithologyCatalogue.from_xml(raw_xml)
        return catalogue

    def write_catalogue_file(self, filename: Path):
        """Writes the catalogue"""
        xml_byte = self.to_xml(skip_empty=True, pretty_print=True, encoding="utf-8")
        xml_string = xml_byte.decode(encoding="utf-8")
        xml_string = xml_string.replace("&gt;", ">")
        xml_string = xml_string.replace("&lt;", "<")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(xml_string)

    def get_main_lithology_groups(self, identifier: str, is_unique: bool = False):
        """Gets the lithology group"""
        id, name = decode_id_and_name(identifier)

        found_lithologies_group = []
        for main_lithology_group in self.main_lithology_groups:
            if main_lithology_group.name == name or main_lithology_group.id == id:
                found_lithologies_group.append(main_lithology_group)
        return items_lookup_return(found_lithologies_group, is_unique)

    def get_main_lithology_group(self, identifier: str) -> MainLithologyGroup:
        """Gets the lithology group"""
        return self.get_main_lithology_groups(identifier, True)

    def get_lithology_groups(self, identifier: str, is_unique: bool = False):
        """Get the lithology group"""
        found_lithology_group = []
        for main_lithology_group in self.main_lithology_groups:
            found_lithology_group.extend(main_lithology_group.get_lithology_groups(identifier, False))
        return items_lookup_return(found_lithology_group, is_unique)

    def get_lithology_group(self, identifier: str):
        """Get one lithology group"""
        return self.get_lithology_groups(identifier, True)

    def get_lithologies(self, identifier: str) -> list[tuple[Lithology, LithologyGroup, MainLithologyGroup]]:
        """retrieves a lithology by its name or id"""
        found_lithologies = []
        for main_lithology_group in self.main_lithology_groups:
            found_lithologies.extend(main_lithology_group.get_lithologies(identifier, False))
        return found_lithologies

    def get_lithology(
        self,
        identifier: str,
    ) -> tuple[Lithology, LithologyGroup, MainLithologyGroup]:
        """retrieves a lithology by its name or id"""
        found_lithologies = self.get_lithologies(identifier)
        return items_lookup_return(found_lithologies, True)

    def get_curves(
        self,
        identifier: str,
    ) -> list[tuple[Curve, CurveGroup]]:
        """returns a curve using the curve name"""
        found_curves = []
        for curve_group in self.curve_groups:
            found_curves.extend(curve_group.get_curves(identifier, False))
        return found_curves

    def get_curve(
        self,
        identifier: str,
    ) -> tuple[Curve, CurveGroup]:
        """Return one curve"""
        found_curves = self.get_curves(identifier)
        return items_lookup_return(found_curves, True)

    def get_curve_group_for_curve(self, curve: Curve) -> CurveGroup:
        """Return the curve group for the curve"""
        found_curve_groups = []
        for curve_group in self.curve_groups:
            if curve_group.contains_curve(curve):
                found_curve_groups.append(curve_group)
        return items_lookup_return(found_curve_groups, True)

    def get_lithology_group_for_lithology(self, lithology: Lithology):
        found_lithology_groups = []
        for main_lithology_group in self.main_lithology_groups:
            lithology_groups = main_lithology_group.get_lithology_groups_for_lithology(lithology)
            found_lithology_groups.extend(lithology_groups)
        return items_lookup_return(found_lithology_groups, True)

    def get_main_lithology_group_for_lithology_group(self, lithology_group: LithologyGroup) -> MainLithologyGroup:
        found_main_lithology_groups = []
        for main_lithology_group in self.main_lithology_groups:
            if main_lithology_group.contains_lithology_group(lithology_group):
                found_main_lithology_groups.append(main_lithology_group)
        return items_lookup_return(found_main_lithology_groups, True)

    def get_meta_parameter_group(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> MetaParameterGroup:
        """Gets the meta parameter group"""
        to_search = self.meta.meta_parameter_groups.copy()

        found_mpg = []
        while len(to_search) > 0:
            meta_parameter_group = to_search.pop()
            if meta_parameter_group.name == name or meta_parameter_group.id == id:
                found_mpg.append(meta_parameter_group)
            if meta_parameter_group.meta_parameter_groups is not None:
                to_search.extend(meta_parameter_group.meta_parameter_groups)

        n_mpg_found = len(found_mpg)
        if n_mpg_found == 0:
            return None, None
        elif n_mpg_found == 1:
            return found_mpg[0]
        else:
            raise LookupError("Multiple items found. Try searching by the unique id.")

    def get_meta_parameter(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> tuple[MetaParameter, MetaParameterGroup]:
        """Get meta parameter"""

        to_search = self.meta.meta_parameter_groups.copy()

        found_mp = []
        while len(to_search) > 0:
            meta_parameter_group = to_search.pop()
            if meta_parameter_group.meta_parameters is not None:
                for meta_parameter in meta_parameter_group.meta_parameters:
                    if meta_parameter.name == name or meta_parameter.id == id:
                        found_mp.append((meta_parameter, meta_parameter_group))
            if meta_parameter_group.meta_parameter_groups is not None:
                to_search.extend(meta_parameter_group.meta_parameter_groups)

        n_mp_found = len(found_mp)
        if n_mp_found == 0:
            return None, None
        elif n_mp_found == 1:
            return found_mp[0]
        else:
            raise LookupError("Multiple items found. Try searching by the unique id.")

    def get_lithology_parameter(self, lithology: str | Lithology, parameter_name: str):
        """Get lithology parameter"""
        if isinstance(lithology, str):
            lithology, _, _ = self.get_lithology(lithology_name=lithology)
        meta_parameter, _meta_parameter_group = self.get_meta_parameter(name=parameter_name)
        parameter = lithology.get_parameter(meta_parameter.id)

        return parameter

    def get_lithology_parameter_value(self, lithology: str | Lithology, parameter_name: str):
        """Gets the lithology parameter"""
        parameter = self.get_lithology_parameter(lithology=lithology, parameter_name=parameter_name)
        raw_value = parameter.value
        if parameter.is_curve:
            curve, cuve_group = self.get_curve(raw_value)
            value = curve.curve_table
        else:
            value = num_string_convert(raw_value)
        return value

    def update_lithology_parameter(
        self,
        lithology: str | Lithology,
        parameter_dict: dict[str, str],
    ):
        """Update lithology based on parameters provided by the user"""
        if isinstance(lithology, str):
            lithology, _lithology_group, _main_lithology_group = self.get_lithology(identifier=lithology)

        # Update
        for parameter_name, value in parameter_dict.items():
            meta_parameter, _meta_parameter_group = self.get_meta_parameter(name=parameter_name)
            parameter = lithology.get_parameter(id=meta_parameter.id)
            if parameter.is_curve:
                curve, curve_group = self.get_curve(id=parameter.meta_parameter_id)
                curve.set_curve_table(value)
            else:
                parameter.value = str(value)

    def duplicate_curve(
        self,
        source_curve: str | Curve,
        new_curve_name: str,
        curve_group: Optional[CurveGroup] = None,
    ) -> Curve:
        """Duplicates a curve"""
        if isinstance(source_curve, str):
            source_curve, curve_group = self.get_curve(source_curve)
        new_curve = source_curve.copy(deep=True)
        new_curve.name = new_curve_name
        new_curve.id = generate_new_id(self.curve_ids)

        # Add to curve group
        if curve_group is None:
            curve_group = self.get_curve_group_for_curve(source_curve)
        curve_group.curves.append(new_curve)
        return new_curve

    def duplicate_lithology(
        self,
        source_lithology: str | Lithology,
        new_lithology_name: str,
        lithology_group: Optional[str | LithologyGroup] = None,
        modifiable: bool = True,
    ):
        """Duplicate a lithology"""
        if isinstance(source_lithology, str):
            id, name = decode_id_and_name(source_lithology)
            source_lithology, lithology_group = self.get_lithology(id=id, name=name)

        new_lithology = source_lithology.copy(deep=True)
        new_lithology.name = new_lithology_name
        new_lithology.id = generate_new_id(self.lithology_ids)
        new_lithology.readonly = not modifiable

        # Create new curves
        for parameter_group in new_lithology.parameter_groups:
            for parameter in parameter_group.parameters:
                if parameter.is_curve:
                    pass

        if lithology_group is None:
            lithology_group, _main_lithology_group = self.get_lithology_group_for_lithology(source_lithology)
        lithology_group.lithologies.append(new_lithology)
        return new_lithology

    def create_lithology_group(
        self,
        source_lithology_group: str | LithologyGroup,
        new_name: str,
        main_lithology_group: Optional[str | MainLithologyGroup] = None,
    ) -> LithologyGroup:
        """Create a lithology group"""

        # Prepare
        if isinstance(source_lithology_group, str):
            source_lithology_group, _ = self.get_lithology_group(source_lithology_group)

        if main_lithology_group is None:
            main_lithology_group = self.get_main_lithology_group_for_lithology_group(source_lithology_group)
        if isinstance(main_lithology_group, str):
            main_lithology_group, _ = self.get_lithology_group(main_lithology_group)

        new_lithology_group = source_lithology_group.copy()
        new_lithology_group.name = new_name
        new_lithology_group.lithologies = None
        new_lithology_group.readonly = False
        new_lithology_group.id = generate_new_id(self.lithology_group_ids)

        main_lithology_group.lithology_groups.append(new_lithology_group)
        return new_lithology_group

    def create_main_lithology_group(
        self,
        source_main_lithology_group: MainLithologyGroup | str,
        new_name: str,
    ) -> MainLithologyGroup:
        """Create a main lithology group"""
        if isinstance(source_main_lithology_group, str):
            source_main_lithology_group = self.get_main_lithology_group(source_main_lithology_group)

        new_main_lithology_group = source_main_lithology_group.copy()
        new_main_lithology_group.id = generate_new_id(existing_ids=self.main_lithology_group_ids)
        new_main_lithology_group.lithology_groups = None
        new_main_lithology_group.name = new_name
        new_main_lithology_group.readonly = False
        self.main_lithology_groups.append(new_main_lithology_group)
        return new_main_lithology_group

    def delete_main_lithology_group(self, main_lithology_group: MainLithologyGroup | str) -> None:
        """Delete a main lithology group"""
        if isinstance(main_lithology_group, str):
            main_lithology_group = self.get_main_lithology_group(main_lithology_group)
        self.main_lithology_groups.remove(main_lithology_group)

    def delete_lithology_group(self, lithology_group: LithologyGroup | str) -> None:
        """Deletes a lithology group"""
        if isinstance(lithology_group, str):
            lithology_group, main_lithology_group = self.get_lithology_group(lithology_group)
        elif isinstance(lithology_group, LithologyGroup):
            main_lithology_group = self.get_main_lithology_group_for_lithology_group(lithology_group)

        main_lithology_group.lithology_groups.remove(lithology_group)

    def delete_lithology(self, lithology: Lithology | str) -> None:
        """Delete lithology"""
        if isinstance(lithology, str):
            lithology, lithology_group, _main_lithology_group = self.get_lithology(lithology)
        elif isinstance(lithology, Lithology):
            lithology_group = self.get_lithology_group_for_lithology(lithology)

        lithology_group.lithologies.remove(lithology)
