"""
services/github_service.py — GitHub storage backend using PyGitHub.

All run artifacts (Excel, HTML, metadata) and configuration (vendors, index)
are stored as files in a dedicated GitHub repository branch.
"""

import base64
import json
import logging
import os
from typing import Any

from github import Github, GithubException, UnknownObjectException

logger = logging.getLogger(__name__)


class GitHubService:
    """Thin wrapper around PyGitHub for reading and writing structured data."""

    def __init__(self) -> None:
        token = os.getenv("GITHUB_TOKEN", "")
        repo_name = os.getenv("GITHUB_REPO", "")
        self.branch = os.getenv("GITHUB_BRANCH", "outputs")

        if not token or not repo_name:
            raise RuntimeError(
                "GITHUB_TOKEN and GITHUB_REPO environment variables must be set."
            )

        g = Github(token)
        self.repo = g.get_repo(repo_name)

    # ------------------------------------------------------------------
    # Raw file I/O
    # ------------------------------------------------------------------

    def read_file(self, path: str) -> bytes:
        """Return raw bytes for a file at *path* on the configured branch."""
        content = self.repo.get_contents(path, ref=self.branch)
        # get_contents returns a list when *path* is a directory
        if isinstance(content, list):
            raise IsADirectoryError(f"{path} is a directory, not a file")
        return base64.b64decode(content.content)

    def write_file(self, path: str, content: bytes, commit_message: str) -> None:
        """Create or update *path* with *content*, making a single commit."""
        try:
            existing = self.repo.get_contents(path, ref=self.branch)
            if isinstance(existing, list):
                raise IsADirectoryError(f"{path} is a directory")
            self.repo.update_file(
                path, commit_message, content, existing.sha, branch=self.branch
            )
            logger.debug("Updated %s on branch %s", path, self.branch)
        except UnknownObjectException:
            self.repo.create_file(
                path, commit_message, content, branch=self.branch
            )
            logger.debug("Created %s on branch %s", path, self.branch)

    def list_files(self, prefix: str) -> list[str]:
        """Return all file paths that live under *prefix* (recursive)."""
        try:
            queue = list(self.repo.get_contents(prefix, ref=self.branch))
        except UnknownObjectException:
            return []

        result: list[str] = []
        while queue:
            item = queue.pop(0)
            if item.type == "dir":
                try:
                    queue.extend(self.repo.get_contents(item.path, ref=self.branch))
                except UnknownObjectException:
                    pass
            else:
                result.append(item.path)
        return result

    def file_exists(self, path: str) -> bool:
        """Return True if *path* exists on the configured branch."""
        try:
            self.repo.get_contents(path, ref=self.branch)
            return True
        except (UnknownObjectException, GithubException):
            return False

    def get_file_download_url(self, path: str) -> str:
        """Return the raw GitHub download URL for *path*."""
        content = self.repo.get_contents(path, ref=self.branch)
        if isinstance(content, list):
            raise IsADirectoryError(f"{path} is a directory")
        return content.download_url

    # ------------------------------------------------------------------
    # JSON helpers
    # ------------------------------------------------------------------

    def read_json(self, path: str) -> dict:
        """Read and parse a JSON file; returns {} if the file does not exist."""
        try:
            raw = self.read_file(path)
            return json.loads(raw.decode("utf-8"))
        except (UnknownObjectException, GithubException):
            return {}
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from %s", path)
            return {}

    def write_json(self, path: str, data: Any, commit_message: str) -> None:
        """Serialise *data* to JSON and write it to *path*."""
        raw = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.write_file(path, raw, commit_message)

    # ------------------------------------------------------------------
    # Run index  (outputs/index.json)
    # ------------------------------------------------------------------

    def get_run_index(self) -> list[dict]:
        """Return the list of RunSummary dicts from outputs/index.json."""
        data = self.read_json("outputs/index.json")
        return data.get("runs", []) if isinstance(data, dict) else []

    def append_run_to_index(self, run_summary: dict) -> None:
        """Append *run_summary* to outputs/index.json atomically."""
        data = self.read_json("outputs/index.json")
        if not isinstance(data, dict):
            data = {}
        runs: list = data.get("runs", [])
        runs.append(run_summary)
        data["runs"] = runs
        self.write_json(
            "outputs/index.json",
            data,
            f"index: add run {run_summary.get('run_id', 'unknown')}",
        )

    # ------------------------------------------------------------------
    # Vendors  (outputs/vendors.json)
    # ------------------------------------------------------------------

    def get_vendors(self) -> dict:
        """Return the vendors dict from outputs/vendors.json."""
        data = self.read_json("outputs/vendors.json")
        if not isinstance(data, dict) or "vendors" not in data:
            return {"vendors": []}
        return data

    def save_vendors(self, data: dict) -> None:
        """Persist the vendors dict to outputs/vendors.json."""
        self.write_json("outputs/vendors.json", data, "vendors: update registry")
