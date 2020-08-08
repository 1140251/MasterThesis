import sys
import os
import logging
from solidity_parser import parser
import collections
import pandas as pd
import numpy as np
import hashlib 

if __name__ == '__main__':
    # create logger 
    log = logging.getLogger('solidity_parser')
    log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # create file handler which logs even debug messages
    fh = logging.FileHandler('solidity_parser.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)
    contractNames = []
    items = dict()
    for root, dirs, files in os.walk("C:\projects\MasterThesis\contracts"):
        for file in files:
            if file.endswith(".sol"):
                try:
                    sourceUnit = parser.parse_file(os.path.join(root, file))
                    sourceUnitObject = parser.objectify(sourceUnit)
                    # sourceUnitObject.imports  # []
                    # sourceUnitObject.pragmas  # []
                    contract_names = sourceUnitObject.contracts.keys()  # get all contract names
                    res = [i for i in contract_names if i] 
                    contractNames.extend(res)

                    for key in res:
                        contract = sourceUnitObject.contracts[key]
                        if contract._node.kind == "contract":
                            contract_functions = contract.functions.keys()
                            resFunctions = [i for i in contract_names if i] 
                            items[os.path.basename(root) + "_" + key] = resFunctions
                except  Exception as error:
                    log.error("Error in file:" + file)
                    log.error("Path:"+os.path.join(root, file))
                    log.error(error)
    
    val_contract_names=collections.Counter(contractNames)
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    dn = pd.DataFrame.from_dict(val_contract_names, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()    
    log.info(dn)

    log.info("------Get Duplicated")
    log.info(len(items))
    test = [list(x) for x in set(tuple(x) for x in items.values())]
    log.info(len(test))

    rev_dict = {} 
    # finding duplicate values 
    # from dictionary using flip 
    flipped = {} 
    for key, value in items.items(): 
        ls = sorted(value) 
        print(ls)
        result = hashlib.sha256(str(ls).encode()).hexdigest()
        if result not in flipped: 
            flipped[result] = [key] 
        else: 
            flipped[result].append(key) 

    # printing result 
    for key, value in flipped.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if len(value) > 1:
            log.info(value)

