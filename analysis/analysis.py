import docker
import logging
import argparse
import os
import sys
from datetime import timedelta
from multiprocessing import Pool, Value
from time import time, localtime, strftime
from cli import create_parser, TOOLS_CHOICES
from docker_api import analyse_files
from functools import partial
from solidity_parser import parser

output_folder = strftime("%Y%d%m_%H%M", localtime())


def analyse(log, args):
    global output_folder
    (tool, file, solc_version) = args

    try:
        start = time()

        log.info('Analysing file: ' + file)
        log.info('Tool: ' + tool)
        analyse_files(tool, file, log, output_folder,
                      solc_version)

        duration = str(timedelta(seconds=round(time() - start)))
        log.info('Completed ' + file + ' [' + tool + '] in ' + duration)
    except Exception as e:
        print(e)
        log.error(str(e))
        raise e


def get_solc_version(file, log):
    try:
        with open(file, 'r', encoding='utf-8') as fd:
            sourceUnit = parser.parse(fd.read())
            sourceUnitObject = parser.objectify(sourceUnit)
            pragmas = sourceUnitObject.pragmas
            solc_version = pragmas[0]['value']
            solc_version = solc_version.strip('^')
            return solc_version
    except:
        log.error(
            'WARNING: could not parse solidity file to get solc version')
    return "0.6.4"  # default version


def get_contract_names(file, log):
    try:
        contractNames = []
        with open(file, 'r', encoding='utf-8') as fd:
            sourceUnit = parser.parse(fd.read())
            sourceUnitObject = parser.objectify(sourceUnit)
            contract_names = sourceUnitObject.contracts.keys()
            res = [i for i in contract_names if i]
            contractNames.extend(res)
            return contractNames
    except:
        log.error(
            'WARNING: could not parse solidity file to get solc version')
    return None


def exec_cmd(args: argparse.Namespace):
    global log, output_folder
    log.info('Arguments passed: ' + str(sys.argv))

    files_to_analyze = []
    if args.tool == ['all']:
        TOOLS_CHOICES.remove('all')
        args.tool = TOOLS_CHOICES

    for file in args.file:
        # analyse files
        if os.path.basename(file).endswith('.sol'):
            files_to_analyze.append(file)
        # analyse dirs recursively
        elif os.path.isdir(file):
            for root, dirs, files in os.walk(file):
                for name in files:
                    if name.endswith('.sol'):
                        files_to_analyze.append(os.path.join(root, name))
        else:
            log.info('%s is not a directory or a solidity file' % file)

    for file in files_to_analyze:
        solc_version = get_solc_version(file, log)
        for tool in args.tool:
            results_folder = 'results/' + output_folder + '/' + tool
            if not os.path.exists(results_folder):
                os.makedirs(results_folder)
            analyse(log, (tool, file, solc_version))


if __name__ == '__main__':

    log = logging.getLogger('analysis')
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('analysis.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    args = create_parser()
    exec_cmd(args)
    log.info('Analysis completed.')
