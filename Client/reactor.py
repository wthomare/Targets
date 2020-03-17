# -*- coding: utf-8 -*-
"""
@author: wilfried.thomare
"""
from twisted.internet import reactor, protocol, defer
from twisted.internet.task import Clock
from YourProject import Handler

import queue

class Client_protocol(protocol.Protocol):
    
    def connectionMade(self):
        """
        Call when the connection is made
        """
        # self.factory was set by the factory's default buildProtocol
        self.params = self.factory.params
        self.queue = self.factory.queue # hypothetic queue/dict of event to play
        self.logger = self.factory.logger
        self.Handler = Handler(self.logger, self.params) # The object which encode/decode/create the data exchange
        
        deferred_list = []
        data_list, self.q, self.def_until_ack = queue.Queue(), queue.Queue(), queue.Queue()
        
        if self.queue:
            for key, value in self.queue:
                data_to_send = self.Handler(value)
                deferred_list.append(defer.Deferred())
                data_list.put_nowait(data_to_send)
        
        self.dl_prim = defer.DeferredList(deferred_list, consummeError=True)
        self.dl_prim.addCallback(self.send_if_ack)
        
        for i, defer_val in enumerate(deferred_list):
            try:
                defer_val.callback(data_list.get())
                defer_val.addTimeout(self.Timeout, Clock())
            except Exception as err:
                self.logger.error(err)
                
                
    def send_if_ack(self, result):
        """
        This function send the n-th data in the queue if the n-th-1 is ack
        """
        
        for (success, data) in result:
            if success:
                if self.first_data:
                    # If it's the first exchange I don't have to wait the ack of the older one ...
                    self.push(data)
                    self.first_data = False
                else:
                    def_object = defer.Deferred().addCallback(self.push)
                    def_object.addTimeout(self.Timeout, Clock())
                    self.def_until_ack.put(def_object)
                    self.q.put_nowait(data)
            else:
                self.logger.error('Failure :', data.getErrorMessage())
        
    def dataReceived(self, data):
        treated_data = self.Handler(data)
        
        if treated_data:
            self.logger.info("Those data are push in the connection : [%s]" %treated_data)
            self.push(treated_data)

    def push(self, data):
        if data:
            self.transport.write(data)
            
    def connectionLost(self, reason):
        self.logger.warning("Connection lost : %s" %(reason))