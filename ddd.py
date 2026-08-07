#!py -3

import logging
import os
import io
import hashlib
from pathlib import Path
from typing import TypeVar, Generic, List, Type, Iterable, Protocol
from abc import ABC, abstractmethod

# Declare type variable
T = TypeVar('T')
ID = TypeVar('ID')

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

class CrudRepository(Generic[T, ID], Protocol):
    
    def save(self, entity: Type[T]) -> Type[T]:
        pass

    def find_one(self, primary_key: ID) -> T:
        pass

    def find_all(self) -> Iterable[T]:
        pass

    def count(self) -> int:
        pass

    def delete(self, entity: T) -> None:
        pass

    def exists(self, primary_key: ID) -> bool:
        pass

class FileHash:
    def __init__(self, file: str, md5: str, size: int):
        self.file = file
        self.md5 = md5
        self.size = size
    
    @property
    def file(self):
        return self.file
    
    @file.setter
    def file(self, file):
        self.file = file
        
    @property
    def md5(self):
        return self.md5
    
    @md5.setter
    def md5(self, md5):
        self.md5 = md5
        
    @property
    def size(self):
        return self.size
    
    @size.setter
    def size(self, size):
        self.size = size

class FileHashRepository(CrudRepository[FileHash, int], Protocol):
    @abstractmethod
    def find_by_name(self) -> Iterable[T]:
        pass

class ListRepository(FileHashRepository):
    def __init__(self):
        self.entries = list()
        
    def save(self, entity: Type[T]) -> Type[T]:
        self.entries.append(entity)
        return entity

    def find_one(self, primary_key: ID) -> T:
        return self.entries[ID]

    def find_all(self) -> Iterable[T]:
        found = [entry for entry in self.entries]
        return found

    def count(self) -> int:
        return len(self.entries)

    def delete(self, entity: T) -> None:
        self.entries.remove(entity)

    def exists(self, primary_key: ID) -> bool:
        return primary_key >= 0 and primary_key < self.count()

    def find_by_name(self, name: str) -> Iterable[T]:
        found = [entry for entry in self.entries if name in entry.file]
        return found

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
    
    
