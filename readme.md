### maestro
Maestro is a [Fabric](http://fabfile.org) based toolkit for managing systems.

### Usage
To use, simply run `fab -l` to see a list of available commands. 

For example, to run a memory report for a host named `dev.example.com`:

`fab -H dev.example.com mgmt.memory`

```
[dev.example.com] Executing task 'mgmt.memory'
[dev.example.com] out:              total       used       free     shared    buffers     cached
[dev.example.com] out: Mem:          7948       4076       3871          0       1942        295

```

## Nodes
Maestro has the ability to use a cloud provider (currently only EC2) for a node list. 

To run an uptime report for all nodes in EC2 us-east region:

`fab nodes:ec2_us_east mgmt.uptime`

