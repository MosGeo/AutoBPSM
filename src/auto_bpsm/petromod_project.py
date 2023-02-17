from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal
import shutil
from auto_bpsm.file_formats.lithology_catalogue import LithologyCatalogue
from auto_bpsm.petromod_executables import PetroMod
from auto_bpsm.petromod_models import OneDimensionalModel, TwoDimensionalModel, ThreeDimensionalModel


@dataclass
class ValueRange:
    min: float
    max: float


MODEL_FOLDER_DICTIONARY = {"1D": "pm1d", "2D": "pm2d", "3D": "pm3d"}
MODEL_CLASS_DICTIONARY = {1: OneDimensionalModel, 2: TwoDimensionalModel, 3: ThreeDimensionalModel}


class PetroModProject:
    """A petromod project representation"""

    project_folder: Path
    petromod: PetroMod

    def __init__(self, project_folder: Path, petromod: PetroMod = None, petromod_folder_index: int = 0):
        """Initializes the project"""
        self.project_folder = project_folder
        self.petromod = petromod if petromod else PetroMod(petromod_folder_index=petromod_folder_index)

    def duplicate_model(
        self,
        source_model_name: str,
        distination_model_name: str,
        model_dimension: Annotated[int, ValueRange(1, 3)] = None,
    ) -> None:
        """creates a copy of a model"""
        source_folder = self.get_model_folder(source_model_name, model_dimension)
        if source_folder is None:
            return None
        distination_folder = Path(source_folder.parent, distination_model_name)
        shutil.copytree(source_folder, distination_folder)

    def list_models(self) -> dict[str, list[str]]:
        """List the models available in the project"""
        models_dict = {}
        for key, model_folder_name in MODEL_FOLDER_DICTIONARY.items():
            models_folder = Path(self.project_folder, model_folder_name)
            models_raw_filenames = list(models_folder.iterdir())
            models = [file.name for file in models_raw_filenames]
            models_dict[key] = models
        return models_dict

    def guess_model_dimension(self, model_name: str):
        """Returns teh model dimensions"""
        models_dict = self.list_models()
        possible_dimensions = []
        for i, (key, models) in enumerate(models_dict.items()):
            if model_name in models:
                possible_dimensions.append(i + 1)

        if len(possible_dimensions) != 1:
            return None
        return possible_dimensions[0]

    def get_model_folder(self, model_name: str, model_dimension: Annotated[int, ValueRange(1, 3)] = None):
        """Returns the model folder"""
        if model_dimension is None:
            model_dimension = self.guess_model_dimension(model_name)
        if model_dimension is None:
            print("Model could not be found or there are multiple models with the same name.")
            return None

        models_folder = MODEL_FOLDER_DICTIONARY[f"{str(model_dimension)}D"]
        model_folder = Path(self.project_folder, models_folder, model_name)
        if not model_folder.is_dir():
            return None
        return model_folder

    def load_model(self, model_name: str, model_dimension: Annotated[int, ValueRange(1, 3)] = None):
        """Loads a model"""
        # Model dimension
        model_folder = self.get_model_folder(model_name, model_dimension)
        model_dimension = int(str(model_folder.parent.name)[2])
        if model_folder is None:
            return None
        model_class = MODEL_CLASS_DICTIONARY[model_dimension]
        return model_class(model_folder)

    def load_lithology(self) -> LithologyCatalogue:
        """Load lithology file"""
        lithology_filename = Path(self.project_folder, "geo", "Lithologies.xml")
        lithology_catalouge = LithologyCatalogue.read_catalogue_file(lithology_filename)
        return lithology_catalouge

    def delete_model(self, model_name: str, model_dimension: Annotated[int, ValueRange(1, 3)] = None):
        """Deletes a model"""
        model_folder = self.get_model_folder(model_name, model_dimension)
        if model_folder is None:
            return None
        shutil.rmtree(model_folder)

    def run_model(self, model_name: str, model_dimension: Annotated[int, ValueRange(1, 3)] = None) -> str | None:
        """Runs a model"""
        # Model dimension
        model_folder = self.get_model_folder(model_name, model_dimension)
        if model_folder is None:
            return None
        log = self.petromod.call_hermes(model_folder)
        return log

    def run_script(
        self,
        script: Path,
        model_name: str,
        script_folder_type: Literal["pmhome", "pmproj", "none"] = "none",
        script_arguments: str = "",
        model_dimension: Annotated[int, ValueRange(1, 3)] = None,
    ) -> str | None:
        """Runs the script"""
        model_folder = self.get_model_folder(model_name, model_dimension)
        if model_folder is None:
            return None
        log = self.petromod.call_pmpy(
            model_folder=model_folder,
            script=script,
            script_folder_type=script_folder_type,
            script_arguments=script_arguments,
        )
        return log
