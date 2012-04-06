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
from fabric.api import env
import os
from maestro import config

def get_provider_driver(provider=None):
    """
    Gets the specified libcloud driver
    
    :param provider: Name of the driver
    :rtype: `libcloud.compute.base.NodeDriver`
    
    """
    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver
    return get_driver(Provider.__dict__.get(provider.upper()))
    
def load_env_keys():
    """
    Loads cloud provider keys from environment into maestro config
    
    """
    env.provider_keys = {}
    env.provider_keys['ec2'] = {
        'id': os.environ.get('EC2_ACCESS_ID', ''),
        'key': os.environ.get('EC2_SECRET_KEY', ''),
    }
    # check provider keys
    if not env.provider_keys:
        raise RuntimeError('You must use environment variables to use cloud nodes.  See the documentation for details')
        