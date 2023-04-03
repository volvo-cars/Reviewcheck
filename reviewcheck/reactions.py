"""Holds class for storing merge request reactions."""

from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional


class Reactions:
    """Hold reactions on MR and analyze."""

    def __init__(self, raw: List[Dict[str, Any]]):
        """Parse the reaction data and store."""
        self.reaction_name: DefaultDict[str, List[str]] = defaultdict(list)
        self.reaction_user: DefaultDict[str, List[str]] = defaultdict(list)
        for reaction in raw:
            self.reaction_name[reaction["name"]].append(reaction["user"]["name"])
            self.reaction_user[reaction["name"]].append(reaction["user"]["username"])

    def __str__(self) -> str:
        """How this object is printed."""
        return "\n".join([f"{r}: {u}" for r, u in self.reaction_name.items()])

    def print_reactors(self) -> Optional[str]:
        """:return: Printable list of people who have reacted."""
        all_reactors: List[str] = list(
            set(
                person
                for reaction in self.reaction_name.values()
                for person in reaction
            )
        )
        all_reactors.sort()
        return " | ".join(all_reactors)

    def print_upvoters(self) -> Optional[str]:
        """:return: Printable list of people who have upvoted."""
        all_upvoters = self.reaction_name.get("thumbsup", [])
        all_upvoters.sort()
        return " | ".join(all_upvoters)

    def react_but_no_upvote(self, user: str) -> bool:
        """Return True if user has left a reaction without upvoting.

        :user: The user name of the user we are checking reviews for.
        :return: True if the user forgot to thumb up, otherwise False.
        """
        has_reacted = any(user in reaction for reaction in self.reaction_user.values())
        has_upvoted = user in self.reaction_user.get("thumbsup", [])
        if has_reacted and not has_upvoted:
            return True
        return False
