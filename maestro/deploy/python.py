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
from fabric.context_managers import settings, cd, hide
from fabric.contrib.project import rsync_project
from maestro.config import default_settings
from maestro.decorators import hosts_required
import os
import tempfile
import string
from random import Random

def generate_uwsgi_config(app_name=None, app_dir=None, ve_dir=None, state_dir='/var/tmp', **kwargs):
    """
    Generates a uWSGI supervisor config

    :param app_name: Name of application
    :param app_dir: Directory for app
    :param ve_dir: Virtualenv directory
    :param state_dir: Application state dir (default: /var/tmp)

    """
    uwsgi_config = '[program:uwsgi-{0}]\n'.format(app_name)
    uwsgi_config += 'command=uwsgi\n'
    # defaults
    if 'user' in kwargs:
        uwsgi_config += '  --uid {0}\n'.format(kwargs.get('user'))
        uwsgi_config += '  --chown-socket {0}\n'.format(kwargs.get('user'))
    if 'group' in kwargs:
        uwsgi_config += '  --gid {0}\n'.format(kwargs.get('group'))
    uwsgi_config += '  -s {0}\n'.format(os.path.join(state_dir, '{0}.sock'.format(app_name)))
    uwsgi_config += '  -H {0}\n'.format(os.path.join(ve_dir, app_name))
    uwsgi_config += '  -M\n'
    uwsgi_config += '  -p 2\n'
    uwsgi_config += '  --no-orphans\n'
    uwsgi_config += '  --vacuum\n'
    uwsgi_config += '  --post-buffering\n'
    uwsgi_config += '  --harakiri 300\n'
    uwsgi_config += '  --max-requests 5000\n'
    uwsgi_config += '  --python-path {0}\n'.format(app_dir)
    uwsgi_config += '  --module wsgi:application\n'
    # uwsgi args
    if kwargs.has_key('uwsgi_args'):
        for k,v in kwargs.get('uwsgi_args', {}).iteritems():
            uwsgi_config += '  --{0} {1}\n'.format(k, v)
    uwsgi_config += 'directory={0}\n'.format(os.path.join(app_dir, app_name))
    if kwargs.has_key('user'):
        uwsgi_config += 'user={0}\n'.format(kwargs.get('user'))
    uwsgi_config += 'stopsignal=QUIT\n'
    return uwsgi_config

def generate_nginx_config(app_name=None, urls=None, state_dir='/var/tmp', **kwargs):
    """
    Generates an nginx config

    :param app_name: Name of application
    :param urls: List of public urls as strings
    :param state_dir: Application state dir (default: /var/tmp)

    """
    if not app_name or not urls:
        raise RuntimeError('You must specify an app_name and urls')
    cfg = 'server {\n'
    cfg += '    listen 80;\n'
    cfg += '    server_name {0};\n'.format(' '.join(urls))
    cfg += '    server_name_in_redirect off;\n'
    cfg += '    location / {\n'
    cfg += '        include uwsgi_params;\n'
    cfg += '        uwsgi_pass unix://{0}/{1}.sock;\n'.format(state_dir, app_name)
    cfg += '    }\n'
    cfg += '}\n'
    return cfg


@task
@hosts_required
def create_app(name=None, urls=None, py_version='26', app_dir='/opt/apps', ve_dir='/opt/ve'):
    """
    Creates a new application container

    :param name: Name of application
    :param urls: Application public URLs (semi-colon separated - i.e. "example.com;anotherexample.com")
    :param py_version: Version of Python to use (default: 26)
    :param app_dir: Root directory for applications (default: /opt/apps)
    :param ve_dir: Root directory for virtualenvs (default: /opt/ve)

    """
    if not name or not urls:
        raise RuntimeError('You must specify an name and urls')
    with default_settings():
        # create app directory
        sudo('mkdir -p {0}'.format(os.path.join(app_dir, name)))
        # create supervisor config
        uwsgi_tmp_conf = tempfile.mktemp()
        with open(uwsgi_tmp_conf, 'w') as f:
            f.write(generate_uwsgi_config(app_name=name, app_dir=app_dir, ve_dir=ve_dir, user='www-data', group='www-data'))
        nginx_tmp_conf = tempfile.mktemp()
        # create nginx config
        with open(nginx_tmp_conf, 'w') as f:
            f.write(generate_nginx_config(app_name=name, urls=urls.split(';')))
        put(uwsgi_tmp_conf, '/etc/supervisor/conf.d/uwsgi-{0}.conf'.format(name), mode=0755, use_sudo=True)
        put(nginx_tmp_conf, '/etc/nginx/conf.d/{0}.conf'.format(name), mode=0755, use_sudo=True)
        # update supervisor
        sudo('supervisorctl update')
        # cleanup
        os.remove(uwsgi_tmp_conf)
        os.remove(nginx_tmp_conf)

@task
@hosts_required
def deploy(name=None, source=None, app_dir='/opt/apps', ve_dir='/opt/ve'):
    """
    Deploys an application

    :param name: Name of application
    :param source: Application source (can be git repo: i.e. https://github.com/ehazlett/myapp or directory)
    :param app_dir: Root directory for applications (default: /opt/apps)
    :param ve_dir: Root directory for virtualenvs (default: /opt/ve)

    """
    if not name or not source:
        raise RuntimeError('You must specify a name and source')
    sudo('mkdir -p {0}'.format(ve_dir))
    # build ve
    with cd(ve_dir):
        sudo('virtualenv --no-site-packages {0}'.format(name))
    # look for git repo
    tmp_deploy_dir = os.path.join('/tmp', ''.join(Random().sample(string.letters+string.digits, 8)))
    sudo('mkdir -p {0} ; chmod -R o+rw {0}'.format(tmp_deploy_dir))
    with cd(tmp_deploy_dir):
        if source.startswith('http') or source.startswith('git'):
            sudo('git clone {0} {1}'.format(source, name))
        else:
            # upload
            if not os.path.exists(source):
                raise RuntimeError('Source directory does not exist')
            # check for trailing slash
            if not source.endswith('/'):
                source = '{0}/'.format(source)
            with hide('stdout'):
                rsync_project('{0}/{1}'.format(tmp_deploy_dir, name), source, exclude=['*.git', '*.swp'])
        # build env
        sudo('{0}/bin/pip install --use-mirrors -r {1}/requirements.txt'.format(os.path.join(ve_dir, name), name))
    with cd('{0}'.format(app_dir)):
        # replace existing app
        sudo('cp -rf {0}/* ./{1}/'.format(os.path.join(tmp_deploy_dir, name), name))
    # reload supervisor
    sudo('supervisorctl restart uwsgi-{0}'.format(name))
    sudo('service nginx reload')
    # cleanup
    sudo('rm -rf {0}'.format(tmp_deploy_dir))

@task
@hosts_required
def restart(name=None):
    """
    Restarts specified application

    :param name: Applicaiton name

    """
    sudo('supervisorctl restart uwsgi-{0}'.format(name))
    sudo('service nginx reload')

@task
@hosts_required
def stop(name=None):
    """
    Stops specified application

    :param name: Applicaiton name

    """
    sudo('supervisorctl stop uwsgi-{0}'.format(name))

@task
@hosts_required
def get_logs(name=None, num_of_lines=25):
    """
    Gets application logs

    :param name: Name of application
    :param num_of_lines: Number of log lines to get

    """
    if not name:
        raise RuntimeError('You must specify a name')
    sudo('tail -n {0} /var/log/supervisor/uwsgi-{1}*'.format(num_of_lines, name))

@task
@hosts_required
def delete_app(name=None, app_dir='/opt/apps', ve_dir='/opt/ve'):
    """
    Deletes an application

    :param name: Name of application
    :param app_dir: Root directory for applications (default: /opt/apps)
    :param ve_dir: Root directory for virtualenvs (default: /opt/ve)

    """
    if not name:
        raise RuntimeError('You must specify a name')
    with default_settings():
        # remove configs
        sudo('rm /etc/nginx/conf.d/{0}.conf'.format(name))
        sudo('rm /etc/supervisor/conf.d/uwsgi-{0}.conf'.format(name))
        # remove app
        sudo('rm -rf {0}'.format(os.path.join(app_dir, name)))
        sudo('rm -rf {0}'.format(os.path.join(ve_dir, name)))
        # bounce nginx and supervisor
        sudo('service nginx reload')
        sudo('supervisorctl reload')
