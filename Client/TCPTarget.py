# -*- coding: utf-8 -*-

# Simple TCP Client

import socket
import time
from Logger import Logger

class TcpTarget():
    '''
    TcpTarget is implementation of a TCP target for the ServerFuzzer
    '''

    def __init__(self, name, host, port, max_retries=10, timeout=None, logger=None):
        '''
        :param name: name of the target
        :param host: host ip (to send data to) currently unused
        :param port: port to send to
        :param timeout: socket timeout (default: None)
        :param logger: logger for the object (default: None)
        '''
        if (host is None) or (port is None):
            raise ValueError('host and port may not be None')

        self.host = host
        self.port = port

        if logger is None:
            confLogg = Logger
            confLogg.add_StreamHandler()
            confLogg.add_FileHandler('TCPClient' + time.strftime("%m/%d/%Y_%H:%M:%S") + '.log')
            self.logger = confLogg.logger
        else:
            self.logger = logger
            
        self.timeout = timeout
        self.socket = None
        self.max_retries = max_retries

    def pre_test(self):
        retry_count = 0
        while self.socket is None and retry_count < self.max_retries:
            sock = self._get_socket()
            if self.timeout is not None:
                sock.settimeout(self.timeout)
            try:
                retry_count += 1
                sock.connect((self.host, self.port))
                self.socket = sock
            except Exception as err:
                sock.close()
                self.logger.error('Error: %s' %err)
                self.logger.error('Failed to connect to target server, retrying...')
                time.sleep(1)
        if self.socket is None:
            raise(socket.error('TCPTarget: (pre_test) cannot connect to server (retries = %d' % retry_count))

    def _get_socket(self):
        '''
        get a socket object
        '''
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def post_test(self):
        '''
        Called after a test is completed, perform cleanup etc.
        '''
        if self.socket is not None:
            self.socket.shutdown()
            self.socket.close()
            self.socket = None

    def _send_to_target(self, data):
        self.socket.send(data)

    def _receive_from_target(self):
        return self.socket.recv(4096)