#!py -3

import logging
import os
import io
import hashlib
from pathlib import Path
from typing import TypeVar, Generic, List, Type, Iterable, Protocol
from abc import ABC, abstractmethod
from collections import namedtuple
import csv
from datetime import datetime

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

FileHash = namedtuple('FileHash', [ 'file', 'size', 'md5', 'mtime' ])

##class FileHash:
##    def __init__(self, file: str, size: int, md5: bytes):
##        self._file: str = file
##        self._size: int = size
##        self._md5: bytes = md5
##    
##    @property
##    def file(self) -> str:
##        return self._file
##    
##    @file.setter
##    def file(self, file: str):
##        self._file = file
##        
##    @property
##    def size(self) -> int:
##        return self._size
##    
##    @size.setter
##    def size(self, size: int):
##        self._size = size
##        
##    @property
##    def md5(self) -> bytes:
##        return self._md5
##    
##    @md5.setter
##    def md5(self, md5: bytes):
##        self._md5 = md5

class FileHashRepository(CrudRepository[FileHash, bytes], Protocol):
    
    def find_by_name(self) -> Iterable[T]:
        pass

class ListRepository(FileHashRepository):
    def __init__(self):
        self.logger = Logger.get_logger()
        self.entries = list()
        
    def save(self, entity: Type[T]) -> Type[T]:
        self.entries.append(entity)
        return entity

    def find_one(self, primary_key: ID) -> T:
        self.logger.debug("Searching for " + primary_key.hex() + "...")
        found = [ entity for entity in self.entries if entity.md5 == primary_key ]
        
        if len(found) != 1:
            self.logger.warning(str(len(found)) + " found.")
            return None
        else:            
            return found[0]

    def find_all(self) -> Iterable[T]:
        found = [ entity for entity in self.entries ]
        return found

    def count(self) -> int:
        return len(self.entries)

    def delete(self, entity: T) -> None:
        self.entries.remove(entity)

    def exists(self, primary_key: ID) -> bool:
        return self.find_one(primary_key) is not None

    def find_by_name(self, name: str) -> Iterable[T]:
        found = [ entry for entry in self.entries if entry.file == name ]
        return found
        
class CsvRepository(ListRepository):
    FILENAME = 'ddd.csv'
    FIELDS = ['md5', 'mtime', 'size', 'file']
    
    def __init__(self):
        self.logger = Logger.get_logger()
        self.logger.debug('CsvRepository.__init__() called')
        super().__init__()

    def __enter__(self):
        self.logger.debug('CsvRepository.__enter__() called')
        fp = Path(self.FILENAME)

        if fp.exists():
            self.logger.debug('Reading CSV')
            with open(self.FILENAME, 'r', newline='', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)

                fields = next(csvreader)
                for row in csvreader:     # Read rows
                    h = FileHash(row[3], int(row[2]), bytes.fromhex(row[0]), float(row[1]))
                    super().save(h)
        else:
            self.logger.debug('No CSV')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug('CsvRepository.__exit__() called')

        if len(super().find_all()) > 0:
            self.logger.debug('Writing CSV')
            with open(self.FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(self.FIELDS)

                for entry in super().find_all():
                    csvwriter.writerow([ entry.md5.hex(), entry.mtime, entry.size, entry.file ])
        else:
            self.logger.debug('No data to save')
            fp = Path(self.FILENAME)
            if fp.exists():
                self.logger.debug('Deleting empty CSV')
                fp.unlink()

class DDD:
    BUFFER_SIZE = 8192

    logger = None

    def __init__(self, repo):        
        self.logger = Logger.get_logger()
        self.repository = repo
        
    def hash_file(self, file) -> (bytes, int):
        md5: bytes = b''
        size: int = -1
        
        with file.open("rb") as f:
            # Get file hash
            digest = hashlib.md5()
            while chunk := f.read(self.BUFFER_SIZE):
                digest.update(chunk)
            md5 = digest.digest()
            
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

                if len(self.repository.find_by_name(str(path))) == 0:
                    (md5, size) = self.hash_file(path)
                    mtime = path.stat().st_mtime
                    # self.logger.debug("      %s:%s:%d" % (md5, path, size))
                    self.repository.save(FileHash(str(path), size, md5, mtime))
                else:
                    self.logger.debug("* Skipped %s" % (path))
                
    def test(self):
        self.logger.debug("--- find_all ---")
        fa = self.repository.find_all()
        for i, v in enumerate(fa):
            dt = datetime.fromtimestamp(v.mtime)
            self.logger.debug("      %s:%s:%s:%d" % (v.md5.hex(), v.file, dt, v.size))
            
        self.logger.debug("--- find_one ---")
        fo = self.repository.find_one(bytes.fromhex('b38a304f579c28439f3defe073685732'))
        if fo is not None:
            dt = datetime.fromtimestamp(fo.mtime)
            self.logger.debug("      %s:%s:%s:%d" % (fo.md5.hex(), fo.file, dt, fo.size))
        else:
            self.logger.warning('Zero or multiple entries found.')
        
        self.logger.debug("--- find_by_name ---")
        fbn = self.repository.find_by_name('0.jpg')
        for i, v in enumerate(fbn):
            dt = datetime.fromtimestamp(v.mtime)
            self.logger.debug("      %s:%s:%s:%d" % (v.md5.hex(), v.file, dt, v.size))
            
        self.logger.debug("--- exists ---")
        e = self.repository.exists(bytes.fromhex('b38a304f579c28439f3defe073685732'))
        self.logger.debug("      %s" % (e))
    
    def main(self):
        self.process('C:\Windows\Web\Wallpaper')
        self.test()

if __name__ == "__main__":
    Logger.init_logger()
    with CsvRepository() as repository:
        app = DDD(repository)
        app.main()
    
    
