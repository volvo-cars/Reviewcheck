"""Tests for the merge_requests.py file."""
from typing import Any, Dict, List

from reviewcheck.merge_request import MergeRequest

sample_mr: Dict[str, Any] = {
    "approvals_before_merge": None,
    "assignee": None,
    "assignees": [],
    "author": {
        "avatar_url": "https://example.com/avatar.jpg",
        "id": 5909,
        "name": "John Doe",
        "state": "active",
        "username": "johndoe",
        "web_url": "https://gitlab.com/johndoe",
    },
    "blocking_discussions_resolved": False,
    "closed_at": None,
    "closed_by": None,
    "created_at": "2022-01-01T00:00:00.000+02:00",
    "description": (
        "Change functions that do not have to create an object of the class\n"
        "to static methods.\n"
        "\n"
        "JIRA: [ARTXXX-1000](https://jira.example.com/browse/ARTXXX-1000)"
    ),
    "detailed_merge_status": "discussions_not_resolved",
    "discussion_locked": None,
    "downvotes": 0,
    "draft": False,
    "force_remove_source_branch": True,
    "has_conflicts": False,
    "id": 40000,
    "iid": 300,
    "labels": [],
    "merge_commit_sha": None,
    "merge_status": "cannot_be_merged_recheck",
    "merge_user": None,
    "merge_when_pipeline_succeeds": False,
    "merged_at": None,
    "merged_by": None,
    "milestone": None,
    "prepared_at": "2022-01-01T00:00:00.000+02:00",
    "project_id": 500,
    "reference": "!300",
    "references": {"full": "repo!300", "relative": "!300", "short": "!300"},
    "reviewers": [],
    "sha": "1111111111111111aaaaaaaaaaaaaaaaaaaaaaaa",
    "should_remove_source_branch": None,
    "source_branch": "the-source-branch",
    "source_project_id": 500,
    "squash": False,
    "squash_commit_sha": None,
    "squash_on_merge": False,
    "state": "opened",
    "target_branch": "dev",
    "target_project_id": 500,
    "task_completion_status": {"completed_count": 0, "count": 0},
    "time_stats": {
        "human_time_estimate": None,
        "human_total_time_spent": None,
        "time_estimate": 0,
        "total_time_spent": 0,
    },
    "title": "Change methods to static",
    "updated_at": "2022-01-01T00:00:00.000+02:00",
    "upvotes": 2,
    "user_notes_count": 32,
    "web_url": "https://gitlab.com/repo/-/merge_requests/300",
    "work_in_progress": False,
}


sample_mr_response: List[Dict[str, Any]] = [
    {
        "id": "abcdef1234567890",
        "individual_note": True,
        "notes": [
            {
                "attachment": None,
                "author": {
                    "avatar_url": (
                        "https://gitlab.com/uploads/-/system/user/avatar/"
                        "0000/avatar.png"
                    ),
                    "id": 0000,
                    "name": "Doe, John",
                    "state": "active",
                    "username": "johndoe",
                    "web_url": "https://gitlab.com/johndoe",
                },
                "body": "there is a bug",
                "commands_changes": {},
                "confidential": False,
                "created_at": "2022-12-14T19:00:00.000+01:00",
                "id": 100000,
                "internal": False,
                "noteable_id": 20000,
                "noteable_iid": 15,
                "noteable_type": "MergeRequest",
                "project_id": 500,
                "resolvable": False,
                "system": True,
                "type": None,
                "updated_at": "2022-12-14T20:00:00.000+01:00",
            }
        ],
    }
]


def test_extract_jira() -> None:
    """Test extracting JIRA ticket from MR description."""
    mr = MergeRequest(sample_mr_response, [], sample_mr, "janedoe")
    assert mr.extract_jira() == "ARTXXX-1000"


def test_extract_jira_lines_after_jira() -> None:
    """Test extracting JIRA ticket from MR description with lines after.

    Test that even if there are other lines after the line in the
    description containing the jiRA ticket, the ticket is still found.
    This also tests that JIRA tickets without a link are found.
    """
    merge_request_1 = MergeRequest(sample_mr_response, [], sample_mr, "janedoe")
    merge_request_1.description = """This is a commit heading

This is a commit body.

JIRA: ABCD-1234

Other text
"""
    assert merge_request_1.extract_jira() == "ABCD-1234"
