import sys
import os
import shutil
import logging
import struct

def validate_path(path) -> bool:
    if path is None:
        logging.error("Path {path} is not set")
        return False
    elif not os.path.exists(path):
        logging.error("Path {path} does not exist")
        return False
    return True

def validate_path_as_file(path) -> bool:
    if not validate_path(path):
        return False
    elif not os.path.isfile(path):
        logging.error("Path {path} is not a regular file")
        return False
    return True

def validate_path_as_dir(path) -> bool:
    if not validate_path(path):
        return False
    elif not os.path.isdir(path):
        logging.error("Path {path} is not a directory")
        return False
    return True

class File:
    """This class is used to represent a vault file of a specified type.

    The file path is obtained by:
        <dir>/<basename>_<git_head>_<timestamp>.<ext>
    """
    def __init__(self, *args):
        # self.ext to be set by derived classes if creating the file
        self.dir = None
        self.basename = None
        self.git_head = None
        self.timestamp = None
        self.ext = None
        self.version = 0x00

        if len(args) == 1:
            self._init_from_path(args[0])
        elif (len(args) == 3):
            self._init_from_args(args[0], args[1], args[2])

    def __repr__(self):
        return (f'<dir={self.dir},'
                f'basename={self.basename},'
                f'git_head={self.git_head},'
                f'timestamp={self.timestamp},'
                f'ext={self.ext}>')

    def _init_from_path(self, path):
        self.dir = os.path.dirname(path)
        self.basename = os.path.basename(path)

        name = self.basename
        ext_idx = name.find('.')
        if ext_idx < 0:
            self.ext = ''
        else:
            name = self.basename[0:ext_idx]
            self.ext = self.basename[ext_idx + 1:]

        name_parts = name.split('_')
        if len(name_parts) == 2:
            self.git_head = name_parts[0]
            self.timestamp = name_parts[1]

    def _init_from_args(self, dir, git_head, timestamp):
        self.dir = dir
        self.git_head = git_head
        self.timestamp = timestamp

    def path(self) -> str:
        """Forms the path from the file attributes.

        Call the valid method before using this function.
        """
        if self.basename is None:
            self.basename = f'{self.git_head}_{self.timestamp}.{self.ext}'

        return os.path.join(self.dir, self.basename)

    def valid(self) -> bool:
        """Checks that the file attributes are valid.

        The file may not be created yet.
        """
        if self.git_head is None:
            logging.error("File git_head is not set")
            return False

        if self.timestamp is None:
            logging.error("File timestamp is not set")
            return False

        if self.ext is None:
            logging.error("File extension is not set")
            return False

        return True

    def get_version(self) -> int:
        return self.version

class CompressedFile(File):
    _COMPRESSED_EXT = 'tar.gz'

    def __init__(self, *args):
        super().__init__(*args)

        if self.ext is None:
            self.ext = CompressedFile._COMPRESSED_EXT

    def __repr__(self):
        return super().__repr__()

    def valid(self) -> bool:
        if not super().valid():
            return False

        if self.ext != CompressedFile._COMPRESSED_EXT:
            logging.error("Invalid compressed file extension: {self.ext}")
            return False

        return True

class RevisionFile(File):
    """Represents a Bluejay revision file.

    The file starts with a 4 byte header consisting of 3 magic bytes and 1 version byte.
    """
    _REV_EXT = 'rev'
    _REV_MAG0 = 0x62 #b
    _REV_MAG1 = 0x6A #j
    _REV_MAG2 = 0x72 #r
    _REV_VERSION_CUR = 0x01
    _REV_VERSION_MAX = 0x01
    _BYTEMASK = 0x000000FF

    def __init__(self, *args):
        super().__init__(*args)

        if self.ext is None:
            self.ext = RevisionFile._REV_EXT

    def __repr__(self):
        return super().__repr__()

    @staticmethod
    def get_header() -> bytes:
        header_data = (RevisionFile._REV_MAG0 << 24 |
                       RevisionFile._REV_MAG1 << 16 |
                       RevisionFile._REV_MAG2 << 8 |
                       RevisionFile._REV_VERSION_CUR)
        return struct.pack('<I', header_data)

    def check_header(self) -> bool:
        """Returns True if the file is a valid RevisionFile.

        This function also sets the self.version attribute for the RevisionFile.
        """
        path = self.path()
        with open(path, 'rb') as fi:
            header_bytes = fi.read(4)

        header = struct.unpack('<I', header_bytes)[0]

        if not (((header >> 24) & RevisionFile._BYTEMASK) == RevisionFile._REV_MAG0 and
                ((header >> 16) & RevisionFile._BYTEMASK) == RevisionFile._REV_MAG1 and
                ((header >> 8) & RevisionFile._BYTEMASK) == RevisionFile._REV_MAG2):
            logging.error("Invalid revision file magic.")
            return False

        self.version = (header & RevisionFile._BYTEMASK)
        if not (self.version >= 0 and self.version <= RevisionFile._REV_VERSION_MAX):
            logging.error("Invalid version in revision file.")
            return False

        return True

    def valid(self) -> bool:
        if not super().valid():
            return False

        if self.ext != RevisionFile._REV_EXT:
            logging.error("Invalid revision file extension: {self.ext}")
            return False

        return True
