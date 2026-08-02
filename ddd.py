#!/bin/env python

import logging
import os
import io
import hashlib

class Logger:    
    logger = None
    
    @classmethod
    def init_logger(cls, filename=None, level=logging.DEBUG):
        if filename is not None:
            logging.basicConfig(
                filename=filename,
                format='%(asctime)s %(levelname)s: %(message)s',
                filemode='w')
        else:
            logging.basicConfig(
                level=level, 
                format='%(levelname)s: %(message)s')

        cls.logger = logging.getLogger()
        cls.logger.setLevel(level)
    
    @classmethod
    def get_logger(cls):
        return cls.logger

class DDD:
    logger = None

    def __init__(self):        
        self.logger = Logger.get_logger()
        
    def process(self, directory="."):
        for root, dirs, files in os.walk(directory):
            # for d in dirs:
                # self.logger.debug("<DIR> %s\%s" % (root, d))
                
            for file in files:
                with open("{}\{}".format(root, file), "rb") as f:
                    digest = hashlib.md5()
                    while chunk := f.read(8192):
                        digest.update(chunk)
                    md5 = digest.hexdigest()
                    f.seek(0, os.SEEK_END)
                    size = f.tell()
                self.logger.debug("      %s:%s\%s:%d" % (md5, root, file, size))
    
    def main(self):
        self.process('C:\Windows\Web\Wallpaper')

if __name__ == "__main__":
    Logger.init_logger()
    app = DDD()
    app.main()
    
    
