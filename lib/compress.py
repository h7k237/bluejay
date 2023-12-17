import sys
import os
import logging
import tarfile

def create_tar_file(input_path, output_path) -> bool:
    if input_path is None or output_path is None:
        logging.error(f'create_tar_file: params not set')
        return False

    logging.debug(f'create_tar_file: creating from: {input_path} into: {output_path}')
    try:
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(input_path, arcname='')
    except Exception as exc:
        logging.error(f'create_tar_file encountered exception: {repr(exc)}')
        return False

    return True

def extract_tar_file(input_path, output_path) -> bool:
    if input_path is None or output_path is None:
        logging.error(f'extract_tar_file: params not set')
        return False

    logging.debug(f'extract_tar_file: extracting from: {input_path} into: {output_path}')
    try:
        with tarfile.open(input_path, "r:gz") as tar:
            tar.extractall(path=output_path)
    except Exception as exc:
        logging.error(f'extract_tar_file encountered exception: {repr(exc)}')
        return False

    return True
