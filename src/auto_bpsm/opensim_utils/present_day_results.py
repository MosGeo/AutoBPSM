from pathlib import Path
import re
import pandas as pd
import numpy as np
from auto_bpsm.petromod_project import PetroModProject


def get_layers_indecies(project: PetroModProject, model_name: str):
    """Get layers indecies"""
    log = project.run_script(
        model_name=model_name,
        script="demo_opensim_output_3rd_party_format.py",
        script_folder_type="pmhome",
        script_arguments="-1",
    )

    lines = log.split("\n")
    lines = [line.strip() for line in lines]
    lines = [re.sub(" +", " ", line) for line in lines]

    layers = []
    is_data = False
    for line in lines:
        if line == "Number Name":
            is_data = True
            continue
        if is_data == False:
            continue
        layers.append(line.split(maxsplit=1))

    layer_table = pd.DataFrame(data=layers, columns=["Index", "Layer"])
    return layer_table


def get_layer_data(project: PetroModProject, model_name: str, layer_index) -> tuple[str, str, pd.DataFrame]:
    """Gets the layer data using the demo script"""
    log = project.run_script(
        model_name=model_name,
        script="demo_opensim_output_3rd_party_format.py",
        script_folder_type="pmhome",
        script_arguments=str(layer_index),
    )

    filename = Path("./demo_1.txt")
    with open(filename, "r") as f:
        lines = f.readlines()

    layer_name = lines[4].split(":")[1].strip()
    layer_unit = lines[5].split(":")[1].strip()

    data_raw = [line.strip().split() for line in lines[8:]]

    data = pd.DataFrame(data=data_raw, columns=["Element", "Value"])

    return layer_name, layer_unit, data


def get_layer_data_table(project, model_name, layer_names) -> pd.DataFrame:
    """Get data quickly"""
    layer_data_dict = {}
    output_layter_table = get_layers_indecies(project, model_name)
    for layer_name in layer_names:
        layer_index = output_layter_table[output_layter_table["Layer"] == layer_name]["Index"].values[0]
        column_values = get_layer_data(project, model_name, layer_index)[2].values[:, 1]
        layer_data_dict[layer_name] = np.flip(column_values)

    data_table = pd.DataFrame(layer_data_dict).astype(float)
    return data_table
