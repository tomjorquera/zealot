import os, shutil, docker
from zealot.env import env

class DockerEnv:
    ## create docker container
    ## - with mounted experiment folder
    ## - with mounted tmp folder
    ## - with mounted out folder
    ##
    # return an env object that allow to run commands
    @env.capture
    def __init__(self,
                 docker_image,
                 out,
                 tmp,
                 data,
                 container_base_path):
        # create out and tmp folders
        # TODO deduplicate code with env_base
        os.makedirs(out)
        os.makedirs(tmp)

        self.client = docker.from_env()

        volumes = {
            os.path.abspath(os.getcwd()): {
                'bind': container_base_path,
                'mode': 'ro'
            },
            os.path.abspath(tmp): {
                'bind': os.path.join(container_base_path, tmp),
                'mode': 'rw'
            },
            os.path.abspath(out): {
                'bind': os.path.join(container_base_path, out),
                'mode': 'rw'
            },
            os.path.abspath(data): {
                'bind': os.path.join(container_base_path, data),
                'mode': 'ro'
            }
        }
        env = {
            'PWD': container_base_path,
            'ZEALOT_OUT': os.path.join(container_base_path, out),
            'ZEALOT_TMP': os.path.join(container_base_path, tmp),
            'ZEALOT_DATA': os.path.join(container_base_path, data)
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
            os.path.join(container_base_path, command), user=str(os.getuid())))

    @env.capture
    def close(self, out, tmp):
        self.container.stop()
        # TODO allow option to not remove container
        self.container.remove()
        # TODO deduplicate code with env_base
        shutil.rmtree(os.path.join(os.getcwd(), tmp))
        shutil.rmtree(os.path.join(os.getcwd(), out))

def setup_env_docker():
    return DockerEnv()
