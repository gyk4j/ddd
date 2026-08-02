#!/bin/env python

import logging
import os

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
    
    def main(self):
        data = "note the string case"
        self.logger.debug(data)
        modified_data = data.upper()
        self.logger.debug(modified_data)

if __name__ == "__main__":
    app = DDD()
    app.main()
    
    
