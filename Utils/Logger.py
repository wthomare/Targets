# -*- coding: utf-8 -*-

import logging



# =============================================================================
class Logger(object):

    # =========================================================================
    def __init__(self, __name__:str, level: int = None):
        self.logger = logging.getLogger(__name__)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        if level is None:
            self.level = logging.DEBUG
        else:
            self.level = level

    # =========================================================================
    def add_StreamHandler(self):
        c_handler = logging.StreamHandler()
        c_handler.setFormatter(self.formatter)
        c_handler.setLevel(self.level)
        self.logger.addHandler(c_handler)
        
    # =========================================================================
    def add_FileHandler(self, file:str = None):
        if file is None:
            self.logger.error("You should provide the file name of the file handler")
            raise AttributeError
        f_handler = logging.FileHandler(file)
        f_handler.setFormatter(self.formatter)
        f_handler.setLevel(self.level)
        self.logger.addHandler(f_handler)
