#!/usr/bin/env python
# Copyright 2013 Maestro Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
from fabric.api import task, env, open_shell
from libcloud.compute.base import NodeImage, NodeSize
from libcloud.compute.types import NodeState
from maestro.decorators import valid_provider_required, provider_required
from maestro.utils import get_provider_driver, load_env_keys
import config
import logging

log = logging.getLogger(__name__)

def get_key(provider=None, region=None):
    """
    Returns keys for provider

    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region

    """
    load_env_keys()
    # check for ec2 east/west and use ec2 keys
    if provider.find('ec2') > -1:
        pk = env.provider_keys.get('ec2')
    else:
        pk = env.provider_keys[provider]
    return pk

def get_connection(provider=None, region=None):
    """
    Returns a connect to the specified provider

    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region

    """
    drv = get_provider_driver(provider=provider, region=region)
    key = get_key(provider, region)
    conn = drv(key.get('id'), key.get('key'))
    return conn

def get_nodes(provider=None, region=None):
    """
    Returns all nodes in region for provider

    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region

    """
    conn = get_connection(provider, region)
    try:
        log.debug('Getting nodes for {0} in {1}'.format(provider, region))
        nodes = conn.list_nodes()
    except Exception, e:
        log.warn('Unable to connect to {0} for {1}: {2}'.format(region, provider, e))
    return nodes

@valid_provider_required
def load_nodes(providers=None, regions='', filter=None):
    """
    Uses a cloud provider(s) for the node list (i.e. ec2)

    :param providers: List of cloud provider names ; comma separated (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param regions: List of cloud provider regions ; comma separated (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)
        * If `regions` is not defined, all regions are used
    :param filter: Regular expression for filtering nodes

    """
    load_env_keys()
    connections = {}
    env.nodes = []
    env.hosts = []
    filter = filter if filter else '.*'
    regex = re.compile(filter)
    for p in providers.split(','):
        if not regions:
            regions = config.AVAILABLE_CLOUD_REGIONS.get(p)
        else:
            regions = regions.split(',')
        for r in regions:
            nodes = get_nodes(p, r)
            [env.nodes.append(x) for x in nodes if regex.match(x.name)]
            [env.hosts.append(x.public_ips[0]) for x in nodes if x.state == NodeState.RUNNING \
                and regex.match(x.name)]
@task
def list_available_providers():
    """
    Lists available providers and regions

    """
    regions = config.AVAILABLE_CLOUD_REGIONS
    for k,v in regions.iteritems():
        print('{0:12s}: {1}'.format(k, ', '.join(regions[k].keys())))

@task
@valid_provider_required
def nodes(providers=None, regions=None, filter=None):
    """
    Selects all cloud provider(s) nodes for running the task

    :param providers: List of cloud provider names ; comma separated (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param regions: List of cloud provider regions ; comma separated (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)
        * If `regions` is not defined, all regions are used
    :param filter: Regular expression for filtering nodes

    """
    load_nodes(providers=providers, regions=regions, filter=filter)

@task
@valid_provider_required
def list_nodes(providers=None, regions=None, filter=None):
    """
    Shows nodes for specified providers

    :param providers: List of cloud provider names ; comma separated (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param regions: List of cloud provider regions ; comma separated (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)
        * If `regions` is not defined, all regions are used
    :param filter: Regular expression for filtering nodes

    """

    load_nodes(providers=providers, regions=regions, filter=filter)
    for n in env.nodes:
        public_ip = n.public_ips[0] if n.public_ips else ''
        private_ip = n.private_ips[0] if n.private_ips else ''
        status = [k for k,v in NodeState.__dict__.iteritems() if v == n.state][0]
        print('{0:20s} {1:12s} {2:12s} {3:25s} {4:25s} {5:10s}'.format(n.name, n.id, n.extra.get('availability', None), public_ip, private_ip, status))

@task
def launch(name=None, provider=None, region=None, image_id=None, size=None,
    keyname=None):
    """
    Launches a node

    :param name: Name of node
    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)

    """
    conn = get_connection(provider, region)
    if not image_id:
        image_id = raw_input('Please enter an Image ID (i.e. ami-12345): ')
    if not size:
        size = raw_input('Please enter a node size (i.e. t1.micro): ')
    if not keyname:
        keyname = raw_input('Please enter a keyname to use (must exist): ')
    image = NodeImage(id=image_id, name="", driver="")
    size = NodeSize(id=size, name="", ram=None, disk=None, bandwidth=None,
        price=None, driver="")
    n = conn.create_node(name=name, image=image, size=size, ex_keyname=keyname)
    print('Node {0} launched'.format(name))

@task
@provider_required('ec2')
def start(name=None, provider=None, region=None):
    """
    Starts a stopped node

    :param name: Name of node
    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)

    """
    conn = get_connection(provider, region)
    return
    for node in get_nodes(provider, region):
        if node.name == name:
            print('Starting {0} ({1})'.format(node.name, node.id))
            conn.ex_start_node(node)
@task
def stop(name=None, provider=None, region=None):
    """
    Stops a node

    :param name: Name of node
    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)

    """
    conn = get_connection(provider, region)
    for node in get_nodes(provider, region):
        if node.name == name:
            print('Stopping {0} ({1})'.format(node.name, node.id))
            conn.ex_stop_node(node)

@task
def terminate(name=None, provider=None, region=None):
    """
    Terminates a node

    :param name: Name of node
    :param provider: Name of provider (see `maestro.config.AVAILABLE_CLOUD_PROVIDERS`)
    :param region: Name of region (see `maestro.config.AVAILABLE_CLOUD_REGIONS`)

    """
    conn = get_connection(provider, region)
    for node in get_nodes(provider, region):
        if node.name == name:
            print('Terminating {0} ({1})'.format(node.name, node.id))
            conn.destroy_node(node)
