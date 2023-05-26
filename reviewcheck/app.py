# Copyright 2023 Volvo Car Corporation
# Licensed under Apache 2.0.

"""Script to show what threads in GitLab you've forgotten to respond to.

You have to configure the script before running it by running
reviewcheck --configure.
"""
import json
import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from shutil import get_terminal_size
from typing import Any, Dict, List, Set

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text

from reviewcheck.cli import Cli
from reviewcheck.config import Config
from reviewcheck.constants import Constants
from reviewcheck.exceptions import RCException
from reviewcheck.merge_request import MergeRequest
from reviewcheck.rich_components import RichGenerator
from reviewcheck.utils import Utils

console = Console()


def configure() -> int:
    """Set up the configuration of reviewcheck.

    :return: Always returns 0.
    """
    Config(True).setup_configuration()
    return 0


def read_viewed_message_ids() -> Set[str]:
    """Read stored comment note IDs from last check.

    :return: The IDs of those comments that were considered in need of a
        reply on the last run of reviewcheck.
    """
    old_comment_note_ids: Set[str] = set()
    try:
        with open(Constants.COMMENT_NOTE_IDS_PATH) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return old_comment_note_ids

    for line in lines:
        old_comment_note_ids.add(line.strip())

    return old_comment_note_ids


def write_viewed_message_ids(new_comment_note_ids: Set[str]) -> None:
    """Write all the comment note IDs from the last run to file.

    :param new_comment_note_ids: The IDs of the comments that are
        considered in need of a reply during this run of reviewcheck.
    """
    with open(Constants.COMMENT_NOTE_IDS_PATH, "w") as f:
        for id in new_comment_note_ids:
            f.write(f"{id}\n")


def show_reviews(config: Dict[str, Any], suppress_notifications: bool) -> None:
    """Download MR data and present review info for each relevant MR.

    :param config: The resolved configuration of reviewcheck.
    """
    secret_token = config["secret_token"]
    api_url = config["api_url"]
    jira_url = config["jira_url"]
    project_ids = config["project_ids"]
    user = config["user"]
    ignored_mrs = config["ignored_mrs"]
    show_all_discussions = config["show_all_discussions"]
    hide_all_threads_user_already_replied_to = config["hide_replied_discussions"]

    mr_pages = []
    with Progress(transient=True, expand=True) as progress:
        gitlab_download_task = progress.add_task(
            "[green]Downloading MR data...",
            start=False,
        )
        for project in project_ids:
            api_url_project = f"{api_url}/projects/{project}"
            merge_requests_data = json.loads(
                requests.get(
                    f"{api_url_project}/merge_requests?state=opened&per_page=500",
                    headers={"PRIVATE-TOKEN": secret_token},
                ).content
            )
            if isinstance(merge_requests_data, dict):
                raise Exception("Malformed data received from GitLab")
            else:
                mr_pages += [
                    mr
                    for mr in merge_requests_data
                    if str(mr["iid"]) not in ignored_mrs
                ]

        mrs: List[MergeRequest] = []

        def reaction_url(project: str, id: str) -> str:
            """Construct API URL for merge request reactions."""
            return f"{api_url}/projects/{project}/merge_requests/{id}/award_emoji"

        def mr_url(project: str, id: str) -> str:
            """Construct API URL for merge request notes."""
            return (
                f"{api_url}/projects/{project}/merge_requests/{id}"
                "/discussions?per_page=500"
            )

        with ThreadPoolExecutor(max_workers=Constants.THREADPOOL_MAXSIZE) as executor:
            progress.start_task(gitlab_download_task)
            progress.update(gitlab_download_task, total=len(mrs))

            for mr_response, reaction_response, mr in executor.map(
                Utils.download_data,
                [
                    (
                        secret_token,
                        mr_url(mr["project_id"], mr["iid"]),
                        reaction_url(mr["project_id"], mr["iid"]),
                        mr,
                    )
                    for mr in mr_pages
                ],
            ):
                mrs.append(
                    MergeRequest(
                        mr_response,
                        reaction_response,
                        mr,
                        user,
                    )
                )
                progress.update(gitlab_download_task, advance=1)

    console.print(
        Panel(
            Text(
                f"Status as of {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                justify="center",
            ),
            style="reverse bold",
        ),
        width=config["output_width"],
    )

    ids_of_seen_messages = read_viewed_message_ids()
    for mr in mrs:
        if (
            mr.user_is_reviewer()
            and mr.number_of_open_threads_needing_user_reply == 0
            and (not show_all_discussions or len(mr.threads) == 0)
        ):
            continue

        main_mr_color = Constants.COLORS[mr.id % len(Constants.COLORS)]
        mr_info_header = Panel(
            Text(RichGenerator.info_box_content(mr, jira_url)),
            title=RichGenerator.info_box_title(mr, main_mr_color),
            width=config["output_width"],
        )

        console.print(mr_info_header)
        if (
            mr.user_reacted_but_no_upvote()
            and not mr.is_author
            and mr.number_of_open_threads_needing_user_reply == 0
        ):
            continue

        for thread in mr.threads:
            last_message = thread["notes"][-1]

            # When minimal view is requsted, only show threads where
            # a response is required.
            if hide_all_threads_user_already_replied_to:
                if last_message["author"]["username"] == user:
                    continue

            user_needs_to_reply = False
            if last_message["author"]["username"] != user:
                user_needs_to_reply = True

                if (
                    not suppress_notifications
                    and str(last_message["id"]) not in ids_of_seen_messages
                ):
                    subprocess.run(
                        [
                            "notify-send",
                            "--expire-time=15000",
                            f"New comment on MR !{mr.id}",
                            (
                                f"{last_message['author']['name']} writes:\n\n"
                                f"{last_message['body']}"
                            ),
                        ]
                    )

            border_color = f"{main_mr_color}" if user_needs_to_reply else "white"
            row_highlighting_style = RichGenerator.rows_highlighting(
                thread,
                user_needs_to_reply,
                user,
            )
            thread_table = RichGenerator.thread_table(
                row_styles=row_highlighting_style,
                border_color=border_color,
                main_color=main_mr_color,
                width=config["output_width"],
            )
            for message in thread["notes"]:
                update_time = Utils.convert_time(message["updated_at"])
                thread_table.add_row(
                    update_time,
                    message["author"]["name"],
                    message["body"],
                )

            if user_needs_to_reply or show_all_discussions:
                thread_table.add_row(
                    "",
                    "Discussion link",
                    f"{mr.web_url}#note_{thread['notes'][0]['id']}",
                )

            console.print(thread_table)

    write_viewed_message_ids(set([id for mr in mrs for id in mr.all_last_message_ids]))


def run() -> int:
    """Start execution of reviewcheck."""
    args = Cli.parse_arguments()

    if args.print_version:
        from reviewcheck import __version__

        print(__version__)
        return 0

    command_palette = {
        "configure": configure,
    }

    if args.command:
        func = command_palette.get(args.command)

        if func is not None:
            return func()
        else:
            print(
                f"'{args.command} is not a valid command, please see "
                "`reviewcheck --help`."
            )
            return 127

    Constants.DATA_DIR.mkdir(exist_ok=True)

    config = Config(False).get_configuration()

    if config is None:
        print(f"Could not read configuration from {str(Constants.CONFIG_PATH)}.")
        return 1

    if args.user:
        config["user"] = args.user
    config["user"] = config["user"].upper()

    if args.output_width:
        config["output_width"] = args.output_width
    else:
        config.setdefault("output_width", get_terminal_size().columns)

    if "ignored_mrs" not in config:
        config["ignored_mrs"] = args.ignore

    if "show_all_discussions" not in config:
        config["show_all_discussions"] = args.all

    if "hide_replied_discussions" not in config:
        config["hide_replied_discussions"] = args.minimal

    try:
        if args.refresh_time is None:
            show_reviews(config, args.no_notifications)
            return 0

        while True:
            console.clear()
            show_reviews(config, args.no_notifications)
            time.sleep(args.refresh_time * 60)
    except KeyboardInterrupt:
        print("\nBye bye!")
        return 0
    except RCException as e:
        logging.error(f"Reviewcheck encountered a problem: {e}")
        return 1
