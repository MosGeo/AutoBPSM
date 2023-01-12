from pathlib import Path
from pydantic import BaseModel
from bs4.element import Tag
from bs4 import BeautifulSoup
from auto_bpsm.models.helpers import model_from_dict, tag_from_model
from auto_bpsm.models.lithology.meta import Meta
from auto_bpsm.models.lithology.curve import CurveGroup
from auto_bpsm.models.lithology.litho import LithologyGroup


class Catalogue(BaseModel):
    Attributes: dict
    Name: str
    Version: str
    ReadOnly: str
    Meta: Meta
    CurveGroups: list[CurveGroup] = []
    LithologyGroups: list[LithologyGroup] = []

    _SIMPLE_VARIABLE_NAMES = ["Name", "Version", "ReadOnly"]

    def from_xml(xml_node: Tag):
        """from xml"""

        # Get meta
        meta_node = xml_node.findChild("Meta", recursive=False)
        meta = Meta.from_xml(meta_node)

        # Attributes
        attributes = xml_node.attrs

        extra_dict = {"Meta": meta, "Attributes": attributes}
        catalogue: Catalogue = model_from_dict(
            Catalogue, xml_node, Catalogue._SIMPLE_VARIABLE_NAMES, extra_dict=extra_dict
        )

        # Curve groups
        curve_group_nodes = xml_node.findChildren("CurveGroup", recursive=False)
        for curve_group_node in curve_group_nodes:
            curve_group = CurveGroup.from_xml(curve_group_node)
            catalogue.CurveGroups.append(curve_group)

        # Lithology groups
        lithology_group_nodes = xml_node.findChildren("LithologyGroup", recursive=False)
        for lithology_group_node in lithology_group_nodes:
            lithology_group = LithologyGroup.from_xml(lithology_group_node)
            catalogue.LithologyGroups.append(lithology_group)

        return catalogue

    def read_catalogue_file(filename: Path):
        with open(filename, "r") as f:
            file = f.read()

        soup = BeautifulSoup(file, "xml")
        catalogue_node = soup.findChild("Catalogue")
        catalogue: Catalogue = Catalogue.from_xml(catalogue_node)
        return catalogue

    def write_catalogue_file(self, filename: Path) -> None:
        soup = BeautifulSoup()

        catalogue_tag = tag_from_model(self, Catalogue._SIMPLE_VARIABLE_NAMES)
        catalogue_tag.attrs = self.Attributes

        meta_tag = self.Meta.to_xml()
        catalogue_tag.append(meta_tag)

        # Add it to the soup
        soup.append(catalogue_tag)

        # Write it to file
        with open(filename, "w") as f:
            f.write(soup.prettify())
