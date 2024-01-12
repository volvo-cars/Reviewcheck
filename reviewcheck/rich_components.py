# Copyright 2023 Volvo Car Corporation
# Licensed under Apache 2.0.

"""Functions for generating components with the rich module."""
from typing import Any, Dict, List, Optional

from rich import box
from rich.table import Table

from reviewcheck.constants import Constants
from reviewcheck.merge_request import MergeRequest
from reviewcheck.utils import Utils


class RichGenerator:
    """Static functions for generatign rich text components."""

    @staticmethod
    def thread_table(
        row_styles: List[str],
        border_color: str,
        main_color: str,
        width: int,
    ) -> Table:
        """Get an empty threads table to populate with messages."""
        table = Table(
            show_header=True,
            show_lines=True,
            row_styles=row_styles,
            border_style=border_color,
            header_style=f"bold {main_color}",
            width=width,
            box=box.ROUNDED,
        )

        table.add_column("Date", width=Constants.TUI_DATE_WIDTH)
        table.add_column("Author", width=Constants.TUI_AUTHOR_WIDTH)
        table.add_column(
            "Message",
            style="dim",
            min_width=width
            - Constants.TUI_AUTHOR_WIDTH
            - Constants.TUI_DATE_WIDTH
            - Constants.TUI_THREE_COL_PADDING_WIDTH,
        )
        return table

    @staticmethod
    def rows_highlighting(
        comment: Dict[str, Any],
        needs_reply: bool,
        username: str,
    ) -> List[str]:
        """Return highligh configuration for each note in a thread.

        Messages after the user's own last message should be
        highlighted. This marks them as "new". It is assumed that all
        messages that have been added after the user's own last message
        is new to the user.

        :param comment: The thread to provide highlighting for.
        :param needs_reply: Whether there are new messages after the
            user's last message.
        :param username: Username of the user who needs to reply.

        :return: List of highlighting information to be given to the
            rich library function for highlighting the given thread.
        """
        n_replies = len(comment["notes"])
        notes = comment["notes"]
        author_list = [n["author"]["username"] for n in notes]
        if not needs_reply:
            return [""] * (n_replies)
        elif username not in author_list:
            return ["bold white not dim"] * (n_replies)
        i_my_last_reply = n_replies - author_list[::-1].index(username)
        return [""] * (i_my_last_reply) + ["bold white not dim"] * (
            n_replies - i_my_last_reply
        )

    @staticmethod
    def info_box_title(
        mr: MergeRequest,
        color: str,
    ) -> str:
        """Return the info box title with rich text configuration.

        :param mr: Data about the mr to construct title for.
        :param jira_ticket_number: The JIRA ticket number associated
            with the MR.
        :param color: Color to use for the title when printing.

        :return: The formatted title to use for the info box.
        """
        title_elements = [
            f"[bold {color}]{mr.title}",
            f"!{mr.id}",
        ]

        if mr.jira_ticket_number:
            title_elements.append(mr.jira_ticket_number)

        return " | ".join(title_elements)

    @staticmethod
    def info_box_content(
        mr: MergeRequest,
        jira_base_url: Optional[str],
    ) -> str:
        """Return the content of the info box for an merge request.

        :param mr: Data for the merge request in question.
        :param jira_url: URL to JIRA ticket associated with the merge
            request, or replacement text.
        :param jira: JIRA ticket number.
            the user is involved.
        :param n_response_required: Number of threads on the merge
            request where the user is involved and hasn't replied to a
            message.

        :return: The text to put in the info box for the given merge
            request.
        """
        info = f"Upvotes: {mr.upvotes}"
        if mr.upvotes > 0:
            info += f"\nPeople who have upvoted: {mr.print_upvoters()}"
        reactors = mr.print_reactors()
        if reactors:
            info += f"\nPeople who have reacted: {reactors}"
        info += f"\nOpen discussions: {mr.number_of_open_threads}"
        if mr.number_of_open_threads:
            info += (
                f"\nOpen discussions where you are involved: "
                f"{mr.number_of_open_threads_for_user}"
            )
            info += "\nOpen discussions you need to respond (colored border): "
            info += f"{mr.number_of_open_threads_needing_user_reply}"
        info += f"\n\nGitLab link:   {mr.web_url}"
        if jira_base_url:
            info += f"\nJira link:     {mr.jira_link(jira_base_url)}"
        info += f"\nSource branch: {mr.source_branch}"
        info += f"\nCreated at:    {Utils.convert_time(mr.creation_time)}"
        info += f"\n\n{mr.description}"
        return info
