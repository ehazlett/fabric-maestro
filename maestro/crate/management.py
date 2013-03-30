from fabric.api import run, sudo, task, get, put, open_shell
from fabric.context_managers import cd, hide
from datetime import date
import os
import tempfile
import random

# TODO: parse lxc config to get path
LXC_PATH = '/var/lib/lxc'
LXC_IP_LINK = 'https://gist.github.com/ehazlett/5274446/raw/070f8a77f7f5738ee2d855a1b94e2e9a23d770c6/gistfile1.txt'

def get_lxc_ip(name=None):
    # get lxc-ip script if doesn't exist
    out = run('test -e /usr/local/bin/lxc-ip', quiet=True,
        warn_only=True)
    if out.return_code != 0:
        with hide('stdout'):
            sudo('wget {0} -O /usr/local/bin/lxc-ip ; chmod +x /usr/local/bin/lxc-ip'.format(
                LXC_IP_LINK))
    with hide('stdout'):
        out = sudo('/usr/local/bin/lxc-ip -n {0}'.format(name))
    return out

@task
def create(name=None, distro='ubuntu', release='precise', arch='amd64'):
    """
    Creates a new Container

    :param name: Name of container
    :param distro: Name of base distro
    :param release: Name of base distro release
    :param arch: Architecture of container

    """
    if not name:
        raise StandardError('You must specify a name')
    sudo('lxc-create -n {0} -t {1} -- -r {2} -a {3}'.format(
        name, distro, release, arch))

@task
def clone(source=None, dest=None, size=2):
    """
    Creates a new Container

    :param source: Name of source container
    :param dest: Name of new container
    :param size: Size of new container (in GB, default: 2)

    """
    if not source or not dest:
        raise StandardError('You must specify a source and dest')
    sudo('lxc-clone -o {0} -n {1} -s {2}G'.format(source, dest, size))

@task
def export_container(name=None):
    """
    Exports (tarball) specified container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    # TODO: parse config to get path
    export_name = '{0}-{1}.tar.gz'.format(name, date.today().isoformat())
    tmp_file = os.path.join('/tmp', export_name)
    print('Creating archive...')
    with cd(os.path.join(LXC_PATH, name)), hide('stdout'):
        sudo('tar czf {0} .'.format(tmp_file))
    print('Downloading {0} ...'.format(export_name))
    get(tmp_file, export_name)
    sudo('rm -f {0}'.format(tmp_file))

@task
def import_container(name=None, local_path=None):
    """
    Imports a container from an export

    :param name: Name of container
    :param local_path: Path to exported container (tarball)

    """
    if not name or not os.path.exists(local_path):
        raise StandardError('You must specify a name and file must exist')
    tmp_file = '/tmp/name.tar.gz'
    print('Uploading archive...')
    put(local_path, tmp_file)
    dest_path = os.path.join(LXC_PATH, name)
    sudo('mkdir -p {0}'.format(dest_path))
    print('Extracting...')
    with cd(dest_path), hide('stdout'):
        sudo('tar xzf {0} .'.format(tmp_file))
    print('Imported {0} successfully...'.format(name))

@task
def list():
    """
    List all Containers

    """
    sudo('lxc-list')

@task
def start(name=None, ephemeral=False):
    """
    Starts a Container

    :param name: Name of container
    :param ephemeral: Disregard changes after stop (default: False)

    """
    if not name:
        raise StandardError('You must specify a name')
    cmd = 'lxc-start -n {0}'.format(name)
    if ephemeral:
        cmd = 'lxc-start-ephemeral -o {0}'.format(name)
    sudo('nohup {0} -d > /dev/null 2>&1'.format(cmd))

@task
def console(name=None):
    """
    Connects to Container console

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    open_shell('sudo lxc-console -e b -n {0} ; exit'.format(name))

@task
def stop(name=None):
    """
    Stops a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    sudo('lxc-stop -n {0}'.format(name))

@task
def destroy(name=None):
    """
    Destroys a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    sudo('lxc-destroy -n {0} -f'.format(name))

@task
def forward(name=None, container_port=None):
    """
    Forwards a host port to a container port

    :param name: Name of container
    :param container_port: Port on container

    """
    # find open port on host
    while True:
        port = random.randint(10000, 50000)
        out = sudo('netstat -lnt | awk \'$6 == "LISTEN" && $4 ~ ".{0}"\''.format(
            port))
        if out == '':
            break
    # get ip of container
    container_ip = get_lxc_ip(name)
    with hide('stdout'):
        sudo('iptables -t nat -A PREROUTING -p tcp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(port, container_ip,
            container_port))
    print('Service available on host port {0}'.format(port))

@task
def list_ports(name=None):
    """
    Removes a container port forward

    :param name: Name of container

    """
    # get ip of container
    container_ip = get_lxc_ip(name)
    cur = sudo('iptables -L -t nat | grep {0}'.format(container_ip),
        warn_only=True, quiet=True)
    if cur:
        for l in cur.splitlines():
            if l:
                dport = cur.split()[-2].split(':')[1]
                target = cur.split()[-1].split(':')[-1]
                print('Port: {0} Target: {1}'.format(dport, target))
    else:
        print('No port forwards for {0}'.format(name))

@task
def remove(name=None, container_port=None):
    """
    Removes a container port forward

    :param name: Name of container
    :param container_port: Port on container

    """
    # get ip of container
    container_ip = get_lxc_ip(name)
    cur = sudo('iptables -L -t nat | grep {0}'.format(container_ip),
        warn_only=True, quiet=True)
    if cur:
        dport = cur.split()[-2].split(':')[1]
        sudo('iptables -t nat -D PREROUTING -p tcp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            container_port), warn_only=True, quiet=True)
        print('Port forward for {0} removed'.format(container_port))

