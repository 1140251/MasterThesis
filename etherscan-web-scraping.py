import requests
import xlrd
import os
import time
import json
import shutil
import collections
import logging
import sys
import pandas as pd
import numpy as np
REQUESTS_HEADERS = {
    "User-Agent": "https://github.com/AndreMiras/pyetheroll",
}
def export(contracts, API_url, API_key, contracts_downloaded):
    log.info("------Starting requests for" + API_url)
    contracts_not_downloaded = []
    for i in range(1, len(contracts)):  
        if i % 5 == 0:
            time.sleep(2)


        URL = 'https://'+API_url+'/api?module=contract&action=getsourcecode&address=' + \
            contracts[i] + '&apikey='+ API_key
        response = requests.get(URL, headers=REQUESTS_HEADERS)
        if response:
            data = response.json()
            log.info(contracts[i])
            if int(data["status"]) == 1:
                result = data["result"][0]
                contractName = result["ContractName"]
                ABI = result["ABI"]
                sourceCode = result["SourceCode"]

                log.info("Name:"+contractName)
                if contractName and contractName.strip():
                    compilerVersion = result["CompilerVersion"]
                    try:
                        os.makedirs("./contracts/" + contracts[i], exist_ok=False)
                        log.info("Creating Folder...")
                        f = open("./contracts/" + contracts[i] + "/abi.json", "w", encoding="utf-8")
                        f.write(ABI)
                        f.close()
                        log.info("Creating ABI...")
                        try:
                            jsonSourceCode = json.loads(sourceCode)
                            try:
                                log.info("Adding SourceCode...")
                                contracts_downloaded.append(tuple([contracts[i], contractName, compilerVersion, "selenium", "multiple", API_url]))

                                for file in jsonSourceCode:
                                    e = open("./contracts/" + contracts[i] + "/"+ file, "w", encoding="utf-8")
                                    e.write(jsonSourceCode[file]["content"])
                                    e.close()
                            except  Exception as error:
                                log.info("Removing folder... " + contracts[i])
                                shutil.rmtree("./contracts/" + contracts[i])
                                raise(error)
                        except json.JSONDecodeError:
                            if "vyper" in result["CompilerVersion"]:
                                extension = "py"
                                contracts_downloaded.append(tuple([contracts[i], contractName, compilerVersion, "vyper", "single", API_url]))
                            else:
                                extension = "sol"
                                contracts_downloaded.append(tuple([contracts[i], contractName, compilerVersion, "selenium", "single", API_url]))
                            try:
                                log.info("Adding SourceCode...")

                                d = open("./contracts/" + contracts[i] + "/"+contractName+"." + extension, "w", encoding="utf-8")
                                d.write(sourceCode)
                                d.close()
                            except Exception as error:
                                log.info("Removing folder... " + contracts[i])
                                shutil.rmtree("./contracts/" + contracts[i])
                                raise(error)
                    except FileExistsError:
                        # directory already exists
                        log.info("NOT DOWNLOADED:"+ contracts[i])
                        contracts_not_downloaded.append(contracts[i])
                        pass
                    log.info("Completed")
                else:
                    log.info("INVALID CONTRACT_NAME FOR:"+ contracts[i])
                    contracts_not_downloaded.append(contracts[i])
            else:
                log.info("NOT FOUND:" + contracts[i])
                contracts_not_downloaded.append(contracts[i])
        else:
            log.info("request error:" + contracts[i])
            contracts_not_downloaded.append(contracts[i])
    log.info("------Ending requests for" + API_url)
    return contracts_not_downloaded


if __name__ == '__main__':
    # create logger 
    log = logging.getLogger('scan_scraping')
    log.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # create file handler which logs even debug messages
    fh = logging.FileHandler('scan.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    loc = ("./export-verified-contractaddress.xlsx")

    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)

    contracts = []
    for i in range(1, sheet.nrows):
        contracts.append(sheet.cell_value(i, 0).strip())

    contracts_downloaded = []
    contracts_not_downloaded_yet = []
    contracts_not_downloaded_yet = export(contracts, 'api.etherscan.io', '3EUHGMN7XGMM5YKJ6T98SV7H652CFD1PDB', contracts_downloaded)
    contracts_not_downloaded_yet = export(contracts_not_downloaded_yet, 'api-ropsten.etherscan.io', '3EMT1YG847RZYJMH3GGZ6Z8B4KH75DGPPC', contracts_downloaded)
    contracts_not_downloaded_yet = export(contracts_not_downloaded_yet, 'api-kovan.etherscan.io', '3EUHGMN7XGMM5YKJ6T98SV7H652CFD1PDB',contracts_downloaded)
    contracts_not_downloaded_yet = export(contracts_not_downloaded_yet, 'api-rinkeby.etherscan.io', '3EUHGMN7XGMM5YKJ6T98SV7H652CFD1PDB', contracts_downloaded)
    contracts_not_downloaded_yet = export(contracts_not_downloaded_yet, 'api-goerli.etherscan.io', '3EUHGMN7XGMM5YKJ6T98SV7H652CFD1PDB', contracts_downloaded)

    log.info("Downloaded:"+ str(len(contracts_downloaded)))
    log.info("Contract not downloaded:" + str(len(contracts_not_downloaded_yet)))
    val_contract_file_names=collections.Counter([y for (x,y,z,n,m,l) in contracts_downloaded])
    val_contract_Versions=collections.Counter([z for (x,y,z,n,m,l) in contracts_downloaded])
    val_contract_Languages=collections.Counter([n for (x,y,z,n,m,l) in contracts_downloaded])
    val_contract_Files=collections.Counter([m for (x,y,z,n,m,l) in contracts_downloaded])
    val_api=collections.Counter([l for (x,y,z,n,m,l) in contracts_downloaded])
with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also

    log.info("------Contract File Names")
    dn = pd.DataFrame.from_dict(val_contract_file_names, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()
    log.info(dn)
    log.info("------Compiler Version")
    dv = pd.DataFrame.from_dict(val_contract_Versions, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()
    log.info(dv)
    log.info("------Language")
    dl = pd.DataFrame.from_dict(val_contract_Languages, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()
    log.info(dl)

    log.info("------Number Files")
    df = pd.DataFrame.from_dict(val_contract_Files, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()
    log.info(df)
    log.info("------Downloaded API")
    da = pd.DataFrame.from_dict(val_api, orient='index', columns=['Count']).sort_values(by=['Count']).reset_index()
    log.info(da)
    log.info("------Complete Table")
    dt = pd.DataFrame.from_dict(contracts_downloaded,columns = ["Contract", "Name", "CompilerVersion", "Language", "NumberFiles", "API"])
    log.info(dt)

    log.info(contracts_not_downloaded_yet)

    for handler in log.handlers:
        handler.close()
        log.removeFilter(handler)


        
