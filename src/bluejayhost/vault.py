import sys
import os
import shutil
import argparse
import logging
from datetime import datetime

from . import compress
from . import git
from . import aes

logger = logging.getLogger("bluejayhost")

class Vault:
    def __init__(self, vault_path):
        self._TOP_DIR = "/tmp/bluejay"
        self._TEMP_DIR = self._TOP_DIR + "/.temp"
        os.makedirs(self._TEMP_DIR, exist_ok=True)
        self._DATETIME_FMT = "%Y%m%dT%H%M%S"

        self.path = vault_path
        self.git_head = git.get_git_head(vault_path)
        self.timestamp = datetime.now().strftime(self._DATETIME_FMT)
        self.compressed_path = f"{self._TEMP_DIR}/{self.git_head}_{self.timestamp}.tar.gz"
        self.encrypted_path = f"{self._TEMP_DIR}/{self.git_head}_{self.timestamp}.enc"

    """
    def __del__(self):
        try:
            shutil.rmtree(self._TEMP_DIR)
        except Exception as exc:
            logger.error(f"Removing: {self._TEMP_DIR} encountered exception: {exc}")
    """

    def _compress(self):
        """Compress the vault.

        Helper function that compresses the vault at self.path into a file in
        the self._TEMP_DIR directory. The output filename has the form:
        <self._TEMP_DIR>/<self.git_head>_<timestamp>.tar.gz
        """
        if self.path is None:
            logger.error(f"Input path is not set")
            return

        if not os.path.isdir(self._TEMP_DIR):
            logger.error(f"Temp directory at: {self._TEMP_DIR} does not exist")
            return

        compress.create_tar_file(self.path, self.compressed_path)

    def lock(self):
        logger.info(f"Compressing the vault")
        self._compress()

    def unlock(self):
        logger.info(f"Unlocking the vault at {self.path}")
        print(f"unlocking the vault at {self.path}!")


