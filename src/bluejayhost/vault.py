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

    def __init__(self):
        os.makedirs(Vault._TEMP_DIR, exist_ok=True)
        self.timestamp = datetime.now().strftime(Vault._DATETIME_FMT)

    def __del__(self):
        try:
            shutil.rmtree(Vault._TEMP_DIR)
        except Exception as exc:
            logger.error(f"Removing: {Vault._TEMP_DIR} encountered exception: {exc}")

class VaultLock(Vault):
    def __init__(self, input_path, vault_path):
        super().__init__()

        self.path = input_path
        self.git_repo = git.GitRepo(input_path)
        self.git_head = None
        self.vault_path = vault_path
        self.compressed_path = None
        self.encrypted_path = None
        self.output_path = None

    def _validate_input(self) -> bool:
        if self.path is None:
            logger.error("Input path is not set")
            return False

        if not os.path.isdir(self.path):
            logger.error(f"Input path directory does not exist at: {self.path}")
            return False

        if self.vault_path is None:
            logger.error("Vault directory path is not set")
            return False

        if not os.path.isdir(self.vault_path):
            prompt = f"Vault directory does not exist at: {self.vault_path}. Create[y/n]?"
            if str(input(prompt)).lower().strip() == 'y':
                os.makedirs(self.vault_path)
            else:
                return False

        if self.git_repo is None:
            logger.error(f"Git repo object not set")
            return False

        self.git_head = self.git_repo.get_head()
        if self.git_head is None:
            logger.error("Unable to get git head commit")
            return False

        return True

    def _compress(self, input_path, output_path) -> bool:
        return compress.create_tar_file(input_path, output_path)

    def _encrypt(self, input_path, output_path) -> bool:
        return crypto.Encrypt(input_path).execute(output_path)

    def lock(self) -> bool:
        if not self._validate_input():
            return False

        if not os.path.isdir(Vault._TEMP_DIR):
            logger.error(f"Temp directory at: {Vault._TEMP_DIR} does not exist")
            return False

        self.compressed_path = f"{Vault._TEMP_DIR}/{self.git_head}_{self.timestamp}.tar.gz"
        self.encrypted_path = f"{Vault._TEMP_DIR}/{self.git_head}_{self.timestamp}.rev"

        logger.debug("Compressing the vault")
        if not self._compress(self.path, self.compressed_path):
            return False

        logger.debug("Encrypting the vault")
        if not self._encrypt(self.compressed_path, self.encrypted_path):
            return False

        logger.debug("Encryption successful")

        self.output_path = f"{self.vault_path}/{os.path.basename(self.encrypted_path)}"
        shutil.copyfile(self.encrypted_path, self.output_path)

        print(f"Output file: {self.output_path}")

        return True
