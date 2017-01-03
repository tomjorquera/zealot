import os, shutil, subprocess
from zealot_ingredient_env import env

class Env:
    @env.capture
    def __init__(self, out, tmp):
        # create out and tmp folders
        # TODO allow to force creation even if folders exist
        os.makedirs(out)
        os.makedirs(tmp)
        # set env variables
        self.env_vars = dict(os.environ)
        self.env_vars['ZEALOT_OUT'] = out
        self.env_vars['ZEALOT_TMP'] = tmp

    def run(self, command):
        # run the shell command with env variables
        subprocess.run([os.path.join(os.getcwd(), command)], env=self.env_vars)

    @env.capture
    def close(self, out, tmp):
        # TODO allow to preserve tmp
        # TODO allow to preserve out
        shutil.rmtree(tmp)
        shutil.rmtree(out)

def setup_env_basic():
    return Env()

