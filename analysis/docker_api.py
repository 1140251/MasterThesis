import docker
import logging
import yaml
import os
import sys
import json
import tarfile
import re
from parsers.Manticore import Manticore
from parsers.Mythril import Mythril
from parsers.Oyente import Oyente
from parsers.Securify import Securify
from parsers.Smartcheck import Smartcheck
from parsers.Solhint import Solhint
from parsers.Verisol import Verisol
from time import gmtime, strftime, time
from distutils.dir_util import copy_tree
import shutil
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

client = docker.from_env()


def pull_image(dockerfile_path, image_tag, log, filesDir, solc_version):
    try:
        print('pulling ' + image_tag + ' image, this may take a while...')
        log.info('pulling ' + image_tag + ' image, this may take a while...')
        # dest_dir = os.path.join(dockerfile_path, filesDir)
        # shutil.rmtree(dest_dir, True)
        # os.mkdir(dest_dir)
        # copy_tree(os.path.abspath(filesDir),
        #           dest_dir, preserve_mode=0, update=1)

        (image, _) = client.images.build(
            path=dockerfile_path, tag=image_tag, rm=False, quiet=False)
        print('image pulled')
        log.info('image pulled')
        return image

    except (docker.errors.APIError, docker.errors.BuildError, TypeError) as err:
        print(err)
        log.error(err)
        raise err


def mount_volumes(dir_path, log):
    try:
        volume_bindings = {os.path.abspath(
            dir_path): {'bind': '/' + dir_path, 'mode': 'rw'}}
        return volume_bindings
    except os.error as err:
        print(err)
        log.error(str(err))


def stop_container(container, log):
    try:
        if container is not None:
            container.stop(timeout=0)
    except (docker.errors.APIError) as err:
        print(err)
        log.error(str(err))


def remove_container(container, log):
    try:
        if container is not None:
            container.remove()
    except (docker.errors.APIError) as err:
        print(err)
        log.error(str(err))


def parse_results(output, tool, file_name, container, log, results_folder, start, end, cfg):
    output_folder = os.path.join(results_folder, file_name)

    results = {
        'contract': file_name,
        'tool': tool,
        'start': start,
        'end': end,
        'duration': end - start,
        'analysis': None
    }
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(os.path.join(output_folder, 'result.log'), 'w', encoding='utf-8') as f:
        f.write(output)

    if 'output_in_files' in cfg:
        try:
            with open(os.path.join(output_folder, 'result.tar'), 'wb') as f:
                output_in_file = cfg['output_in_files']['folder']
                bits, _ = container.get_archive(output_in_file)
                for chunk in bits:
                    f.write(chunk)
        except Exception as e:
            print(output)
            print(e)
            print(
                '\x1b[1;31m' + 'ERROR: could not get file from container. file not analysed.' + '\x1b[0m')
            log.error(
                'ERROR: could not get file from container. file not analysed.')

    with open(os.path.join(output_folder, 'result.json'), 'w') as f:
        try:
            if tool == 'manticore':
                if os.path.exists(os.path.join(output_folder, 'result.tar')):
                    tar = tarfile.open(os.path.join(
                        output_folder, 'result.tar'))
                    m = re.findall('Results in /(mcore_.+)', output)
                    results['analysis'] = []
                    for fout in m:
                        output_file = tar.extractfile(
                            'results/global.findings')
                        results['analysis'].append(Manticore().parse(
                            output_file.read().decode('utf8')))
            elif tool == 'mythril':
                results['analysis'] = Mythril().parse(output)
            elif tool == 'oyente':
                results['analysis'] = Oyente().parse(output)
            elif tool == 'securify':
                results['analysis'] = Securify().parse(output)
            elif tool == 'slither':
                if os.path.exists(os.path.join(output_folder, 'result.tar')):
                    tar = tarfile.open(os.path.join(
                        output_folder, 'result.tar'))
                    output_file = tar.extractfile('output.json')
                    results['analysis'] = json.loads(output_file.read())
            elif tool == 'smartcheck':
                results['analysis'] = Smartcheck().parse(output)
            elif tool == 'solhint':
                results['analysis'] = Solhint().parse(output)
            elif tool == 'verisol':
                if os.path.exists(os.path.join(output_folder, 'result.tar')):
                    try:
                        tar = tarfile.open(os.path.join(
                            output_folder, 'result.tar'))
                        output_file = tar.extractfile('corral.txt')
                        output_result = output_file.read()
                        results['analysis'] = str(output_result)
                    except Exception as e:
                        results['analysis'] = Verisol().parse(output)
                        pass
        except Exception as e:
            print(output)
            print(e)
            # ignore
            pass

        json.dump(results, f, indent=2)


def analyse_files(tool, file, log, now, solc_version):
    try:
        toolFolder = 'tools/' + tool
        cfg_path = os.path.abspath(toolFolder + '/' + tool + '.yaml')

        if not os.path.exists(cfg_path):
            log.error(tool + ': config yaml file not provided.')
            sys.exit()

        if not os.path.exists(toolFolder + '/Dockerfile'):
            log.error(tool + ': Dockerfile not provided.')
            sys.exit()

        with open(cfg_path, 'r', encoding='utf-8') as ymlfile:
            try:
                cfg = yaml.safe_load(ymlfile)
            except yaml.YAMLError as exc:
                log.info(exc)

        if 'level' not in cfg or cfg['level'] == None:
            log.error(
                tool + ': level not provided. please check you config file.')
            sys.exit()

        if 'cmd' not in cfg or cfg['cmd'] == None:
            log.error(
                tool + ': commands not provided. please check you config file.')
            sys.exit()

        # create result folder with time
        results_folder = 'results/' + now + '/' + tool
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        # bind directory path instead of file path to allow imports in the same directory
        volume_bindings = mount_volumes(os.path.dirname(file), log)

        file_name = os.path.basename(file)
        file_name = os.path.splitext(file_name)[0]

        start = time()

        if not client.images.list(tool):
            image = pull_image('tools/'+tool, 'eth-tools/' +
                               tool, log, os.path.dirname(file), solc_version)
        else:
            image = client.images.get(tool)

        cmd = cfg['cmd']

        level = cfg['level']
        if level == 'bytecode':
            file = file.replace('.sol', '.bytecode')

        if '{version}' in cmd:
            cmd = cmd.replace('{version}', solc_version)
        if '{contract}' in cmd:
            cmd = cmd.replace('{contract}', '/' + file.replace('\\', '/'))
        else:
            cmd += ' /' + file.replace('\\', '/')
        container = None
        try:
            container = client.containers.run(image,
                                              cmd,
                                              detach=True,
                                              # cpu_quota=150000,
                                              volumes=volume_bindings)
            try:
                container.wait(timeout=(30 * 80))
            except Exception as e:
                pass
            output = container.logs().decode('utf8').strip()
            if (output.count('compilation failed') >= 1):
                log.error(
                    'ERROR: Solc experienced a fatal error. Check the results file for more info\n')

            end = time()

            parse_results(output, tool, file_name, container,
                          log, results_folder, start, end, cfg)
        finally:
            stop_container(container, log)
            remove_container(container, log)

    except (docker.errors.APIError, docker.errors.ContainerError, docker.errors.ImageNotFound) as err:
        print(err)
        log.error(err)
