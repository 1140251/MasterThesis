import re
from parsers.Parser import Parser
import json


class Mythril(Parser):
    def __init__(self):
        pass

    def parse(self, str_output):

        try:
            data = json.loads(str_output)
            return data
        except Exception as e:
            data = str_output.splitlines()
            result = data[-1]
            return json.loads(result)
