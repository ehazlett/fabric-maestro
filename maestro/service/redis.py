from .base import BaseService
from fabric.api import run, task, sudo, put
from fabric.context_managers import settings, hide
import time
from maestro.decorators import hosts_required
from maestro.utils import generate_password
import os

class Redis(BaseService):
    def __init__(self, *args, **kwargs):
        super(Redis, self).__init__(*args, **kwargs)
        self._service_name = 'redis'
        self._default_conf = kwargs.get('default_conf', '/etc/redis.conf')
        self._conf = os.path.join(self._conf_dir,
            '{0}.conf'.format(self._service_name))
        self._supervisor_conf = os.path.join(self._supervisor_conf_dir,
            '{0}-{1}.conf'.format(self._name, self._service_name))
        self._data_dir = os.path.join(self._conf_dir, self._service_name)
        self._password = generate_password()

    def _provision(self, *args, **kwargs):
        # generate redis config
        with hide('stdout', 'warnings'):
            password = generate_password()
            sudo('cp -f {0} {1}'.format(self._default_conf, self._conf))
            # edit config
            sudo("sed -i 's/bind.*/bind 0.0.0.0/g' {0}".format(
                self._conf))
            sudo("sed -i 's/port.*/port {0}/g' {1}".format(self._port,
                self._conf))
            sudo("sed -i 's/pidfile.*/pidfile \/var\/run\/redis-{0}/g' {1}".format(
                self._name, self._conf))
            sudo("sed -i 's/dir.*/dir {0}/g' {1}".format(
                self._data_dir.replace('/', '\/'), self._conf))
            sudo("echo \"masterauth {0}\" >> {1}".format(self._password, self._conf))
            sudo("mkdir -p {0}".format(self._data_dir))
            # create supervisor config
            tmpl = """[program:redis-{0}]
command=redis-server {1}
user=root
autostart=true
autorestart=true
redirect_stderr=true
""".format(self._name, self._conf)
            sudo("echo \"{0}\" > {1}".format(tmpl, self._supervisor_conf))
    
    def _post_provision(self):
        time.sleep(3)
        print("Redis service provisioned." \
            "  Password: {0}".format(self._password))

    def _remove(self, *args, **kwargs):
        sudo("rm -rf {0}".format(self._conf))
        sudo("rm -rf {0}".format(self._supervisor_conf))
        sudo("rm -rf {0}".format(self._data_dir))

@task
@hosts_required
def create(name=None, port=None):
    """
    Provisions a new Redis service

    :param name: Name of instance
    :param port: Port for instance

    """
    m = Redis(name=name, port=port)
    m.provision()

@task
@hosts_required
def remove(name=None):
    """
    Removes a Redis service

    :param name: Name of instance

    """
    m = Redis(name=name)
    m.remove()
