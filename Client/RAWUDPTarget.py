# -*- coding: utf-8 -*-
# UDP Client in raw mode

import socket
import time
from scapy.all import Ether, IP, UDP, Raw
from udp import UdpTarget
from Logger import Logger


class RawUdpTarget(UdpTarget):
    '''
    RawUdpTarget is implementation of a UDP target using a raw socket
    '''

    def __init__(self, name, interface, host, port, timeout=None, logger=None):
        '''
        :param name: name of the target
        :param interface: interface name
        :param host: host ip (to send data to) currently unused
        :param port: port to send to
        :param timeout: socket timeout (default: None)
        :param logger: logger for the object (default: None)
        '''
        if logger is None:
            confLogg = Logger
            confLogg.add_StreamHandler()
            confLogg.add_FileHandler('RAWUDPClient' + time.strftime("%m/%d/%Y_%H:%M:%S") + '.log')
            self.logger = confLogg.logger
        else:
            self.logger = logger
        
        self._interface = interface

    def _prepare_socket(self):
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_IP)
        self.socket.bind((self._interface, 0))

    def _send_to_target(self, data):
        ether = Ether(dst='ff:ff:ff:ff:ff:ff')
        ip = IP(src=self.host, dst='255.255.255.255')
        udp = UDP(sport=68, dport=self.port)
        payload = Raw(load=data)
        packet = str(ether / ip / udp / payload)
        self.logger.debug('Sending header+data to host: %s:%d' % (self.host, self.port))
        self.socket.send(packet)
        self.logger.debug('Header+data sent to host')

    def _receive_from_target(self):
        return self.socket.recvfrom(4096)