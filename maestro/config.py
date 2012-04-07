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
from fabric.context_managers import settings, hide
import fabric.state
import libcloud.security
import platform

# don't verify ssl certs (doesn't work on os x)
if platform.mac_ver():
    libcloud.security.VERIFY_SSL_CERT = False

# to hide 'running', this must be at the global level 
#   https://github.com/fabric/fabric/issues/424
fabric.state.output['running'] = False
fabric.state.output['status'] = False

AVAILABLE_CLOUD_PROVIDERS = (
    'ec2',
    'ec2_us_east',
    'ec2_us_west',
    'rackspace',
)
def default_settings():
    """
    Returns a default settings object for tasks
    
    :rtype: `fabric.context_managers.settings`
    
    """
    defaults = settings(
        hide('running', 'stdout', 'stderr'),
    )
    return defaults