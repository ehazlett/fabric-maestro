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
from fabric.api import task, env
from libcloud.compute.types import NodeState
from maestro.decorators import valid_provider_required
from maestro.utils import get_provider_driver, load_env_keys

@task
@valid_provider_required
def load_nodes(providers=None):
    """
    Uses a cloud provider(s) for the node list (i.e. ec2)
    
    :param providers: List of cloud provider names ; comma separated (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    
    """
    load_env_keys()
    connections = {}
    env.nodes = []
    env.hosts = []
    for p in providers.split(','):
        Driver = get_provider_driver(p)
        # check for ec2 east/west and use ec2 keys
        if p.find('ec2') > -1:
            pk = env.provider_keys.get('ec2')
        else:
            pk = env.provider_keys[p]
        conn = Driver(pk.get('id'), pk.get('key'))
        connections[p] = conn
    for k,conn in connections.iteritems():
        nodes = conn.list_nodes()
        [env.nodes.append(x) for x in nodes]
        [env.hosts.append(x.public_ips[0]) for x in nodes if x.state == NodeState.RUNNING]
        
@task
@valid_provider_required
def list_nodes(providers=None):
    """
    Gets all nodes for specified providers
    
    :param providers: List of cloud provider names ; comma separated (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :rtype: List of nodes
    
    """
    load_nodes(providers)
    for n in env.nodes:
        public_ip = n.public_ips[0] if n.public_ips else ''
        private_ip = n.private_ips[0] if n.private_ips else ''
        status = [k for k,v in NodeState.__dict__.iteritems() if v == n.state][0]
        print('{0:20s} {1:12s} {2:25s} {3:25s} {4:10s}'.format(n.name, n.id, public_ip, private_ip, status))
