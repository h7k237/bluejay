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

class Vault(object):
    _TMP_DIR = "/tmp/bluejay"
    _TEMP_DIR = _TMP_DIR + "/.temp"
    _DATETIME_FMT = "%Y%m%dT%H%M%S"

    def __init__(self, vault_path, repo_path):
        self.vault_path = vault_path
        self.repo_path = repo_path

    def __enter__(self):
        os.makedirs(Vault._TEMP_DIR, exist_ok=True)
        self.timestamp = datetime.now().strftime(Vault._DATETIME_FMT)

        return self

    def __exit__(self, type, value, traceback):
        try:
            shutil.rmtree(Vault._TEMP_DIR)
        except Exception as exc:
            logging.warning(f'Removing: {Vault._TEMP_DIR} encountered exception: {repr(exc)}')

class VaultLocker(Vault):
    def __init__(self, vault_path, repo_path):
        super().__init__(vault_path, repo_path)

        self.git_repo = None
        self.git_head = None
        self.compressed_file = None
        self.encrypted_file = None

    def _validate_input(self) -> bool:
        if not file.validate_path_as_dir(Vault._TEMP_DIR):
            return False

        if not file.validate_path_as_dir(self.repo_path):
            return False

        if self.vault_path is None:
            logging.error("Vault directory path is not set")
            return False

        if not os.path.isdir(self.vault_path):
            if (os.path.exists(self.vault_path)):
                logging.error(f"Vault path {self.vault_path} exists and is not a vault directory")
                return False

            prompt = f"Vault directory does not exist at: {self.vault_path}. Create? [y/n]:"
            if str(input(prompt)).lower().strip() == 'y':
                try:
                    os.makedirs(self.vault_path)
                except Exception as exc:
                    logging.error(f"Creating: {self.vault_path} encountered exception: {exc}")
                    return False
            else:
                return False

        return True

    def _init_git_repo(self) -> bool:
        self.git_repo = git.GitRepo(self.repo_path)

        self.git_head = self.git_repo.get_head()
        if self.git_head is None:
            return False

        return True

    def execute(self) -> bool:
        if not self._validate_input():
            return False

        if not self._init_git_repo():
            return False

        self.compressed_file = file.CompressedFile(Vault._TEMP_DIR, self.git_head, self.timestamp)
        compressed_path = self.compressed_file.path()
        if compressed_path is None:
            return False

        logging.debug(f"Compressing the vault into: {compressed_path}")
        if not compress.create_tar_file(self.repo_path, compressed_path):
            return False

        self.encrypted_file = file.RevisionFile(Vault._TEMP_DIR, self.git_head, self.timestamp)
        encrypted_path = self.encrypted_file.path()
        if encrypted_path is None:
            return False

        logging.debug(f"Encrypting the vault into: {encrypted_path}")
        if not crypto.Encrypt(compressed_path).execute(encrypted_path):
            return False

        output_path = file.RevisionFile(self.vault_path, self.git_head, self.timestamp).path()
        if output_path is None:
            return False

        logging.debug(f"Copying the encrypted file into: {output_path}")
        shutil.copyfile(encrypted_path, output_path)

        print(f"Output file: {output_path}")

        return True

class VaultUnlocker(Vault):
    def __init__(self, vault_path, repo_path):
        super().__init__(vault_path, repo_path)

        self.git_repo = None
        self.git_head = None
        self.compressed_file = None
        self.encrypted_file = None

    def _get_latest_revision(self) -> bool:
        if not os.path.isdir(self.vault_path):
            logging.error(f"Failed to get revision file from {self.vault_path}.")
            return False

        rev_file_objs = []
        for path, dirs, files in os.walk(self.vault_path):
            for f in files:
                fpath = os.path.join(path, f)
                if not os.path.isfile(fpath):
                    continue

                rev_file_obj = file.RevisionFile(fpath)
                if rev_file_obj.valid():
                    rev_file_objs.append(rev_file_obj)

        if len(rev_file_objs) == 0:
            logging.error("No valid revision files in vault directory")
            return False

        rev_file_objs.sort(key=lambda obj: obj.timestamp, reverse=True)

        for obj in rev_file_objs:
            prompt = f"Use the revision file {obj.path()}? [y/n]:"
            input_char = str(input(prompt)).lower().strip()
            if input_char == 'y':
                self.encrypted_file = obj
                return True
            elif input_char == 'n':
                continue
            else:
                break

        logging.error("Failed to get latest revision file.")
        return False

    def _validate_input(self) -> bool:
        if not file.validate_path_as_dir(Vault._TEMP_DIR):
            return False

        if self.repo_path is None:
            logging.error("Output git repo path not set")
            return False

        if os.path.exists(self.repo_path):
            logging.error("Repo path already exists. Please clear the path.")
            return False

        if os.path.isdir(self.vault_path):
            if not self._get_latest_revision():
                return False
        else:
            self.encrypted_file = file.RevisionFile(self.vault_path)

        if self.encrypted_file is None or not self.encrypted_file.valid():
            logging.error("Error initializing input revision file.")
            return False

        return True

    def execute(self) -> bool:
        if not self._validate_input():
            return False

        encrypted_path = self.encrypted_file.path()
        if encrypted_path is None:
            return False

        self.compressed_file = file.CompressedFile(
            Vault._TEMP_DIR,
            self.encrypted_file.git_head,
            self.encrypted_file.timestamp)
        compressed_path = self.compressed_file.path()
        if not compressed_path:
            return False

        logging.debug(f"Decrypting the revision file into: {compressed_path}")
        if not crypto.Decrypt(encrypted_path).execute(compressed_path):
            return False

        logging.debug(f"Uncompressing the vault into: {self.repo_path}")
        if not compress.extract_tar_file(compressed_path, self.repo_path):
            return False

        print(f"Output git repo: {self.repo_path}")

        return True
