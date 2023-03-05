from pathlib import Path
from auto_bpsm.file_formats.lithology_catalogue import LithologyCatalogue
from auto_bpsm.file_formats.pmt import PetroModTable
from auto_bpsm.file_formats.pma import PetroModASCII

IN_FILENAMES = {
    "mckenzie_heat_flow_options": "mckenzie/riftphases.pmt",
    "global_coordinates": "ggxy.pmt",
    "heat_flow": "in1d_hf.pmt",
    "paleowater_depth": "in1d_pwd.pmt",
    "sediment_water_interface_temperature": "in1d_swit.pmt",
    "depostion_history": "main1d.pmt",
    "output_ages": "outa.pmt",
    "auto_sediment_water_interface_temperature": "swio.pmt",
    "well_assignment": "wellassignment.pmt",
    "tools_options": "tool.pmt",
}

DEF_FILENAMES = {
    "mckenzie_heat_flow_options": "mckenziehf_opts.pma",
    "simulation_options": "proj.pma",
}


class PetroModModel:
    """PetroMod model"""

    model_name: str
    model_folder: str


class OneDimensionalModel:
    """One dimenstional model"""

    # Model
    model_name: str
    model_folder: Path

    # Options
    mckenzie_heat_flow_options: PetroModASCII
    simulation_options: PetroModASCII
    tools_options: PetroModTable

    # Inputs
    mckenzie_rift_phases: PetroModTable
    global_coordinates: PetroModTable
    heat_flow: PetroModTable
    paleowater_depth: PetroModTable
    sediment_water_interface_temperature: PetroModTable
    depostion_history: PetroModTable
    output_ages: PetroModTable
    auto_sediment_water_interface_temperature: PetroModTable
    well_assignment: PetroModTable

    def __init__(self, model_folder: Path):
        """Loads a model"""
        self.model_name = model_folder.name
        self.model_folder = model_folder

        for variable, file in IN_FILENAMES.items():
            filename = Path(self.model_folder, "in", file)
            self.__setattr__(variable, PetroModTable.read_file(filename))

        for variable, file in DEF_FILENAMES.items():
            filename = Path(self.model_folder, "def", file)
            self.__setattr__(variable, PetroModASCII.read_file(filename))

    def save_model(self):
        """Saves the model back"""
        for variable, file in IN_FILENAMES.items():
            filename = Path(self.model_folder, "in", file)
            pmt: PetroModTable = self.__getattribute__(variable)
            pmt.write_file(filename)

        for variable, file in DEF_FILENAMES.items():
            filename = Path(self.model_folder, "def", file)
            pma: PetroModASCII = self.__getattribute__(variable)
            pma.write_file(filename)


class TwoDimensionalModel:
    ...


class ThreeDimensionalModel:
    ...
