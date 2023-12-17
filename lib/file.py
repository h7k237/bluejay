import sys
import os
import shutil
import logging
from typing import Optional

logger = logging.getLogger("bluejayhost")

def validate_path(path) -> bool:
    if path is None:
        logger.error("Path {path} is not set")
        return False
    elif not os.path.exists(path):
        logger.error("Path {path} does not exist")
        return False
    return True

def validate_path_as_file(path) -> bool:
    if not validate_path(path):
        return False
    elif not os.path.isfile(path):
        logger.error("Path {path} is not a regular file")
        return False
    return True

def validate_path_as_dir(path) -> bool:
    if not validate_path(path):
        return False
    elif not os.path.isdir(path):
        logger.error("Path {path} is not a directory")
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

    def path(self) -> Optional[str]:
        if self.dir is None:
            logger.error(f'File directory not set: {self}')
            return None

        if self.basename is None:
            if (self.git_head is None or
                    self.timestamp is None or
                    self.ext is None):
                logger.error(f'Required file params not set: {self}')
                return None

            self.basename = f'{self.git_head}_{self.timestamp}.{self.ext}'

        return os.path.join(self.dir, self.basename)

    def valid(self) -> bool:
        path = self.path()
        if path is None:
            return False

        return (os.path.isfile(path) and
                self.git_head is not None and
                self.timestamp is not None and
                self.ext is not None)

class CompressedFile(File):
    _COMPRESSED_EXT = 'tar.gz'

    def __init__(self, *args):
        super().__init__(*args)

        if self.ext is None:
            self.ext = CompressedFile._COMPRESSED_EXT

    def __repr__(self):
        return super().__repr__()

    def valid(self) -> bool:
        return (super().valid() and
                self.ext == CompressedFile._COMPRESSED_EXT)

class RevisionFile(File):
    _REVISION_EXT = 'rev'

    def __init__(self, *args):
        super().__init__(*args)

        if self.ext is None:
            self.ext = RevisionFile._REVISION_EXT

    def __repr__(self):
        return super().__repr__()

    def valid(self) -> bool:
        return (super().valid() and
                self.ext == RevisionFile._REVISION_EXT)
