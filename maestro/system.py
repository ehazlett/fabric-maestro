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
from fabric.api import run, task
from maestro.config import default_settings
from maestro.decorators import hosts_required

@task
@hosts_required
def memory():
    """
    Returns system uptime
    
    :rtype: string
    
    """
    with default_settings():
        return run('free -m | head -2')

@task
@hosts_required
def uptime():
    """
    Returns system uptime
    
    :rtype: string
    
    """
    with default_settings():
        return run('uptime')