#!/bin/env python

import logging
import os
import io
import hashlib
from pathlib import Path

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
    BUFFER_SIZE = 8192

    logger = None

    def __init__(self):        
        self.logger = Logger.get_logger()
        
    def hash_file(self, file):
        md5 = ''
        size = -1
        
        with file.open("rb") as f:
            # Get file hash
            digest = hashlib.md5()
            while chunk := f.read(self.BUFFER_SIZE):
                digest.update(chunk)
            md5 = digest.hexdigest()
            
            # Get file size
            f.seek(0, os.SEEK_END)
            size = f.tell()
            
        return (md5, size)
        
    def process(self, directory="."):
        for root, dirs, files in os.walk(directory):
            # for d in dirs:
                # self.logger.debug("<DIR> %s\%s" % (root, d))
                
            for file in files:
                path = Path(root, file)
                (md5, size) = self.hash_file(path)
                self.logger.debug("      %s:%s:%d" % (md5, path, size))
    
    def main(self):
        self.process('C:\Windows\Web\Wallpaper')

if __name__ == "__main__":
    Logger.init_logger()
    app = DDD()
    app.main()
    
    
