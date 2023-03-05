from pathlib import Path


class PetroModASCII(dict):
    """A PMA file"""

    filename: Path

    @staticmethod
    def read_file(filename: Path):
        """Read a pma file"""
        with open(filename, "r", encoding="utf-8") as f:
            raw_pma = f.readlines()

        pma = PetroModASCII()
        for line in raw_pma:
            line = line.strip()
            if line == "":
                continue
            key, value = line.split(maxsplit=1)
            pma[key] = value

        pma.filename = filename

        return pma

    def save(self):
        """Saves the file back"""
        if not self.filename:
            raise FileExistsError
        self.write_file(self.filename)

    def write_file(self, filname: Path) -> None:
        """Writes the pma file"""
        lines = []
        for key, value in self.items():
            lines.append(f"{str(key)} {str(value)}\n")
        with open(filname, "w", encoding="utf-8") as f:
            f.writelines(lines)
