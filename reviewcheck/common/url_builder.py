"""File with functions for constructing URLs."""
import datetime
from typing import Optional


class UrlBuilder:
    """Class with functions for constructing URLs."""

    @staticmethod
    def _get_created_after_utm_parameter(weeks: int = 3) -> str:
        three_weeks_ago = (
            datetime.datetime.now() - datetime.timedelta(weeks=weeks)
        ).isoformat()[:-7] + "Z"
        fast_mode_utm_param = f"&created_after={three_weeks_ago}"
        return fast_mode_utm_param

    @staticmethod
    def construct_project_mr_list_url(
        api_url: str,
        project: int,
    ) -> str:
        """Make GitLab API URL for all merge request in a project.

        :param api_url: Base URL for the GitLab API of the user's GitLab
            instance.
        :param project: The project ID of the project to look for merge
            requests in.

        :return: The constructed URL.
        """
        url = f"{api_url}/projects/{project}/merge_requests?state=opened&per_page=500"

        return url

    @staticmethod
    def construct_download_all_merge_requests_url(
        api_url: str,
        project: int,
        id: int,
    ) -> str:
        """Construct URL for dowloading data for an MR from GitLab.

        :param api_url: Base URL for the GitLab API of the user's GitLab
            instance.
        :param project: The project ID of the project to look for merge
            requests in.
        :id: The ID of the merge request to get data for.

        :return: The constructed URL.
        """
        url = (
            f"{api_url}/projects/{project}"
            f"/merge_requests/{id}/discussions?per_page=500"
        )
        return url

    @staticmethod
    def construct_jira_link(jira_url: str, ticket_number: Optional[str]) -> str:
        """Construct link to JIRA for ticket found in MR description.

        :param jira_url: Base URL for the user's JIRA instance.
        :param ticket_number: The JIRA ticket number.
        """
        if ticket_number:
            return f"{jira_url}/{ticket_number}"
        return "No JIRA reference found"
