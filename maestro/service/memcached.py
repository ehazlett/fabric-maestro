from .base import BaseService
from fabric.api import run, task, sudo, put
from fabric.context_managers import settings, hide
import time
from maestro.decorators import hosts_required
from maestro.utils import generate_password
import os

class Memcached(BaseService):
    def __init__(self, *args, **kwargs):
        super(Memcached, self).__init__(*args, **kwargs)
        self._service_name = 'memcached'
        self._default_user = kwargs.get('user', 'memcache')
        self._default_conf = kwargs.get('default_conf', '/etc/memcached.conf')
        self._default_mem = kwargs.get('memory', 64)
        self._conf = os.path.join(self._conf_dir,
            '{0}.conf'.format(self._service_name))
        self._supervisor_conf = os.path.join(self._supervisor_conf_dir,
            '{0}-{1}.conf'.format(self._name, self._service_name))
        self._data_dir = os.path.join(self._conf_dir, self._service_name)

    def _provision(self, *args, **kwargs):
        # generate memcached config
        with hide('stdout', 'warnings'):
            sudo('cp -f {0} {1}'.format(self._default_conf, self._conf))
            args = "-l 0.0.0.0 "
            args += "-p {0} ".format(self._port)
            # create supervisor config
            tmpl = """[program:memcached-{0}]
command=memcached -u {1} {2}
user=root
autostart=true
autorestart=true
redirect_stderr=true
""".format(self._name, self._default_user, args)
            sudo("echo \"{0}\" > {1}".format(tmpl, self._supervisor_conf))

    def _post_provision(self):
        time.sleep(3)
        print("Memcached service provisioned.")

    def _remove(self, *args, **kwargs):
        sudo("rm -rf {0}".format(self._conf))
        sudo("rm -rf {0}".format(self._supervisor_conf))
        sudo("rm -rf {0}".format(self._data_dir))

@task
@hosts_required
def create(name=None, port=None):
    """
    Provisions a new Memcached service

    :param name: Name of instance
    :param port: Port for instance

    """
    m = Memcached(name=name, port=port)
    m.provision()

@task
@hosts_required
def remove(name=None):
    """
    Removes a Memcached service

    :param name: Name of instance

    """
    m = Memcached(name=name)
    m.remove()
