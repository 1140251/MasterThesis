import re
from parsers.Parser import Parser
import json


class Securify(Parser):
    def __init__(self):
        pass

    def parse(self, str_output):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        result = ansi_escape.sub('', str_output)
        try:
            data = json.loads(result)
            return data
        except Exception as e:
            data = result.splitlines()
            string = "stderr"
            value = -1
            for s in data:
                if string in str(s):
                    value = data.index(s)
            if(value != -1):
                result = data[value + 1]
                if('error' in result and 'sources' in result):
                    return json.loads(result)
                else:
                    return ''
            else:
                map(str.strip, data)
                output = []
                for index, line in enumerate(data):
                    if "Severity:" in line:
                        jsonResponse = {
                            "Severity": line.replace("Severity:", '').strip(),
                            "Pattern": "",
                            "Description": "",
                            "Type": "",
                            "Contract": "",
                            "Line": ""
                        }

                    elif "Pattern:" in line:
                        line = line.replace("Pattern:", '')
                        jsonResponse['Pattern'] = line.strip()
                    elif "Description:" in line:
                        lineContent = line.replace("Description:", '')
                        description = []
                        description.append(lineContent.strip())
                        index = data.index(line) + 1
                        for descriptionLine in data[index:]:
                            if "Type:" in descriptionLine:
                                break
                            description.append(descriptionLine.strip())
                        jsonResponse['Description'] = description
                    elif "Type:" in line:
                        line = line.replace("Type:", '')
                        jsonResponse['Type'] = line.strip()
                    elif "Contract:" in line:
                        line = line.replace("Contract:", '')
                        jsonResponse['Contract'] = line.strip()
                    elif "Line:" in line:
                        line = line.replace("Line:", '')
                        jsonResponse['Line'] = line.strip()
                        output.append(jsonResponse)
                return output
