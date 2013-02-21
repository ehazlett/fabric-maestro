from .base import BaseService
from fabric.api import run, task, sudo, put
from fabric.context_managers import settings, hide
import time
from maestro.decorators import hosts_required
from maestro.utils import generate_password
import os

class MySQL(BaseService):
    def __init__(self, *args, **kwargs):
        super(MySQL, self).__init__(*args, **kwargs)
        self._service_name = 'mysql'
        self._default_conf = '/etc/mysql/my.cnf'
        self._default_user = 'root'
        self._default_password = kwargs.get('default_password', None)
        self._conf = os.path.join(self._conf_dir,
            '{0}.cnf'.format(self._service_name))
        self._supervisor_conf = os.path.join(self._supervisor_conf_dir,
            '{0}-{1}.conf'.format(self._name, self._service_name))
        self._data_dir = os.path.join(self._conf_dir, self._service_name)
        self._mysql_user = 'mysql'

    def _provision(self, *args, **kwargs):
        # copy mysql config
        with hide('stdout', 'warnings'):
            sudo('cp -f {0} {1}'.format(self._default_conf, self._conf))
            # edit config
            sudo("sed -i 's/port.*/port = {0}/g' {1}".format(self._port,
                self._conf))
            sudo("sed -i 's/datadir.*/datadir = {0}/g' {1}".format(
                self._data_dir.replace('/', '\/'), self._conf))
            sudo("sed -i 's/bind-address.*/bind-address = 0.0.0.0/g' {0}".format(
                self._conf))
            sudo("mkdir -p {0}".format(self._data_dir))
            sudo("chown -R {0} {1}".format(self._mysql_user, self._data_dir))
            sudo("mysql_install_db --defaults-extra-file={0}".format(
                self._conf))
            # create supervisor config
            tmpl = """[program:mysql-{0}]
command=mysqld --defaults-extra-file={1}
user=root
autostart=true
autorestart=true
redirect_stderr=true
""".format(self._name, self._conf)
            sudo("echo \"{0}\" > {1}".format(tmpl, self._supervisor_conf))

    def _post_provision(self):
        # wait for mysql to start
        time.sleep(3)
        # create admin user
        mysql_cmd = "mysql -u {0} --port {1} -h localhost".format(
            self._default_user, self._port)
        if self._default_password:
            mysql_cmd += " -p{0}".format(self._default_password)
        password = generate_password()
        sudo("echo \"create user 'root'@'%' identified by '{0}';\" | {1}".format(
            password, mysql_cmd))
        sudo("echo \"grant all privileges on *.* to 'root'@'%' with grant option\" | {0}".format(
            mysql_cmd))
        print("MySQL service provisioned." \
            "  Username: root" \
            "  Password: {0}".format(password))

    def _remove(self, *args, **kwargs):
        sudo("rm -rf {0}".format(self._conf))
        sudo("rm -rf {0}".format(self._supervisor_conf))
        sudo("rm -rf {0}".format(self._data_dir))

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

@task
@hosts_required
def remove(name=None):
    """
    Provisions a new MySQL service

    :param name: Name of instance

    """
    m = MySQL(name=name)
    m.remove()
