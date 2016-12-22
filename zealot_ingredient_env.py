import os, shutil, subprocess
from sacred import Ingredient

env = Ingredient('env')

@env.config
def env_cfg():
    out = 'out'
    tmp = 'tmp'
    type = None
    docker_image = None
    container_base_path = '/exp'
