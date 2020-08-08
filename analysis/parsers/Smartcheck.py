import re
from parsers.Parser import Parser


class Smartcheck(Parser):
    def __init__(self):
        pass

    def extract_result_line(self, line):
        index_split = line.index(":")
        key = line[:index_split]
        value = line[index_split + 1:].strip()
        if value.isdigit():
            value = int(value)
        return (key, value)

    def parse(self, str_output):
        output = []
        current_error = {}
        lines = str_output.splitlines()
        for line in lines:
            if "severity:" in line:
                values = line.split()
                (_, severity) = self.extract_result_line(values[1])
                current_error = {
                    'lines': values[0],
                    'severity': severity,
                    "error": " ".join(str(x) for x in values[2:])
                }
                output.append(current_error)
        return output
