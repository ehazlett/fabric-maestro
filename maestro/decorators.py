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
from fabric.api import env
from maestro import config
from maestro.utils import load_maestro_rc

def hosts_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):
       if not env.hosts:
           raise RuntimeError('You must specify a host or hosts')
       return f(*args, **kwargs)
   return decorated
        
def load_maestro_resource(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        load_maestro_rc()
        return f(*args, **kwargs)
    return decorated
    
def valid_provider_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # cleanup this function?
        cloud_providers = config.AVAILABLE_CLOUD_PROVIDERS
        invalid_provider = False
        if not args and not kwargs:
            raise RuntimeError('You must specify a provider')
        if len(args) > 0 and args[0].lower() not in cloud_providers:
            invalid_provider = True
        if len(kwargs) > 0:
            if 'providers' in kwargs:
                for p in kwargs['providers'].split(','):
                    if p not in cloud_providers:
                        invalid_provider = p
        if invalid_provider:
            raise ValueError('Invalid provider {0}.  Available: {1}'.format( \
                invalid_provider, ','.join(cloud_providers)))
        return f(*args, **kwargs)
    return decorated