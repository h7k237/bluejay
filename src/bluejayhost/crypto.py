import sys
import os
import logging

from hashlib import pbkdf2_hmac
#import cryptography.fernet

# https://stackoverflow.com/questions/69312922/how-to-encrypt-large-file-using-python/71068357#71068357
# https://developers.google.com/tink/encrypt-large-files-or-data-streams

logger = logging.getLogger("bluejayhost")

class Encrypt:
    _PWD_RETRIES = 3
    # Random 16 byte salt
    _PBKDF2_SALT = b"\x1c\xc5y{\xe1uUu\xa2\xde\xa1\x1a\x07\xa6\xf8'"
    _PBKDF2_ITERS = 500_000

    def __init__(self, input_path):
        self.path = input_path
        self.success = False
        self.derived_key = None

    def _validate_input_file(self) -> bool:
        if self.path is None or not os.path.isfile(self.path):
            logger.error(f"Input at: {self.path} does not exist or is invalid")
            return False

        return True

    def _derive_key(self) -> bool:
        retries = Encrypt._PWD_RETRIES

        while retries > 0:
            pwd = input("Enter encryption password:")
            pwd_ver = input("Verify encryption password:")

            if pwd == pwd_ver:
                break

            logger.error("Passwords don't match")
            retries -= 1

        if retries == 0:
            logger.error("Failed to get encryption key")
            return False

        self.derived_key = pbkdf2_hmac('sha256', pwd.encode(),
                                       Encrypt._PBKDF2_SALT, Encrypt._PBKDF2_ITERS)
        logger.debug(f"Derived key: {self.derived_key}")

        return True

    def execute(self, output_path) -> bool:
        if not self._validate_input_file():
            return False

        if not self._derive_key():
            return False

        logger.debug(f"Successfully created encrypted file at: {output_path}")
        return True
