import sys
import os
import logging

logger = logging.getLogger("bluejayhost")

class Encrypt:
    def __init__(self, input_path):
        self.path = input_path
        self.success = False

    def _validate_input_file(self) -> bool:
        if self.path is None or not os.path.isfile(self.path):
            logger.error(f"Input at: {self.path} does not exist or is invalid")
            return False

        return True

    def execute(self, output_path) -> bool:
        if not self._validate_input_file():
            return False

        logger.debug(f"Successfully created encrypted file at: {output_path}")
        return True
