from typing import Literal, Optional
from pathlib import Path
import os
import subprocess

PETROMOD_DEFAULT_PARENT_FOLDER = Path(r"C:\Program Files\Schlumberger")


class PetroMod:
    petromod_binary_folder: Path

    def __init__(
        self,
        petromod_binary_folder: Path = None,
        petromod_folder_index: int = 0,
        petromod_parent_folder: Path = PETROMOD_DEFAULT_PARENT_FOLDER,
    ):
        """Initializes the petromod folder"""
        if petromod_binary_folder:
            self.petromod_binary_folder = petromod_binary_folder
        else:
            petromod_folders = PetroMod.get_petromod_folders(petromod_parent_folder)
            if len(petromod_folders) >= 1:
                self.petromod_binary_folder = petromod_folders[petromod_folder_index]

        # Raise if the folder does not exist
        if self.petromod_binary_folder is None:
            raise FileNotFoundError()

    def call_hermes(self, model_folder: Path):
        """Runs a model"""
        hermes_filename = Path(self.petromod_binary_folder, "hermes.exe")
        command = f'"{str(hermes_filename)}" -model "{str(model_folder.resolve())}"'
        log = PetroMod.run_command(command)
        return log

    def call_pmpy(
        self,
        model_folder: Path,
        script: Path | str,
        script_folder_type: Literal["pmhome", "pmproj", "none"] = "none",
        script_arguments: str = "",
    ):
        """Call a python script"""
        os.environ["PM_HOME"] = str(self.petromod_binary_folder.parent.parent)
        pmpy_filename = Path(self.petromod_binary_folder, "runpmpy.exe")
        command = f'"{str(pmpy_filename)}" -m "{str(model_folder.resolve())}" -scriptdir {script_folder_type} -script "{str(script)}" {str(script_arguments)}'
        log = PetroMod.run_command(command)
        return log

    @staticmethod
    def run_command(command: str) -> str:
        """Runs a commmand"""
        log = subprocess.getoutput(f"{command}")
        return log

    @staticmethod
    def get_petromod_folders(petromod_parent_folder: Path = PETROMOD_DEFAULT_PARENT_FOLDER) -> Optional[list[Path]]:
        """Returns the possible petromod folder"""
        possible_petromod_folders = list(petromod_parent_folder.glob(r"PetroMod */WIN64/bin"))
        if possible_petromod_folders:
            return possible_petromod_folders
        else:
            return None
