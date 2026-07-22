# integrations/github/repo_metadata.py
#
# Tracks version metadata for the project and its model configurations.
#
# STATUS: CONCEPT ONLY — Placeholder data structures only.
#
# This module provides a structured way to record:
#   - Which version of the project is running
#   - When configurations were last changed
#   - Which models have been tested at which project versions
#   - Notes about compatibility between project versions and model versions
#
# This is useful for long-term projects where both the codebase and the
# model files may change independently over time.
#
# TODO (Phase 5.5):
#   - Implement read_project_version()
#   - Implement record_model_test()
#   - Implement get_compatibility_notes()

from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Project version — update this manually with each significant milestone
# ---------------------------------------------------------------------------
PROJECT_VERSION = "0.0.1"
PROJECT_PHASE = "Phase 0 — Scaffold"


def get_project_metadata() -> dict:
    """
    Return basic metadata about the current project state.

    This is a static snapshot — it does not read from git or any external source.
    Update the constants at the top of this file as the project progresses.
    """
    return {
        "version": PROJECT_VERSION,
        "phase": PROJECT_PHASE,
        "description": "Initial scaffold — no working inference yet.",
        "schema_version": 1,
    }


def record_model_test(
    model_filename: str,
    project_version: str,
    chat_template_used: str,
    result: str,
    notes: str = "",
) -> dict:
    """
    Record the result of testing a model at a specific project version.

    Arguments:
        model_filename    (str) — The .gguf filename tested
        project_version   (str) — Project version at time of test
        chat_template_used (str) — Which template was used
        result            (str) — "pass", "fail", "partial"
        notes             (str) — Freeform notes

    Returns:
        dict — The test record (to be persisted by caller)

    TODO (Phase 5.5):
        Persist these records to config/test_log.json
    """
    return {
        "model_filename": model_filename,
        "project_version": project_version,
        "chat_template_used": chat_template_used,
        "result": result,
        "notes": notes,
        "tested_at": datetime.now(timezone.utc).isoformat(),
    }


def get_version_changelog() -> list:
    """
    Return a structured list of project version milestones.

    This is maintained manually — add an entry each time a significant
    phase is completed.

    TODO: Move this to a separate CHANGELOG.md once Phase 1 is complete.
    """
    return [
        {
            "version": "0.0.1",
            "date": "2025",
            "phase": "Phase 0",
            "summary": "Initial scaffold created. Directory structure, "
                       "documentation, and stub modules established. "
                       "No working inference.",
            "breaking_changes": [],
        },
        # Add entries here as work progresses:
        # {
        #     "version": "0.1.0",
        #     "date": "[TBD]",
        #     "phase": "Phase 1",
        #     "summary": "Backend routes working. /status returns real data.",
        #     "breaking_changes": [],
        # },
    ]
