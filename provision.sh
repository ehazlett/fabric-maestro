#!/bin/sh

# common config

if [ -e "/etc/.configured" ] ; then
    echo "VM appears configured ; not provisioning"
    exit 0
fi

# puppetlabs repo
if [ ! -e "/etc/apt/sources.list.d/puppetlabs.list" ] ; then
    wget -q "http://apt.puppetlabs.com/puppetlabs-release-precise.deb" -O /tmp/puppetlabs.deb
    dpkg -i /tmp/puppetlabs.deb
fi

# update apt
apt-get -y update 2>&1 > /dev/null
apt-get -y install vim screen python-setuptools python-dev
easy_install pip > /dev/null 2>&1

# install puppet
apt-get install -y puppet-common

# mark instance as configured
touch /etc/.configured
echo "Configuration complete."

exit 0
