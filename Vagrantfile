# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.host_name = "maestro.local"
  config.vm.provision :shell, :path => "provision.sh"
  config.vm.network :hostonly, "10.10.10.30"
  config.ssh.forward_agent = true
  config.vm.forward_port 80, 8080 # http
  config.vm.forward_port 10000, 10000 # services
  config.vm.forward_port 10001, 10001 # services
  config.vm.forward_port 10002, 10002 # services
  config.vm.forward_port 10003, 10003 # services
  config.vm.forward_port 10004, 10004 # services
  config.vm.customize ["modifyvm", :id, "--memory", 1024]
end
