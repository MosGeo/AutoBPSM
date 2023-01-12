from typing import Any
from bs4.element import Tag
from bs4 import BeautifulSoup
from pydantic import BaseModel


def model_from_dict(class_type: BaseModel, xml_node: Tag, variables: list[str] = None, extra_dict: dict = {}):
    """Converts xml node to object"""

    # Default value
    if variables is None:
        variables = xml_node.findChildren(recursive=False)
    else:
        variables = xml_node.findChildren(variables, recursive=False)

    variables_dict = {field.name: field.string for field in variables}
    variables_dict.update(extra_dict)
    return class_type(**variables_dict)


def tag_from_model(class_instance: BaseModel, variables: list[str] = None) -> Tag:
    """Creates a tag from model"""

    print(class_instance.__fields__)
    if variables is None:
        variables = list(class_instance.__fields__.keys())

    soup = BeautifulSoup()
    tag = soup.new_tag(class_instance.__class__.__name__)

    for variable in variables:
        child_tag = soup.new_tag(name=variable)
        child_tag.string = class_instance.__getattribute__(variable)
        tag.append(child_tag)

    return tag
