import sys
import os
import logging

from . import file

from getpass import getpass
from hashlib import pbkdf2_hmac
import base64

# https://stackoverflow.com/questions/69312922/how-to-encrypt-large-file-using-python/71068357#71068357
# https://developers.google.com/tink/encrypt-large-files-or-data-streams
import struct
from cryptography.fernet import Fernet

logger = logging.getLogger("bluejayhost")

class Crypto:
    _PWD_RETRIES = 3
    _PWD_MAX_LEN = 1024
    _PBKDF2_SALT = b'bluejayhostbadsaltedinit' # 24 bytes with ASCII encoding
    _PBKDF2_ITERS = 40_000
    _PBKDF2_DKLEN = 32
    _CHUNK_LEN = (1 << 16) # 64KB

    def __init__(self):
        self.derived_key = None

    def _derive_key(self) -> bool:
        retries = Crypto._PWD_RETRIES

        while retries > 0:
            pwd = getpass("Enter encryption password:")
            pwd_ver = getpass("Verify encryption password:")

            if (pwd == pwd_ver and
                    len(pwd) > 0 and
                    len(pwd) < Crypto._PWD_MAX_LEN):
                break

            if len(pwd) == 0:
                logger.error("Password can't be empty")
            elif len(pwd) >= Crypto._PWD_MAX_LEN:
                logger.error(f"Password can't be longer than {Crypto._PWD_MAX_LEN} chars")
            else:
                logger.error("Passwords don't match")
            retries -= 1

        if retries == 0:
            logger.error("Failed to get encryption key")
            return False

        dk_bytes = pbkdf2_hmac(
            'sha256', pwd.encode(),
            Crypto._PBKDF2_SALT, Crypto._PBKDF2_ITERS,
            dklen=Crypto._PBKDF2_DKLEN)

        self.derived_key = base64.urlsafe_b64encode(dk_bytes)
        logger.debug(f"Derived key: {self.derived_key}")

        return True

class Encrypt(Crypto):
    def __init__(self, input_path):
        super().__init__()
        self.path = input_path

    def _encrypt(self, output_path) -> bool:
        fernet = Fernet(self.derived_key)

        with open(self.path, 'rb') as fi, open(output_path, 'wb') as fo:
            for chunk in iter(lambda: fi.read(Crypto._CHUNK_LEN), b''):
                try:
                    enc = fernet.encrypt(chunk)
                except Exception as exc:
                    logger.error(f'fernet.encrypt encountered exception: {repr(exc)}')
                    return False

                fo.write(struct.pack('<I', len(enc)))
                fo.write(enc)

        return True

    def execute(self, output_path) -> bool:
        if not file.validate_path_as_file(self.path):
            return False

        if not self._derive_key():
            return False

        if not self._encrypt(output_path):
            return False

        logger.debug(f"Successfully created encrypted file at: {output_path}")

        return True

class Decrypt(Crypto):
    def __init__(self, input_path):
        super().__init__()
        self.path = input_path

    def _decrypt(self, output_path) -> bool:
        fernet = Fernet(self.derived_key)

        with open(self.path, 'rb') as fi, open(output_path, 'wb') as fo:
            while True:
                enc_size_data = fi.read(4)
                if enc_size_data == b'':
                    break
                enc_size = struct.unpack('<I', enc_size_data)[0]
                chunk = fi.read(enc_size)
                try:
                    dec = fernet.decrypt(chunk)
                except Exception as exc:
                    logger.error(f'fernet.decrypt encountered exception: {repr(exc)}')
                    return False

                fo.write(dec)

        return True

    def execute(self, output_path) -> bool:
        if not file.validate_path_as_file(self.path):
            return False

        if not self._derive_key():
            return False

        if not self._decrypt(output_path):
            return False

        logger.debug(f"Successfully created decrypted file at: {output_path}")

        return True
