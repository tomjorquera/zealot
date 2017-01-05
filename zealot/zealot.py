#!/usr/bin/python3
import sys, os, shutil, logging, git, docker
from datetime import datetime
from sacred import Experiment, dependencies, arg_parser
from sacred.observers import MongoObserver
from ingredient.env import env
from ingredient.env_basic import setup_env_basic
from ingredient.env_docker import  setup_env_docker
from utils import *

zealot = Experiment('Zealot', ingredients=[env])

##
# Global config
_git_storage = os.path.join(os.path.expanduser('~'), '.zealot_git_storage')

@zealot.config
def zealot_config():
    storage_folder = os.path.join(os.path.expanduser('~'), 'Experiments')
    storage_time_format = '%Y-%m-%d_%H:%M:%S'
    log_level = 'INFO'
    git_url = None
    git_storage = _git_storage
    mongo_url = None
    mongo_db_name = 'zealot'

@zealot.capture()
def setup_env(env):
    if env['docker_image'] is not None:
        return setup_env_docker()
    else:
        return setup_env_basic()

@zealot.capture()
def store_results(env, storage_folder, storage_time_format, _seed):
    # TODO allow to optionally store artifacts created in tmp
    save_artifacts(zealot, os.path.join(os.getcwd(), env['out']))

    # store out artifacts in experiments folder
    shutil.copytree(os.path.join(os.getcwd(), env['out']),
                    os.path.join(storage_folder,
                                 os.path.basename(os.getcwd()) +
                                 '_' + datetime.now().strftime(storage_time_format) +
                                 '_' + str(_seed)))

@zealot.main
def main(env, _log, mongo_url, mongo_db_name):

    _log.info('preparing running env')
    running_env = setup_env()

    # get all steps and run them in order
    # TODO allow to optionally store steps as resources
    for step in [line.rstrip('\n') for line in open('steps.txt')]:
        _log.info('running step %s', step)
        store_raw_source(zealot, os.path.abspath(step))
        running_env.run(step)

    _log.info('all steps completed')

    # store artifacts generated in the out folder 
    _log.info('storing artifacts')
    store_results()

    # clean up and restore current working dir
    _log.info('cleaning up')
    running_env.close()

if __name__ == '__main__':
    # get config
    # TODO is there a way to avoid to do this?
    config = generate_config(zealot)

    if('git_url' in config and config['git_url'] is not None):
        # checkout/update repo, add ref to config, and go into working dir
        git_url = config['git_url']
        git_loc = clone_or_udpdate_git_repo(git_url, _git_storage)
        zealot.add_config(git_rev = str(git.Repo(os.getcwd()).head.commit))
        os.chdir(git_loc)

    # add step files as sources
    for step in [line.rstrip('\n') for line in
                 open(os.path.join(os.getcwd(), 'steps.txt'))]:
        store_raw_source(zealot, step)

    # check if experiment contains a dockerfile
    # TODO ask what to do when dockerfile + docker image in parameter?
    if os.path.exists('Dockerfile'):
        image_name = 'zealot_' + os.path.basename(os.getcwd())
        docker.from_env().images.build(path=os.getcwd(), tag=image_name)
        env.add_config(docker_image=image_name)

    # configure mongo observer if required
    if('mongo_url' in config and config['mongo_url'] is not None):
        zealot.observers.append(
            MongoObserver.create(config['mongo_url'],config['mongo_db_name']))

    # run experiment
    zealot.run_commandline()
