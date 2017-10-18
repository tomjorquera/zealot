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

import subprocess

# TODO allow support of JupyterHub

def jupyter_run():
    process = subprocess.Popen(['jupyter', 'notebook'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True)

    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end='')

    process.stdout.close()
