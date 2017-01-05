import os, re, sys
from sacred import dependencies, arg_parser
from sacred.config.config_scope import ConfigScope

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

def generate_config(zealot):
    # check for user-scope config file
    user_config_path = os.path.join(os.path.expanduser('~'), '.zealot.yaml')
    if (os.path.exists(user_config_path)):
        zealot.add_config(user_config_path)

    # check for command-line config
    args = arg_parser.parse_args(sys.argv)
    conf_updates = arg_parser.get_config_updates(args['UPDATE'])

    # create dict
    config = {}
    for c in zealot.configurations:
        if isinstance(c, ConfigScope):
            config.update(c.__call__())
        else:
            config.update(c._conf)

    config.update(conf_updates[0])

    return config

def save_artifacts(zealot, base_path):
    for artifact in os.listdir(base_path):
        path = os.path.join(base_path, artifact)
        if os.path.isfile(path):
            zealot.add_artifact(path)
        else:
            save_artifacts(zealot, path)

def store_raw_source(zealot, filename):
    zealot.sources.add(dependencies.Source(filename,
                                           dependencies.get_digest(filename)))
