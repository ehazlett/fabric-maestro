from .base import BaseService
from fabric.api import run, task, sudo, put
from fabric.context_managers import settings, hide
from maestro.decorators import hosts_required
import os

class MySQL(BaseService):
    def __init__(self, *args, **kwargs):
        super(MySQL, self).__init__(*args, **kwargs)
        self._service_name = 'mysql'
        self._default_conf = '/etc/mysql/my.cnf'
        self._conf = os.path.join(self._conf_dir,
            '{0}.cnf'.format(self._service_name))
        self._supervisor_conf = os.path.join(self._supervisor_conf_dir,
            '{0}-{1}.conf'.format(self._name, self._service_name))
        self._data_dir = os.path.join(self._conf_dir, self._service_name)
        self._mysql_user = 'mysql'

    def _provision(self):
        # copy mysql config
        with hide('stdout', 'warnings'):
            sudo('cp -f {0} {1}'.format(self._default_conf, self._conf))
            # edit config
            sudo("sed -i 's/port.*/port = {0}/g' {1}".format(self._port,
                self._conf))
            sudo("sed -i 's/datadir.*/datadir = {0}/g' {1}".format(
                self._data_dir.replace('/', '\/'), self._conf))
            sudo("mkdir -p {0}".format(self._data_dir))
            sudo("chown -R {0} {1}".format(self._mysql_user, self._data_dir))
            sudo("mysql_install_db --defaults-extra-file={0}".format(
                self._conf))
            # TODO: create admin user
            # create supervisor config
            tmpl = """[program:mysql-{0}]
command=mysqld --defaults-extra-file={1}
user=root
autostart=true
autorestart=true
redirect_stderr=true
""".format(self._name, self._conf)
            sudo("echo \"{0}\" > {1}".format(tmpl, self._supervisor_conf))
            # refresh supervisor
            sudo("supervisorctl update")

@task
@hosts_required
def create(name=None, port=None):
    """
    Provisions a new MySQL service

    :param name: Name of instance
    :param port: Port for instance

    """
    m = MySQL(name=name, port=port)
    m.provision()
