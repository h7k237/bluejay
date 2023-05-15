import sys
import os
import argparse
import tarfile
import logging

logger = logging.getLogger("bluejayhost")

class Vault:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.vault_git_head = self._get_vault_git_head()
        logger.info(f"Got vault git HEAD as {self.vault_git_head}")

    def lock(self):
        logger.info(f"Locking the vault at {self.vault_path}")
        print(f"Locking the vault at {self.vault_path}!")

    def unlock(self):
        logger.info(f"Unlocking the vault at {self.vault_path}")
        print(f"unlocking the vault at {self.vault_path}!")

    def _get_vault_git_head(self):
        """Get the HEAD commit from the vault"""
        if not self.vault_path:
            return None

        return f"HEAD"

def compress_path(input_path, output_path):
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(input_path, arcname=os.path.basename(input_path))

    print(f"BluejaySecureElement compressed at {output_path}. Proceeding...")

def aes_encrypt_file(input_file, output_file):
    # TODO
    print(f"aes_encrypt_file")

