import sys
import os
import logging
import tarfile

logger = logging.getLogger("bluejayhost")

def create_tar_file(input_path, output_path) -> bool:
    """Compress the input into a tar file"""
    if input_path is None:
        logger.error(f"Input path is not set")
        return False

    logger.debug(f"Creating tar file for input_path:"
                 f"{input_path} at: {output_path}")

    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(input_path, arcname=os.path.basename(input_path))

    logger.debug(f"Successfully created compressed file at: {output_path}")
    return True
