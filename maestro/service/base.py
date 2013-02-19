from hashlib import sha256
from fabric.api import sudo
import os

class BaseService(object):
    def __init__(self, name=None, port=None, username=None,
        password=None, base_conf_dir=None, supervisor_conf_dir=None,
        *args, **kwargs):
        self._name = self._get_instance_name(name)
        self._port = port
        self._username = username
        self._password = password
        self._service_name = 'base'
        if not base_conf_dir:
            base_conf_dir = '/var/tmp'
        self._base_conf_dir = base_conf_dir
        self._conf_dir = os.path.join(self._base_conf_dir, self._name)
        if not supervisor_conf_dir:
            supervisor_conf_dir = '/etc/supervisor/conf.d'
        self._supervisor_conf_dir = supervisor_conf_dir

    def _get_instance_name(self, name):
        s = sha256()
        s.update(name)
        return s.hexdigest()[:12]

    def _setup(self):
        sudo('mkdir -p {0}'.format(self._conf_dir))

    def _pre_provision(self):
        pass

    def _post_provision(self):
        pass

    def _provision(self, *args, **kwargs):
        raise NotImplemented

    def provision(self):
        self._setup()
        self._pre_provision()
        self._provision()
        self._post_provision()
