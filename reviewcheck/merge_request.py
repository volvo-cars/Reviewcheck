# Copyright 2023 Volvo Car Corporation
# Licensed under Apache 2.0.

"""File for storing the MergeRequest class."""
import re
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional

from reviewcheck.exceptions import RCException


class MergeRequest:
    """Class representing a merge request."""

    def __init__(self, threads: Any, reactions: Any, metadata: Any, user: str):
        """Initialize a MergeRequest object."""
        if reactions is None:
            reactions = []
        if (
            not isinstance(threads, list)
            or not isinstance(reactions, list)
            or not isinstance(metadata, dict)
        ):
            raise RCException("Malformed data from GitHub")
        self.title: str = metadata["title"]
        self.mr_author: str = metadata["author"]["username"]
        self.user: str = user
        self.is_author = self.mr_author == self.user
        self.id: int = metadata["iid"]
        self.project: int = metadata["project_id"]
        self.web_url: str = metadata["web_url"]
        self.upvotes: int = metadata["upvotes"]
        self.creation_time: str = metadata["created_at"]
        self.source_branch: str = metadata["source_branch"]
        self.description: str = metadata["description"]
        self.jira_ticket_number = self.extract_jira()

        self.threads: List[Dict[str, Any]] = []
        self.number_of_open_threads = 0
        self.number_of_open_threads_for_user = 0
        self.number_of_open_threads_needing_user_reply = 0
        self.all_last_message_ids: List[str] = []
        for thread in threads:
            messages = thread["notes"]
            first_message = thread["notes"][0]
            last_message = thread["notes"][-1]
            # Filter out comments that are not threads (not resolvable)
            if "resolved" in first_message:
                # ...and only those that are not already resolved
                if not first_message["resolved"]:
                    self.number_of_open_threads += 1
                    # ...and the thread is relevant for the user
                    if (
                        self.user_is_participant(messages)
                        or self.user_is_referenced_in_thread(messages)
                        or self.user_is_author_of_thread(messages)
                    ):
                        self.number_of_open_threads_for_user += 1
                        self.threads.append(thread)
                        self.all_last_message_ids.append(last_message["id"])
                        if last_message["author"]["username"] != self.user:
                            self.number_of_open_threads_needing_user_reply += 1

        self.reaction_and_name: DefaultDict[str, List[str]] = defaultdict(list)
        self.reaction_and_gitlab_user: DefaultDict[str, List[str]] = defaultdict(list)
        for reaction in reactions:
            self.reaction_and_name[reaction["name"]].append(reaction["user"]["name"])
            self.reaction_and_gitlab_user[reaction["name"]].append(
                reaction["user"]["username"]
            )

    def jira_link(self, jira_base_url: str) -> Optional[str]:
        """Getter for JIRA URL."""
        if self.jira_ticket_number:
            return f"{jira_base_url}/{self.jira_ticket_number}"
        return "No JIRA reference found"

    def extract_jira(self) -> Optional[str]:
        """Extract JIRA ticket number from MR description.

        :param description: The description of the MR.
        :return: Jira ticket number if found, otherwise None.
        """
        if self.description is None:
            return None
        # Parse the VIRA ticket number
        jira_regex = re.compile(r".*(?i)JIRA: (.*)(\\n)*")
        jira_match = jira_regex.match(self.description.split("\n")[-1])
        jira = None
        if jira_match:
            jira = str(jira_match.group(1))
            already_a_link_regex = re.compile(r"\[(.*)\].*")
            already_a_link = already_a_link_regex.match(jira)
            if already_a_link:
                jira = str(already_a_link.group(1))
        return jira

    def print_reactors(self) -> Optional[str]:
        """:return: Printable list of people who have reacted."""
        all_reactors: List[str] = list(
            set(
                person
                for reaction in self.reaction_and_name.values()
                for person in reaction
            )
        )
        all_reactors.sort()
        if len(all_reactors) > 0:
            return " | ".join(all_reactors)
        return None

    def print_upvoters(self) -> Optional[str]:
        """:return: Printable list of people who have upvoted."""
        all_upvoters = self.reaction_and_name.get("thumbsup", [])
        all_upvoters.sort()
        return " | ".join(all_upvoters)

    def user_reacted_but_no_upvote(self) -> bool:
        """Return True if user has left a reaction without upvoting.

        :return: True if the user forgot to thumb up, otherwise False.
        """
        has_reacted = any(
            self.user in names for names in self.reaction_and_gitlab_user.values()
        )
        has_upvoted = self.user in self.reaction_and_gitlab_user.get("thumbsup", [])
        if has_reacted and not has_upvoted:
            return True
        return False

    def user_is_reviewer(self) -> bool:
        """Return true if the user is reviewing this MR.

        The user is considered to be reviewing the merge request when
        they have left a reaction on it but not upvoted it, and they
        themself is not the author of the merge request because they
        cannot review their own merge request.
        """
        return not (self.user_reacted_but_no_upvote() and not self.is_author)

    def user_is_referenced_in_thread(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if configured user is mentioned in a given thread.

        :param messages: The thread to check as a list of messages.
        :param username: The username of the configured user.

        :return: True if the user is mentioned in the given thread,
            otherwise false.
        """
        for message in messages:
            if ("@" + self.user) in message["body"]:
                return True
        return False

    def user_is_author_of_thread(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if the given user has responded to thread in its MR.

        Check whether the given user is the author of the current merge
        request, and if so, whether is the last person to respond to the
        given thread.

        :param mr: The merge request to check.
        :param messages: The thread to check.
        :param username: The username to look for as author.

        :return: False if the user doesn't have anything to respond to,
            otherwise True.
        """
        if self.mr_author == self.user:
            if messages[-1]["author"]["username"] != self.user:
                return True
        return False

    def user_is_participant(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if user is active in current thread.

        :param messages: The thread to check whether the user is active
            in.
        :param: The username of the user to check for involvement of.

        :return: True if the user is involved in the current thread,
            otherwise False.
        """
        for message in messages:
            if message["author"]["username"] == self.user:
                return True
        return False
