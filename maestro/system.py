#!/usr/bin/env python
#    Copyright 2012 Maestro Project
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from fabric.api import run, task, sudo, put
from fabric.utils import puts
from fabric.operations import open_shell
from fabric.context_managers import settings
from maestro.config import default_settings
from maestro.decorators import hosts_required

@task
@hosts_required
def memory():
    """
    Shows system uptime

    """
    with default_settings():
        run('free -m')

@task
@hosts_required
def run_command(command):
    """
    Shows the output from the specified command

    :param command: Command to execute

    """
    with default_settings():
        run(command)

@task
@hosts_required
def upload_file(src, dest, mode=None):
    """
    Uploads a local file

    :param src: Path to the local file
    :param dest: Destination path on the host
    :param mode: Mode to set the remote file
    """
    if mode:
        mode = int(mode)
    with default_settings():
        put(src, dest, use_sudo=True, mode=mode)

@task
@hosts_required
def shell():
    """
    Spawns a shell on the remote instance

    """
    with settings(parallel=False):
        open_shell()

@task
@hosts_required
def update_check():
    """
    Shows update status

    """
    with default_settings():
        run('cat /var/lib/update-notifier/updates-available')

@task
@hosts_required
def update_system(dist_upgrade=False):
    """
    Updates system

    """
    upgrade = "apt-get -y upgrade"
    if dist_upgrade or type(dist_upgrade) == type(str) and dist_upgrade.lower() == 'true':
        upgrade = "apt-get -y dist-upgrade"
    sudo('apt-get update && {0}'.format(upgrade))

@task
@hosts_required
def uptime():
    """
    Shows system uptime

    """
    with default_settings():
        run('uptime')