##
## Copyright (c) 2016-2017 Linagora.
##
## This file is part of Zealot
## (see https://ci.linagora.com/tjorquera/zealot).
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.
##
import os, shutil, subprocess
from zealot.env import env

class Env:
    @env.capture
    def __init__(self, out, tmp, data):
        # create out and tmp folders
        # TODO allow to force creation even if folders exist
        os.makedirs(out)
        os.makedirs(tmp)
        # set env variables
        self.env_vars = dict(os.environ)
        self.env_vars['ZEALOT_OUT'] = out
        self.env_vars['ZEALOT_TMP'] = tmp
        self.env_vars['ZEALOT_DATA'] = data

    def run(self, command, args):
        # run the shell command with env variables
        process = subprocess.Popen(
            [os.path.join(os.getcwd(), command)] + args.split(),
            env=self.env_vars,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True)

        for stdout_line in iter(process.stdout.readline, ""):
            print(stdout_line, end='')

        process.stdout.close()

    @env.capture
    def close(self, out, tmp):
        # TODO allow to preserve tmp
        # TODO allow to preserve out
        shutil.rmtree(tmp)
        shutil.rmtree(out)

def setup_env_basic():
    return Env()

