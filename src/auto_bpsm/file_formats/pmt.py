from pathlib import Path
import pandas as pd


class PetroModTable:
    start_comments: list[str] = []
    headers: list[str] = []
    format: str
    stop: str
    split_line: str
    table: pd.DataFrame

    filename: Path

    @staticmethod
    def line_to_data(line: str, prefix: str = None):
        if prefix:
            line = line.replace(prefix, "", 1)
        line = line.strip().removeprefix("|").removesuffix("|")
        data = line.split("|")
        data = [item.strip() for item in data]
        return data

    @staticmethod
    def data_to_line(data: list[str], prefix: str = None):
        data = [str(item) for item in data]
        line = " | ".join(data)
        if prefix:
            line = prefix + " | " + line
        else:
            line = "| " + line
        line = line + " |\n"
        return line

    @staticmethod
    def read_file(filename: Path):
        """Read a pma file"""

        try:
            with open(filename, "r", encoding="utf-8") as f:
                raw_pmt = f.readlines()
        except:
            with open(filename, "r", encoding="unicode_escape") as f:
                raw_pmt = f.readlines()

        # Comments
        i = 0
        is_start_comment = True
        start_comments = []
        while is_start_comment:
            if raw_pmt[i].startswith("c"):
                start_comments.append(raw_pmt[i])
                i = i + 1
            else:
                is_start_comment = False

        # Headers
        is_head = True
        headers = []
        while is_head:
            if raw_pmt[i].startswith("Head"):
                headers.append(PetroModTable.line_to_data(raw_pmt[i], "Head"))
                i = i + 1
            else:
                is_head = False

        # Key
        key = PetroModTable.line_to_data(raw_pmt[i], "Key")
        i = i + 1

        # Stop
        stop = raw_pmt[i]
        i = i + 1

        # Format
        format = PetroModTable.line_to_data(raw_pmt[i], "Format")
        i = i + 1

        # Split lines
        split_line = raw_pmt[i]
        i = i + 1

        # Data
        data = raw_pmt[i:]
        data = [line.replace("Data", "") for line in data]
        data_list = []
        for line in data:
            data_list.append(PetroModTable.line_to_data(line, "Data"))

        pmt_table = pd.DataFrame(data=data_list, columns=key)
        pmt = PetroModTable()
        pmt.start_comments = start_comments
        pmt.headers = headers
        pmt.format = format
        pmt.stop = stop
        pmt.split_line = split_line
        pmt.table = pmt_table
        pmt.filename = filename

        return pmt

    def save(self):
        """Saves the file back"""
        if not self.filename:
            raise FileExistsError
        self.write_file(self.filename)

    def write_file(self, filename: Path):
        """Write the files"""
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(self.start_comments)
            for header in self.headers:
                f.write(PetroModTable.data_to_line(header, "Head"))
            columns = self.table.columns
            f.write(PetroModTable.data_to_line(columns, "Key"))
            f.write(self.stop)
            f.write(PetroModTable.data_to_line(self.format, "Format"))
            f.write(self.split_line)
            data_list = self.table.values.tolist()
            for row in data_list:
                f.write(PetroModTable.data_to_line(row, "Data"))
