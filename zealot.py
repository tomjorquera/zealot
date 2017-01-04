#!/usr/bin/python3
import sys, os, shutil, logging, git, re
from datetime import date
from sacred import Experiment, dependencies, arg_parser
from zealot_ingredient_env import env
from zealot_ingredient_env_basic import setup_env_basic
from zealot_ingredient_env_docker import setup_env_docker

# TODO allow to make accessible in the env (mount/link/...) a 'data' folder
#      (read-only if possible)
# TODO allow to download the experiment directly from a git repo instead of a
#      file path
# TODO rework system to create a 'safe' contained env where the original exp is
#      duplicated, and force 'out' and 'tmp' to be part of this env
#      => store all experiments in a 'experiments' folder, generate a new
#      subfolder for each new experiment
#      <path>/experiments
#                  |_ experiment_date_UUID
#                                  |_ steps
#                                  |_ out
#                                  |_ tmp

zealot = Experiment('Zealot', ingredients=[env])

##
# Global config
_git_storage = os.path.join(os.path.expanduser('~'), '.zealot_git_storage')

@zealot.config
def zealot_config():
    storage_folder = os.path.join(os.path.expanduser('~'), 'Experiments')
    log_level = 'INFO'
    git_url = None
    git_storage = _git_storage

def save_artifacts(zealot, base_path):
    for artifact in os.listdir(base_path):
        path = os.path.join(base_path, artifact)
        if os.path.isfile(path):
            zealot.add_artifact(path)
        else:
            save_artifacts(zealot, path)

@zealot.capture()
def setup_env(env):
    if env['docker_image'] is not None:
        return setup_env_docker()
    else:
        return setup_env_basic()

@zealot.capture()
def store_results(env, storage_folder, _seed):
    # TODO allow to optionally store artifacts created in tmp
    save_artifacts(zealot, os.path.join(os.getcwd(), env['out']))

    # store out artifacts in experiments folder
    shutil.copytree(os.path.join(os.getcwd(), env['out']),
                    os.path.join(storage_folder,
                                 os.path.basename(os.getcwd()) +
                                 '_' + str(date.today()) +
                                 '_' + str(_seed)))

def store_raw_source(filename):
    zealot.sources.add(dependencies.Source(filename, dependencies.get_digest(filename)))

@zealot.main
def main(env, _log):

    _log.info('preparing running env')
    running_env = setup_env()

    # get all steps and run them in order
    # TODO allow to optionally store steps as resources
    for step in [line.rstrip('\n') for line in open('steps.txt')]:
        _log.info('running step %s', step)
        store_raw_source(os.path.abspath(step))
        running_env.run(step)

    _log.info('all steps completed')

    # store artifacts generated in the out folder 
    _log.info('storing artifacts')
    store_results()

    # clean up and restore current working dir
    _log.info('cleaning up')
    running_env.close()

def clone_or_udpdate_git_repo(git_url, git_storage):
        project_name = re.search('.*/(.+?)\.git$', git_url).group(1)

        git_loc = os.path.join(git_storage, project_name)

        # clone repo if required
        if not os.path.exists(git_loc):
            git.Repo.clone_from(git_url,
                                git_loc,
                                depth=1)

        repo = git.Repo(git_loc)
        # update repo to latest version
        repo.remotes.origin.pull('master')
        return git_loc

if __name__ == '__main__':

    args = arg_parser.parse_args(sys.argv)
    conf_updates = arg_parser.get_config_updates(args['UPDATE'])

    if('git_url' in conf_updates[0]):
        # checkout/update repo, add ref to config, and go into working dir
        git_url = conf_updates[0]['git_url']
        git_loc = clone_or_udpdate_git_repo(git_url, _git_storage)
        zealot.add_config(git_rev = str(git.Repo(os.getcwd()).head.commit))
        os.chdir(git_loc)

    # add step files as sources
    for step in [line.rstrip('\n') for line in open(os.path.join(os.getcwd(), 'steps.txt'))]:
        store_raw_source(step)

    # run experiment
    zealot.run_commandline()
