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
    def __init__(self, file: str, md5: bytes, size: int):
        self._file: str = file
        self._md5: bytes = md5
        self._size: int = size
    
    @property
    def file(self) -> str:
        return self._file
    
    @file.setter
    def file(self, file: str):
        self._file = file
        
    @property
    def md5(self) -> bytes:
        return self._md5
    
    @md5.setter
    def md5(self, md5: bytes):
        self._md5 = md5
        
    @property
    def size(self) -> int:
        return self._size
    
    @size.setter
    def size(self, size: int):
        self._size = size

class FileHashRepository(CrudRepository[FileHash, bytes], Protocol):
    
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
        
class CsvRepository(FileHashRepository):
    def __init__(self):
        self.logger = Logger.get_logger()
        self.entries = list()
        # self.idx - dict()
        
    def save(self, entity: Type[T]) -> Type[T]:        
        self.entries.append(entity)
        
        # Add to index
        # if entity.md5 not in self.idx:
            # self.idx[entity.md5] = dict()
            
        # if entity.size not in self.idx[entity.md5]:
            # self.idx[entity.md5][entity.size] = list()
            
        # self.idx[entity.md5][entity.size].append(entity)
        
        return entity

    def find_one(self, primary_key: ID) -> T:
        # Not found
        # if primary_key not in self.idx:
            # return None
    
        # Not found
        # if len(list(self.idx[primary_key])) == 0:
            # return None
        
        # sizes = list(self.idx[primary_key])
        # Collision found; 1 md5 with multiple sizes
        # if len(sizes) > 1:
            # return None
        
        # Duplicates found; 1 md5 with multiple files
        # files = self.idx[primary_key][sizes[0]]
        # if len(files) > 1:
            # return None
            
        # Found 1 entry        
        # t = files[0]
        # return t
        
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
        # found = [ entry for entry in self.entries if entry.md5 == entity.md5 and entry.size == entity.size and entry.file == entity.file ]                
        self.entries.remove(entity)

    def exists(self, primary_key: ID) -> bool:
        return self.find_one(primary_key) is not None

    def find_by_name(self, name: str) -> Iterable[T]:
        found = [ entry for entry in self.entries if entry.file.endswith(name) ]
        return found

class DDD:
    BUFFER_SIZE = 8192

    logger = None

    def __init__(self):        
        self.logger = Logger.get_logger()
        self.repository = CsvRepository()
        
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
                (md5, size) = self.hash_file(path)
                # self.logger.debug("      %s:%s:%d" % (md5, path, size))
                self.repository.save(FileHash(str(path), md5, size))
                
    def test(self):
        self.logger.debug("--- find_all ---")
        fa = self.repository.find_all()
        for i, v in enumerate(fa):
            self.logger.debug("      %s:%s:%d" % (v.md5.hex(), v.file, v.size))
            
        self.logger.debug("--- find_one ---")
        fo = self.repository.find_one(bytes.fromhex('b38a304f579c28439f3defe073685732'))
        self.logger.debug("      %s:%s:%d" % (fo.md5.hex(), fo.file, fo.size))
        
        self.logger.debug("--- find_by_name ---")
        fbn = self.repository.find_by_name('0.jpg')
        for i, v in enumerate(fbn):
            self.logger.debug("      %s:%s:%d" % (v.md5.hex(), v.file, v.size))
            
        self.logger.debug("--- exists ---")
        e = self.repository.exists(bytes.fromhex('b38a304f579c28439f3defe073685732'))
        self.logger.debug("      %s" % (e))
    
    def main(self):
        self.process('C:\Windows\Web\Wallpaper')
        self.test()

if __name__ == "__main__":
    Logger.init_logger()
    app = DDD()
    app.main()
    
    
