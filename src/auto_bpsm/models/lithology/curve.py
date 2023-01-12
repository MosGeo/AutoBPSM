from pydantic import BaseModel
from bs4.element import Tag
from auto_bpsm.models.helpers import model_from_dict


class CurvePoint(BaseModel):
    X: float
    Y: float


class Curve(BaseModel):
    """Curve"""

    Id: str
    Name: str
    ReadOnly: str
    PetrelTemplateX: str
    PetrelTemplateY: str
    PetroModUnitX: str
    PetroModUnitY: str
    PetroModId = str
    CurvePoints: list[CurvePoint] = []

    def from_xml(xml_node: Tag):
        variables = list(Curve.__fields__.keys())
        variables.remove("CurvePoints")
        curve: Curve = model_from_dict(Curve, xml_node, variables)
        curve_point_nodes = xml_node.findChildren("CurvePoint", recursive=False)
        for curve_point_node in curve_point_nodes:
            curve_point = model_from_dict(CurvePoint, curve_point_node)
            curve.CurvePoints.append(curve_point)
        return curve


class CurveGroup(BaseModel):
    Id: str
    Name: str
    ReadOnly: str
    Curves: list[Curve] = []

    def from_xml(xml_node: Tag):

        variables = list(CurveGroup.__fields__.keys())
        variables.remove("Curves")
        curve_group: CurveGroup = model_from_dict(CurveGroup, xml_node, variables)

        curve_nodes = xml_node.findChildren("Curve", recursive=False)
        for curve_node in curve_nodes:
            curve_group.Curves.append(Curve.from_xml(curve_node))

        return curve_group
