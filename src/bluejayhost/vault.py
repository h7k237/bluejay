import sys
import os
import shutil
import argparse
import logging
from datetime import datetime

from . import compress
from . import git
from . import crypto

logger = logging.getLogger("bluejayhost")

class Vault:
    _TOP_DIR = "/tmp/bluejay"
    _TEMP_DIR = _TOP_DIR + "/.temp"
    _DATETIME_FMT = "%Y%m%dT%H%M%S"

    def __init__(self, vault_path):
        os.makedirs(Vault._TEMP_DIR, exist_ok=True)

        self.path = vault_path
        self.git_repo = git.GitRepo(vault_path)
        self.timestamp = datetime.now().strftime(Vault._DATETIME_FMT)
        self.compressed_path = None
        self.encrypted_path = None

    """
    def __del__(self):
        try:
            shutil.rmtree(Vault._TEMP_DIR)
        except Exception as exc:
            logger.error(f"Removing: {Vault._TEMP_DIR} encountered exception: {exc}")
    """

    def _validate_vault_dir(self) -> bool:
        if self.path is None:
            logger.error(f"Input path is not set")
            return False

        if not os.path.isdir(self.path):
            logger.error(f"Vault directory does not exist at: {self.path}")
            return False

        if self.git_repo is None:
            logger.error(f"Git repo object not set")
            return False

        return True

    def _compress(self, input_path, output_path) -> bool:
        return compress.create_tar_file(input_path, output_path)

    def _encrypt(self, input_path, output_path) -> bool:
        return crypto.Encrypt(input_path).execute(output_path)

    def lock(self):
        if not self._validate_vault_dir():
            return

        if not os.path.isdir(Vault._TEMP_DIR):
            logger.error(f"Temp directory at: {Vault._TEMP_DIR} does not exist")
            return

        self.git_head = self.git_repo.get_head()
        if self.git_head is None:
            logger.error(f"Unable to get git head commit")
            return

        self.compressed_path = f"{Vault._TEMP_DIR}/{self.git_head}_{self.timestamp}.tar.gz"
        self.encrypted_path = f"{Vault._TEMP_DIR}/{self.git_head}_{self.timestamp}.enc"

        logger.debug(f"Compressing the vault")
        if not self._compress(self.path, self.compressed_path):
            return

        logger.debug(f"Encrypting the vault")
        if not self._encrypt(self.compressed_path, self.encrypted_path):
            return

    def unlock(self):
        if not self._validate_vault_dir():
            return

        logger.debug(f"Unlocking the vault at {self.path}")


