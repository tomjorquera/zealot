import os, shutil, docker
from zealot_ingredient_env import env

class DockerEnv:
    ## create docker container
    ## - with mounted experiment folder
    ## - with mounted tmp folder
    ## - with mounted out folder
    ##
    # return an env object that allow to run commands
    @env.capture
    def __init__(self,
                 exp_folder,
                 docker_image,
                 out,
                 tmp,
                 container_base_path):
        # create out and tmp folders
        # TODO deduplicate code with env_base
        os.makedirs(out)
        os.makedirs(tmp)

        self.client = docker.from_env()
        self.exp_path = os.path.join(container_base_path, exp_folder)

        volumes = {
            os.path.abspath(os.getcwd()): {
                'bind': self.exp_path,
                'mode': 'ro'
            },
            os.path.abspath(tmp): {
                'bind': os.path.join(self.exp_path, tmp),
                'mode': 'rw'
            },
            os.path.abspath(out): {
                'bind': os.path.join(self.exp_path, out),
                'mode': 'rw'
            }
        }
        env = {
            'PWD': self.exp_path,
            'ZEALOT_OUT': os.path.join(self.exp_path, out),
            'ZEALOT_TMP': os.path.join(self.exp_path, tmp)
        }
        self.container = self.client.containers.run(
            docker_image,
            detach=True,
            tty=True,
            volumes=volumes,
            environment=env,
            user=os.getuid())

    @env.capture
    def run(self, command, _log, container_base_path):
        _log.info(self.container.exec_run(
            os.path.join(self.exp_path, command), user=str(os.getuid())))

    @env.capture
    def close(self, tmp):
        self.container.stop()
        # TODO allow option to not remove container
        self.container.remove()
        # TODO deduplicate code with env_base
        shutil.rmtree(os.path.join(os.getcwd(), tmp))

def setup_env_docker(exp_folder):
    return DockerEnv(exp_folder)
