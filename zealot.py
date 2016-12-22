import os
from sacred import Experiment
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

@zealot.config
def zealot_config():
    exp_folder = None
    step_prefix = ''

def save_artifacts(zealot, base_path):
    for artifact in os.listdir(base_path):
        path = os.path.join(base_path, artifact)
        if os.path.isfile(path):
            zealot.add_artifact(path)
        else:
            save_artifacts(path)

@zealot.capture()
def setup_env(env, exp_folder):
    if env['type'] == 'docker':
        if env['docker_image'] == None:
            raise ValueError('you must provide a docker image using the "docker_image" parameter')
        return setup_env_docker(exp_folder)
    else:
        return setup_env_basic()

@zealot.automain
def main(env, _log, exp_folder, step_prefix):

    if exp_folder is None:
        raise ValueError('you must provide a path for the experiment using the "exp_folder" parameter')

    # change current dir and set env
    _log.info('changing working dir to %s', exp_folder)
    os.chdir(exp_folder)

    _log.info('preparing running env')
    running_env = setup_env()

    # get all steps and run them in order
    # TODO allow to optionally store steps as resources
    steps = [file for file in os.listdir(os.getcwd()) if file.startswith(step_prefix)]
    for step in sorted(steps):
        _log.info('running step %s', step)
        running_env.run(step)

    _log.info('all steps completed')

    # store artifacts generated in the out folder 
    _log.info('storing artifacts')
    # TODO allow to optionally store artifacts created in tmp
    save_artifacts(zealot, os.path.join(os.getcwd(), env['out']))

    # clean up and restore current working dir
    _log.info('cleaning up')
    running_env.close()
