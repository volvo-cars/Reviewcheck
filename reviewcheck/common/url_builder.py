import datetime
from typing import Optional


class UrlBuilder:
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
        fast_mode: bool = False,
    ) -> str:
        url = f"{api_url}/projects/{project}/merge_requests?state=opened&per_page=500"
        if fast_mode:
            url += "&sort=asc" + UrlBuilder._get_created_after_utm_parameter(3)

        return url

    @staticmethod
    def construct_download_all_merge_requests_url(
        api_url: str,
        project: int,
        id: int,
    ) -> str:
        url = (
            f"{api_url}/projects/{project}"
            f"/merge_requests/{id}/discussions?per_page=500"
        )
        return url

    @staticmethod
    def construct_jira_link(jira_url: str, ticket_number: Optional[str]) -> str:
        if ticket_number:
            return f"{jira_url}/{ticket_number}"
        return "No JIRA reference found"
