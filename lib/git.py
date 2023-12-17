import sys
import os
import logging
from typing import Optional
from git import Repo

class GitRepo:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.repo = Repo(repo_path)

    def get_head(self) -> Optional[str]:
        return self.repo.head.object.hexsha
