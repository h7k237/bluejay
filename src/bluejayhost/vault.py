import sys
import os
import shutil
import argparse
import logging
from datetime import datetime

from . import file
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
        self.compressed_file = None
        self.encrypted_file = None
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
            prompt = f"Vault directory does not exist at: {self.vault_path}. Create? [y/n]:"
            if str(input(prompt)).lower().strip() == 'y':
                try:
                    os.makedirs(self.vault_path)
                except Exception as exc:
                    logger.error(f"Creating: {self.vault_path} encountered exception: {exc}")
                    return False
            else:
                return False

        if self.git_repo is None:
            logger.error(f"Git repo object not set")
            return False

        self.git_head = self.git_repo.get_head()
        if self.git_head is None:
            logger.error("Unable to get git head commit. Please initialize the git repository.")
            return False

        return True

    def _compress(self, input_path, output_path) -> bool:
        return compress.create_tar_file(input_path, output_path)

    def _encrypt(self, input_path, output_path) -> bool:
        return crypto.Encrypt(input_path).execute(output_path)

    def lock(self) -> bool:
        if not os.path.isdir(Vault._TEMP_DIR):
            logger.error(f"Temp directory at: {Vault._TEMP_DIR} does not exist")
            return False

        if not self._validate_input():
            return False

        self.compressed_file = file.CompressedFile(Vault._TEMP_DIR, self.git_head, self.timestamp)
        self.encrypted_file = file.RevisionFile(Vault._TEMP_DIR, self.git_head, self.timestamp)

        compressed_path = self.compressed_file.path()
        logger.debug(f"Compressing the vault into: {compressed_path}")
        if not self._compress(self.path, compressed_path):
            return False

        encrypted_path = self.encrypted_file.path()
        logger.debug(f"Encrypting the vault into: {encrypted_path}")
        if not self._encrypt(compressed_path, encrypted_path):
            return False

        logger.debug("Encryption successful")

        self.output_path = file.RevisionFile(self.vault_path, self.git_head, self.timestamp).path()

        logger.debug(f"Copying the encrypted file into: {self.output_path}")
        shutil.copyfile(encrypted_path, self.output_path)

        print(f"Output file: {self.output_path}")

        return True

class VaultUnlock(Vault):
    def __init__(self, input_path, git_repo_path):
        super().__init__()

        self.path = input_path
        self.git_repo_path = git_repo_path
        self.git_repo = None
        self.git_head = None
        self.vault_path = None
        self.compressed_file = None
        self.encrypted_file = None
        self.uncompressed_path = None
        self.decrypted_path = None
        self.output_path = None

    def _get_latest_revision(self):
        if not os.path.isdir(self.vault_path):
            return

        rev_file_paths = os.listdir(self.vault_path)
        rev_file_paths = [f'{self.vault_path}/{file}' for file in rev_file_paths]
        rev_file_paths = [file for file in rev_file_paths if os.path.isfile(file)]
        if len(rev_file_paths) == 0:
            logger.error("No revision files in vault directory")
            return

        rev_file_objs = [file.RevisionFile(path) for path in rev_file_paths]
        rev_file_objs = [obj for obj in rev_file_objs if obj.valid()]
        if len(rev_file_objs) == 0:
            logger.error("No valid revision files in vault directory")
            return

        rev_file_objs.sort(key=lambda obj: obj.timestamp, reverse=True)

        for obj in rev_file_objs:
            prompt = f"Use the revision file {obj.path()}? [y/n]:"
            input_char = str(input(prompt)).lower().strip()
            if input_char == 'y':
                self.encrypted_file = obj
                break
            elif input_char == 'n':
                continue
            else:
                break

    def _validate_input(self) -> bool:
        if self.path is None:
            logger.error("Input path is not set")
            return False

        if self.git_repo_path is None:
            logger.error("Output git repo path not set")
            return False

        if os.path.exists(self.git_repo_path):
            logger.error("Output git repo path already exists. Please clear the path.")
            return False

        if os.path.isdir(self.path):
            self.vault_path = self.path
            self._get_latest_revision()
        else:
            self.encrypted_file = file.RevisionFile(self.path)

        if self.encrypted_file is None or not self.encrypted_file.valid():
            logger.error("Error initializing input revision file")
            return False

        return True

    def _uncompress(self, input_path, output_path) -> bool:
        return compress.extract_tar_file(input_path, output_path)

    def _decrypt(self, input_path, output_path) -> bool:
        return crypto.Decrypt(input_path).execute(output_path)

    def unlock(self) -> bool:
        if not os.path.isdir(Vault._TEMP_DIR):
            logger.error(f"Temp directory at: {Vault._TEMP_DIR} does not exist")
            return False

        if not self._validate_input():
            return False

        """
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
"""

        return True
