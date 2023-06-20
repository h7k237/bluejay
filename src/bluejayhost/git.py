import sys
import os
import logging

logger = logging.getLogger("bluejayhost")

def get_git_head(repo_path):
    """Get the HEAD commit from a git repo"""
    if repo_path is None:
        logger.error(f"Input repo path is not set")
        return None

    return f"HEAD"
