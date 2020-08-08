
#!/usr/bin/env python3
import logging
import argparse
import os
import sys

TOOLS_CHOICES = ['all']
CONFIG_TOOLS_PATH = os.path.abspath('tools')


def create_parser():
    parser = argparse.ArgumentParser(
        description="Static analysis of Ethereum smart contracts")
    group_source_files = parser.add_mutually_exclusive_group(required='True')
    group_tools = parser.add_mutually_exclusive_group(required='True')
    parser._optionals.title = "options:"
    # get tools available by parsing the name of the config files
    tools = [os.path.splitext(f)[0] for f in os.listdir(CONFIG_TOOLS_PATH)]
    for tool in tools:
        TOOLS_CHOICES.append(tool)

    group_source_files.add_argument('-f',
                                    '--file',
                                    nargs='*',
                                    default=[],
                                    help='select solidity file(s) or directories to be analysed')
    group_tools.add_argument('-t',
                             '--tool',
                             choices=TOOLS_CHOICES,
                             nargs='+',
                             help='select tool(s)')
    # required=True)

    args = parser.parse_args()
    return(args)
