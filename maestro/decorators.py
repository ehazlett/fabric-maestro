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
from functools import wraps
from maestro import config
from fabric.api import env

def valid_provider_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cloud_providers = config.AVAILABLE_CLOUD_PROVIDERS
        if not args and not kwargs or len(args) < 1 and len(kwargs) < 1:
            raise RuntimeError('You must specify a provider')
        if len(args) > 0 and args[0].lower() not in cloud_providers \
            or len(kwargs) > 0 and kwargs['provider'] not in cloud_providers:
            raise ValueError('Invalid provider.  Available: {0}'.format( \
                ','.join(cloud_providers)))
        return f(*args, **kwargs)
    return decorated
    
def hosts_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not env.hosts:
                raise RuntimeError('You must specify a host or hosts')
            return f(*args, **kwargs)
        return decorated