# integrations/github/sync_placeholder.py
#
# Placeholder for future GitHub repository sync functionality.
#
# STATUS: CONCEPT ONLY — Nothing here is implemented or needed yet.
#
# This module represents a future capability for syncing project configuration,
# model metadata, and prompt templates with a remote git repository.
#
# Why this might be useful eventually:
#   - Two developers working on the same project can share model configs
#   - Prompt template improvements can be version-controlled
#   - Model performance notes can be tracked in git history
#   - The project's own development can be synced across machines
#
# What this is NOT:
#   - A cloud backup system
#   - A model file sync (models are too large for git)
#   - A deployment pipeline
#   - Anything that requires a GitHub API token to use
#
# TODO (Phase 5.5 — low priority):
#   - Define exactly which files should be synced (configs, templates, notes)
#   - Decide whether to use raw git commands via subprocess or a git library
#   - Implement push_config_snapshot()
#   - Implement pull_latest_configs()
#   - Document sync workflow in SETUP_TEMPLATE.md


class SyncError(Exception):
    """Raised when a sync operation fails."""
    pass


def push_config_snapshot(
    remote_url: str,
    branch: str = "main",
    commit_message: str = "Update model configs",
) -> bool:
    """
    Push current config state to a remote git repository.

    Arguments:
        remote_url     (str) — The git remote URL to push to
        branch         (str) — Target branch name
        commit_message (str) — Git commit message

    Files that WOULD be included in the snapshot:
        - config/model.config.json
        - config/model_registry.json
        - model_runtime/prompt_formatter.py (template definitions)
        - AGENT_MODEL.md

    Files that MUST NOT be included:
        - models/*.gguf  (too large, gitignored)
        - Any file containing secrets or personal data

    TODO (Phase 5.5):
        import subprocess
        subprocess.run(["git", "add", "config/", "AGENT_MODEL.md"], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", remote_url, branch], check=True)
        return True
    """
    raise NotImplementedError(
        "push_config_snapshot() is a future feature. See TODO.md Phase 5.5."
    )


def pull_latest_configs(
    remote_url: str,
    branch: str = "main",
) -> bool:
    """
    Pull latest config changes from a remote git repository.

    WARNING: This will overwrite local config files with remote versions.
    Local changes not committed will be lost.

    TODO (Phase 5.5):
        import subprocess
        subprocess.run(["git", "fetch", remote_url, branch], check=True)
        subprocess.run(["git", "merge", f"origin/{branch}"], check=True)
        return True
    """
    raise NotImplementedError(
        "pull_latest_configs() is a future feature. See TODO.md Phase 5.5."
    )


def check_sync_status() -> dict:
    """
    Check whether local state is in sync with the remote.

    Returns:
        dict — {
            "local_ahead": int,    # commits ahead of remote
            "local_behind": int,   # commits behind remote
            "has_uncommitted": bool,
            "last_sync": str | None,
        }

    TODO (Phase 5.5): Implement using git log and git status parsing.
    """
    # Placeholder result
    return {
        "local_ahead": 0,
        "local_behind": 0,
        "has_uncommitted": False,
        "last_sync": None,
        "note": "Sync status checking not yet implemented.",
    }
