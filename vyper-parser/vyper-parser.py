import sys
import os
import logging
import pandas as pd
import numpy as np
import ast as python_ast
import json
import collections
import vyper.cli.vyper_compile as compiler
import pandas as pd
import numpy as np
import hashlib 


def getMethodIdentifiers(orderedDict):   
    for key, value in orderedDict.items():
        itemSTR = json.dumps(value)
        item = json.loads(itemSTR)
        if hasattr(item, 'get'): 
           return item.get("method_identifiers").keys()
    

if __name__ == '__main__':
    # create logger 
    log = logging.getLogger('vyper_parser')
    log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # create file handler which logs even debug messages
    fh = logging.FileHandler('vyper_parser.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)
    errors = 0
    count = 0
    methods = []
    items = dict()
    for root, dirs, files in os.walk("/mnt/c/projects/MasterThesis/contracts"):
        for file in files:
            if file.endswith(".py"):
                try:        
                    orderedDict = compiler.compile_files([os.path.join(root, file)],['combined_json'], show_gas_estimates=True, evm_version="istanbul")
                    result = getMethodIdentifiers(orderedDict)
                    methods.extend(result)
                    items[os.path.basename(root)] = result
                    count +=1
                except  Exception as error:
                    errors +=1
    log.error("Number of errors:"+ str(errors))
    if methods:
        val_methods=collections.Counter(methods)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            dn = pd.DataFrame.from_dict(val_methods, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()
            log.info(dn)

            log.info(items)
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