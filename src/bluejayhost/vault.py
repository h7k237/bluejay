import sys
import os
import argparse
import tarfile
import logging

logger = logging.getLogger("bluejayhost")

class Vault:
    def __init__(self):
        _vault_path = f""

    def lock(self):
        asdf

    def unlock(self):
        asdf

"""
The BluejaySecureElement is a git repo of sensitive data that is either specified by the user or
found in the /tmp/bluejay/se directory.
"""

class InputNotFoundError(Exception):
    def __str__(self):
        return f'Unable to find BluejaySecureElement! Please specify a valid git repo.'

def validate_input():
    parser = argparse.ArgumentParser(description='Lock the BluejaySecureElement')
    parser.add_argument('-i', dest='input_path', help='Path to the BluejaySecureElement git repo')
    args = parser.parse_args()
    return args.input_path

def find_input():
    input_path = validate_input()

    if input_path is None:
        input_path = '/tmp/bluejay/se'

    if not os.path.exists(input_path + '/.git'):
        raise InputNotFoundError
    else:
        print(f"Found BluejaySecureElement at {input_path}. Proceeding...")

    return input_path

def compress_path(input_path, output_path):
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(input_path, arcname=os.path.basename(input_path))

    print(f"BluejaySecureElement compressed at {output_path}. Proceeding...")

def aes_encrypt_file(input_file, output_file):
    # TODO

if __name__ == "__main__":
    try:
        input_path = find_input()

        if not os.path.exists('/tmp/bluejay'):
            os.makedirs('/tmp/bluejay')

        compressed_filename = '/tmp/bluejay/se.tgz'
        encrypted_filename = '/tmp/bluejay/se.enc'

        compress_path(input_path, compressed_filename)

        aes_encrypt_file(compressed_filename, encrypted_filename)

    except Exception as e:
        print(f'ERROR: {e}')
