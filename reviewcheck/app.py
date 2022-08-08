"""
A script to show you what threads in GitLab you've forgotten to respond to.

You have to configure the script before running it by running reviewcheck --configure
"""
import json
import logging
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from shutil import get_terminal_size
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from reviewcheck.cli import Cli
from reviewcheck.common.constants import Constants
from reviewcheck.common.exceptions import RCException
from reviewcheck.common.url_builder import UrlBuilder
from reviewcheck.config import Config
from reviewcheck.utils import Utils

console = Console()
THREAD_POOL = 32


def download_gitlab_data(
    get_data: Tuple[str, int, str],
) -> Tuple[List[Dict[str, Any]], int]:
    # This is how to create a reusable connection pool with python requests.
    with requests.Session() as session:
        session.mount(
            "https://",
            requests.adapters.HTTPAdapter(
                pool_maxsize=THREAD_POOL, max_retries=3, pool_block=True
            ),
        )
        url, mr_id, secret_token = get_data
        response = session.get(url, headers={"PRIVATE-TOKEN": secret_token})
        response_json = json.loads(response.content)
        logging.info(
            "request was completed in %s seconds [%s]",
            response.elapsed.total_seconds(),
            response.url,
        )
        if response.status_code != 200:
            logging.error(
                "request failed, error code %s [%s]", response.status_code, response.url
            )
        if 500 <= response.status_code < 600:
            # server is overloaded? give it a break
            time.sleep(5)

        num_pages = int(response.headers["X-Total-Pages"])
        for page in range(2, num_pages + 1):
            response = session.get(
                f"{url}&page={page}", headers={"PRIVATE-TOKEN": secret_token}
            )
            response_json += json.loads(response.content)
            logging.info(
                "request was completed in %s seconds [%s]",
                response.elapsed.total_seconds(),
                response.url,
            )
            if response.status_code != 200:
                logging.error(
                    "request failed, error code %s [%s]",
                    response.status_code,
                    response.url,
                )
            if 500 <= response.status_code < 600:
                # server is overloaded? give it a break
                time.sleep(5)

    if isinstance(response_json, list):
        if len(response_json) == 0 or isinstance(response_json[0], dict):
            return response_json, mr_id

    raise Exception("Malformed data returned from GitLab.")


def is_user_referenced_in_thread(
    notes: List[Dict[str, Any]],
    username: str,
) -> bool:
    for note in notes:
        if ("@" + username) in note["body"]:
            return True
    return False


def is_user_author_of_thread(
    mr: Dict[str, Any],
    notes: List[Dict[str, Any]],
    username: str,
) -> bool:
    if mr["author"] == username:
        if notes[-1]["author"]["username"] != username:
            return True
    return False


def is_user_participating_in_thread(
    notes: List[Dict[str, Any]],
    username: str,
) -> bool:
    for note in notes:
        if note["author"]["username"] == username:
            return True
    return False


def get_rows_highlighting(
    comment: Dict[str, Any],
    needs_reply: bool,
    username: str,
) -> List[str]:
    """Messages after your own last message should be highlighted"""
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


def configure() -> int:
    Config(True).setup_configuration()
    return 0


def get_info_box_title(
    mr: Dict[str, Any],
    jira_ticket_number: Optional[str],
    color: str,
) -> str:
    return (
        f"[bold {color}]{mr['mr_data']['title']} | "
        f"!{mr['mr_data']['iid']} | {jira_ticket_number}"
    )


def get_info_box_content(
    mr: Dict[str, Any],
    jira_url: str,
    jira: Optional[str],
    n_all_notes: int,
    n_your_notes: int,
    n_response_required: int,
) -> str:
    return (
        f"Open discussions: {n_all_notes}"
        f"\nOpen discussions where you are involved: {n_your_notes}"
        "\nOpen discussions you need to respond (colored border): "
        f"{n_response_required}"
        f"\n\nGitLab link:   {mr['mr_data']['web_url']}"
        f"\nJira link:     {UrlBuilder.construct_jira_link(jira_url, jira)}"
        f"\nSource branch: {mr['mr_data']['source_branch']}"
        f"\nCreated at:    {Utils.convert_time(mr['mr_data']['created_at'])}"
        f"\n\n{mr['mr_data']['description']}"
    )


def read_comment_note_ids_from_file() -> Set[str]:
    """Read stored comment note IDs from last check."""
    old_comment_note_ids: Set[str] = set()
    try:
        with open(Constants.COMMENT_NOTE_IDS_PATH) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return old_comment_note_ids

    for line in lines:
        old_comment_note_ids.add(line.strip())

    return old_comment_note_ids


def write_comment_note_ids_to_file(new_comment_note_ids: Set[str]) -> None:
    """Write all the comment note IDs from the last run to file"""
    with open(Constants.COMMENT_NOTE_IDS_PATH, "w") as f:
        for id in new_comment_note_ids:
            f.write(f"{id}\n")


def show_reviews(config: Dict[str, Any]) -> None:
    secret_token = config["secret_token"]
    api_url = config["api_url"]
    jira_url = config["jira_url"]
    project_ids = config["project_ids"]
    user = config["user"]
    ignored_mrs = config["ignored_mrs"]
    show_all_discussions = config["show_all_discussions"]
    hide_replied_discussions = config["hide_replied_discussions"]

    mr_pages = []
    with Progress(transient=True, expand=True) as progress:
        gitlab_download_task = progress.add_task(
            "[green]Downloading MR data...",
            start=False,
        )
        for project in project_ids:
            merge_requests_data = json.loads(
                requests.get(
                    UrlBuilder.construct_project_mr_list_url(
                        api_url,
                        project,
                    ),
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

        mrs = {
            mr["iid"]: {
                "mr_data": mr,
                "project": mr["project_id"],
                "author": mr["author"]["username"],
            }
            for mr in mr_pages
        }
        for id, mr in mrs.items():
            mrs[id]["url"] = UrlBuilder.construct_download_all_merge_requests_url(
                api_url,
                mr["project"],
                id,
            )

        with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
            progress.start_task(gitlab_download_task)
            progress.update(gitlab_download_task, total=len(mrs))
            for response_json, mr_id in executor.map(
                download_gitlab_data,
                [(mr["url"], id, secret_token) for id, mr in mrs.items()],
            ):
                mrs[mr_id]["discussion_data"] = response_json
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

    old_comment_note_ids = read_comment_note_ids_from_file()
    new_comment_note_ids: Set[str] = set()
    for id, mr in mrs.items():
        discussion_data = mr["discussion_data"]
        discussion_data = [c for c in discussion_data if "resolved" in c["notes"][0]]
        discussion_data = [c for c in discussion_data if not c["notes"][0]["resolved"]]
        n_all_notes = len(discussion_data)
        discussion_data = [
            c
            for c in discussion_data
            if is_user_participating_in_thread(c["notes"], user)
            or is_user_referenced_in_thread(c["notes"], user)
            or is_user_author_of_thread(mr, c["notes"], user)
        ]
        n_your_notes = len(discussion_data)

        n_response_required = len(
            [
                1
                for comment in discussion_data
                if comment["notes"][-1]["author"]["username"] != user
            ]
        )

        color = Constants.COLORS[id % len(Constants.COLORS)]

        if len(discussion_data) > 0:
            if n_response_required == 0 and not show_all_discussions:
                continue
            console.print()

            # Parse the VIRA ticket number
            jira_regex = re.compile(r".*JIRA: (.*)(\\n)*")
            jira_match = jira_regex.match(mr["mr_data"]["description"].split("\n")[-1])
            jira = None
            if jira_match:
                jira = str(jira_match.group(1))
                already_a_link_regex = re.compile(r"\[(.*)\].*")
                already_a_link = already_a_link_regex.match(jira)
                if already_a_link:
                    jira = str(already_a_link.group(1))

            mr_info_header = Panel(
                Text(
                    get_info_box_content(
                        mr,
                        jira_url,
                        jira,
                        n_all_notes,
                        n_your_notes,
                        n_response_required,
                    )
                ),
                title=get_info_box_title(mr, jira, color),
                width=config["output_width"],
            )
            console.print(mr_info_header)

        for comment in discussion_data:
            # When minimal view is requsted, only show threads where a response is
            # required
            if hide_replied_discussions:
                if comment["notes"][-1]["author"]["username"] == user:
                    continue

            reply_needed = False
            if comment["notes"][-1]["author"]["username"] != user:
                reply_needed = True

                # For notifications
                new_comment_note_id = comment["notes"][-1]["id"]
                new_comment_note_ids.add(new_comment_note_id)
                if str(new_comment_note_id) not in old_comment_note_ids:
                    message = (
                        comment["notes"][-1]["author"]["name"]
                        + ": "
                        + comment["notes"][-1]["body"]
                    )
                    subprocess.run(["notify-send", message])

            border_color = f"{color}" if reply_needed else "white"

            row_highlighting_style = get_rows_highlighting(
                comment,
                reply_needed,
                user,
            )

            threads_table = Table(
                show_header=True,
                show_lines=True,
                row_styles=row_highlighting_style,
                border_style=border_color,
                header_style=f"bold {color}",
                width=config["output_width"],
                box=box.ROUNDED,
            )

            threads_table.add_column("Date", width=Constants.TUI_DATE_WIDTH)
            threads_table.add_column("Author", width=Constants.TUI_AUTHOR_WIDTH)
            threads_table.add_column(
                "Message",
                style="dim",
                min_width=config["output_width"]
                - Constants.TUI_AUTHOR_WIDTH
                - Constants.TUI_DATE_WIDTH
                - Constants.TUI_THREE_COL_PADDING_WIDTH,
            )
            for note in comment["notes"]:
                update_time = Utils.convert_time(note["updated_at"])
                threads_table.add_row(
                    update_time,
                    note["author"]["name"],
                    note["body"],
                )

            if reply_needed:
                threads_table.add_row(
                    "",
                    "Discussion link",
                    f"{mr['mr_data']['web_url']}#note_{comment['notes'][0]['id']}",
                )

            console.print(threads_table)
    write_comment_note_ids_to_file(new_comment_note_ids)


def run() -> int:
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
            show_reviews(config)
            return 0

        while True:
            console.clear()
            show_reviews(config)
            time.sleep(args.refresh_time * 60)
    except KeyboardInterrupt:
        print("\nBye bye!")
        return 0
    except RCException as e:
        logging.error(f"Reviewcheck encountered a problem: {e}")
        return 1
