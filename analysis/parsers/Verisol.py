import re
from parsers.Parser import Parser


class Verisol(Parser):
    def __init__(self):
        pass

    def parse(self, str_output):
        output = []
        lines = str_output.splitlines()
        for line in lines:
            if "VeriSol translation error" in line:
                output.append(line)
            if "SyntaxError:" in line:
                output.append(line)
            if "ParserError:" in line:
                output.append(line)
            if "Warning!!:" in line:
                result = line.split(":")
                output.append(result[1])

        return output
