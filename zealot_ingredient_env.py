import os, shutil, subprocess
from sacred import Ingredient

env = Ingredient('env')

@env.config
def env_cfg():
    out = 'out'
    tmp = 'tmp'
    docker_image = None
    container_base_path = '/exp'
