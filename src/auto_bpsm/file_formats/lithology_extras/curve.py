from typing import Optional
from pydantic_xml import BaseXmlModel, element
import pandas as pd

from auto_bpsm.utilities import decode_id_and_name, items_lookup_return

# from typing_extensions import Self
# from copy import deepcopy


class CurvePoint(BaseXmlModel):
    """Point"""

    x: float = element(tag="X")
    y: float = element(tag="Y")


class Curve(BaseXmlModel):
    """Curve"""

    id: str = element(tag="Id")
    name: str = element(tag="Name")
    creator: Optional[str] = element(tag="Creator")
    readonly: str = element(tag="ReadOnly")
    petrel_template_x: str = element(tag="PetrelTemplateX")
    petrel_template_y: str = element(tag="PetrelTemplateY")
    petromod_unit_x: str = element(tag="PetroModUnitX")
    petromod_unit_y: str = element(tag="PetroModUnitY")
    petromod_id: str = element(tag="PetroModId")
    curve_points: list[CurvePoint] = element(tag="CurvePoint")

    @property
    def curve_table(self) -> pd.DataFrame:
        """Get teh curve table"""
        x_values = []
        y_values = []
        for curve_point in self.curve_points:
            x_values.append(curve_point.x)
            y_values.append(curve_point.y)

        table = pd.DataFrame.from_dict({"x": x_values, "y": y_values})
        return table

    def set_curve_table(self, table: pd.DataFrame) -> None:
        """Sets the curves points from table"""
        curve_points = []
        for row in table.iterrows():
            x = row[1].x
            y = row[1].y
            curve_point = CurvePoint(x=x, y=y)
            curve_points.append(curve_point)

        self.curve_points = curve_points


class CurveGroup(BaseXmlModel):
    """Curve groups"""

    id: str = element(tag="Id")
    name: str = element(tag="Name")
    readonly: str = element(tag="ReadOnly")
    curves: list[Curve] = element(tag="Curve", default_factory=list)

    @property
    def curve_ids(self) -> list[str]:
        """Returns all the ids of the curves in the curve group"""
        ids = []
        for curve in self.curves:
            ids.append(curve.id)
        return ids

    def get_curves(
        self,
        identifier: str,
        is_unique: bool = False,
    ) -> Curve | list[Curve]:
        """Return curves found"""
        id, name = decode_id_and_name(identifier)
        found_curves = []
        for curve in self.curves:
            if curve.name == name or curve.id == id:
                found_curves.append([curve, self])
        return items_lookup_return(found_curves, is_unique)

    def contains_curve(self, curve: Curve):
        """Returns the curve group for the curve"""
        return curve in self.curves
