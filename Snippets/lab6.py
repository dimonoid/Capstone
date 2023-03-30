#!/usr/bin/python2.7
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController


class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        # SWITCH
        S1 = Topo.addSwitch(self, 'S1')
        S2 = Topo.addSwitch(self, 'S2')
        S3 = Topo.addSwitch(self, 'S3')
        S4 = Topo.addSwitch(self, 'S4')
        # HOST
        H1 = Topo.addHost(self, 'H1')
        H2 = Topo.addHost(self, 'H2')
        H4 = Topo.addHost(self, 'H4')
        H5 = Topo.addHost(self, 'H5')
        H6 = Topo.addHost(self, 'H6')
        H7 = Topo.addHost(self, 'H7')
        H8 = Topo.addHost(self, 'H8')
        # LINKs
        Topo.addLink(self, H1, S1, port1=None, port2=None, key=None)
        Topo.addLink(self, H2, S1, port1=None, port2=None, key=None)
        Topo.addLink(self, H4, S4, port1=None, port2=None, key=None)
        Topo.addLink(self, H5, S3, port1=None, port2=None, key=None)
        Topo.addLink(self, H6, S3, port1=None, port2=None, key=None)
        Topo.addLink(self, H7, S3, port1=None, port2=None, key=None)
        Topo.addLink(self, H8, S3, port1=None, port2=None, key=None)

        Topo.addLink(self, S1, S2, port1=None, port2=None, key=None)
        Topo.addLink(self, S2, S3, port1=None, port2=None, key=None)
        Topo.addLink(self, S1, S4, port1=None, port2=None, key=None)
        # ..Your code here..


def starter():
    topology = MyTopo()
    net = Mininet(topo=topology, controller=lambda name: RemoteController(name, ip='127.0.0.1'), autoSetMacs=True)
    net.start()
    dumpNodeConnections(net.hosts)
    CLI(net)
    net.stop()


setLogLevel('info')
starter()
