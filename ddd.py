#!/bin/env python

import logging
import os
import io
import hashlib

class Logger:    
    logger = None
    
    def __init__(self, filename=None):
        if filename is not None:
            logging.basicConfig(
                filename=filename,
                format='%(asctime)s %(levelname)s: %(message)s',
                filemode='w')
        else:
            logging.basicConfig(
                level=logging.DEBUG, 
                format='%(levelname)s: %(message)s')

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

class DDD:
    logger = None

    def __init__(self):
        self.logger = Logger().logger
        
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
    app = DDD()
    app.main()
    
    
