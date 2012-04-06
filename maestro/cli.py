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
import sys
import inspect
from argparse import ArgumentParser
from fabric.api import env
from fabric.tasks import execute, WrappedCallableTask
from fabric.network import disconnect_all
from maestro import config
from maestro.utils import load_maestro_rc
from maestro.core import load_nodes, list_nodes
import maestro.system

def show_tasks():
    """
    Gets list of Maestro tasks
    
    :rtype: List of task names
    
    """
    task_list = []
    [task_list.append(x[0]) for x in inspect.getmembers(maestro.system) if isinstance(x[1], WrappedCallableTask)]
    return task_list

def parse_tasks(args):
    """
    Parses arguments from CLI for tasks
    
    """
    if args.tasks_list:
        print('Available Tasks:')
        print(', '.join(show_tasks()))
        
def parse_nodes(args):
    """
    Parses arguments from CLI for nodes
    """
    if args.user:
        env.user = args.user
    env.parallel = args.parallel
    if args.list:
        list_nodes(args.cloud_provider)
    if args.task:
        load_nodes(args.cloud_provider)
        execute(getattr(maestro.system, args.task))

def main():
    """
    Main entry point for CLI
    
    """
    load_maestro_rc()
    parser = ArgumentParser(prog='maestro', description='DevOps management')
    sub = parser.add_subparsers()
    sub_tasks = sub.add_parser('tasks', help='Tasks')
    sub_tasks.add_argument('-l', '--list', action='store_true', dest='tasks_list', default=False, \
        help='Show available tasks')
    sub_tasks.add_argument('-r', '--run', action='store', dest='tasks_task', \
        help='Task to run')
    sub_tasks.set_defaults(func=parse_tasks)
    
    sub_nodes = sub.add_parser('nodes', help='Nodes')
    sub_nodes.add_argument('-c', '--cloud-provider', action='store', dest='cloud_provider', \
        choices=config.AVAILABLE_CLOUD_PROVIDERS, default=None, required=True, \
        help='Name of cloud provider to use')
    sub_nodes.add_argument('-l', '--list', action='store_true', dest='list', default=False, \
        help='List all nodes')
    sub_nodes.add_argument('-t', '--task', action='store', dest='task', \
        help='Task to run on nodes')
    sub_nodes.add_argument('-u', '--user', action='store', dest='user', \
        help='Username to use when running task')
    sub_nodes.add_argument('-p', '--parallel', action='store_true', default=False, \
        help='Run task in parallel among nodes')
    sub_nodes.set_defaults(func=parse_nodes)
        
    args = parser.parse_args()
    args.func(args)
    # disconnect
    disconnect_all()
    sys.exit(0)

if __name__=='__main__':
    main()