import sys
import os
import logging

logger = logging.getLogger("bluejayhost")

class GitRepo:
    def __init__(self, input_path):
        self.path = input_path

    def get_head(self):
        if self.path is None:
            logger.error(f"Repo path is not set")
            return None

        return f"HEAD"
