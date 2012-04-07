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
from fabric.api import run, task, sudo
from fabric.utils import puts
from fabric.operations import open_shell
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
def shell():
    """
    Spawns a shell on the remote instance
    
    """
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
def update_system():
    """
    Updates system
    
    """
    sudo('apt-get update && apt-get -y upgrade')
    
@task
@hosts_required
def uptime():
    """
    Shows system uptime
    
    """
    with default_settings():
        run('uptime')