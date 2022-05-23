"""
A script to show you what threads in GitLab you've forgotten to respond to.

Your configuration file should be in .config/reviewcheckrc and contain the following:

    secret_token: <get a secret token from your settings in gitlab>
    user: <your username>

Dependencies: rich
"""
import datetime
import json
import logging
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from reviewcheck.cli import Cli
from reviewcheck.common.constants import Constants

import requests
import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

console = Console()
THREAD_POOL = 16

# This is how to create a reusable connection pool with python requests.
session = requests.Session()
session.mount(
    "https://",
    requests.adapters.HTTPAdapter(
        pool_maxsize=THREAD_POOL, max_retries=3, pool_block=True
    ),
)


def download_gitlab_data(get_data):
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
                "request failed, error code %s [%s]", response.status_code, response.url
            )
        if 500 <= response.status_code < 600:
            # server is overloaded? give it a break
            time.sleep(5)

    return response_json, mr_id


def is_user_referenced_in_thread(notes, uname):
    for note in notes:
        if ("@" + uname) in note["body"]:
            return True


def is_user_author_of_thread(mr, notes, uname):
    if mr["author"] == uname:
        if notes[-1]["author"]["username"] != uname:
            return True

    return False


def is_user_participating_in_thread(notes, uname):
    for note in notes:
        if note["author"]["username"] == uname:
            return True

    return False


def get_rows_highlighting(comment, needs_reply, uname):
    """Messages after your own last message should be highlighted"""
    n_replies = len(comment["notes"])
    notes = comment["notes"]
    author_list = [n["author"]["username"] for n in notes]
    if not needs_reply:
        return [""] * (n_replies)
    elif uname not in author_list:
        return ["bold white not dim"] * (n_replies)
    i_my_last_reply = n_replies - author_list[::-1].index(uname)
    return [""] * (i_my_last_reply) + ["bold white not dim"] * (
        n_replies - i_my_last_reply
    )


def run() -> int:
    args = Cli.parse_arguments()
    config_path = Path.home() / ".config/reviewcheckrc"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    secret_token = config["secret_token"]
    api_url = config["api_url"]
    jira_url = config["jira_url"]

    user = config["user"]
    if args.user:
        user = args.user
    user = user.upper()

    three_weeks_ago = (datetime.datetime.now() - datetime.timedelta(weeks=3)).isoformat()[
        :-7
    ] + "Z"
    created_after = f"&created_after={three_weeks_ago}" if args.fast else ""

    project_ids = ["3996", "4913"]
    mr_pages = []
    with Progress(transient=True, expand=True) as progress:
        gitlab_download_task = progress.add_task(
            "[green]Downloading MR data...",
            start=False,
        )
        for project in project_ids:
            merge_requests_data = json.loads(
                requests.get(
                    f"{api_url}"
                    f"/projects/{project}/merge_requests"
                    f"?state=opened&per_page=500&sort=asc{created_after}",
                    headers={"PRIVATE-TOKEN": secret_token},
                ).content
            )
            if isinstance(merge_requests_data, dict):
                raise Exception(merge_requests_data)
            else:
                mr_pages += [
                    mr for mr in merge_requests_data if str(mr["iid"]) not in args.ignore
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
            mrs[id]["url"] = (
                f"{api_url}"
                f"/projects/{mr['project']}/merge_requests/{id}/discussions"
                f"?per_page=500"
            )

        with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
            # wrap in a list() to wait for all requests to complete
            progress.start_task(gitlab_download_task)
            progress.update(gitlab_download_task, total=len(mrs))
            for response_json, mr_id in executor.map(
                download_gitlab_data, [(mr["url"], id, secret_token) for id, mr in mrs.items()]
            ):
                mrs[mr_id]["discussion_data"] = response_json
                progress.update(gitlab_download_task, advance=1)

    for id, mr in mrs.items():
        discussion_data = mr["discussion_data"]
        discussion_data = [c for c in discussion_data if "resolved" in c["notes"][0]]
        discussion_data = [c for c in discussion_data if not c["notes"][0]["resolved"]]
        n_notes = len(discussion_data)
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

        color = random.choice(Constants.colors)

        if len(discussion_data) > 0:
            if n_response_required == 0 and not args.all:
                continue
            print()

            # Parse the VIRA ticket number
            jira_regex = re.compile(r".*JIRA: (.*)(\\n)*")
            jira_match = jira_regex.match(mr["mr_data"]["description"].split("\n")[-1])
            jira = None
            if jira_match:
                jira = jira_match.group(1)
                already_a_link_regex = re.compile(r"\[(.*)\].*")
                already_a_link = already_a_link_regex.match(jira)
                if already_a_link:
                    jira = already_a_link.group(1)

            mr_info_header = Panel(
                Text(
                    f"Open discussions: {n_notes}"
                    f"\nOpen discussions where you are involved: {n_your_notes}"
                    f"\nOpen discussions you need to respond (colored border): {n_response_required}"
                    f"\n\nGitLab: {mr['mr_data']['web_url']}"
                    f"\nJira:   {jira_url}/{jira}"
                    f"\n\n{mr['mr_data']['description']}"
                ),
                title=f"[bold {color}]{mr['mr_data']['title']} | !{mr['mr_data']['iid']} | {jira}",
                width=112,
            )
            console.print(mr_info_header)

        for comment in discussion_data:
            reply_needed = False
            if comment["notes"][-1]["author"]["username"] != user:
                reply_needed = True

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
                width=112,
                box=box.ROUNDED,
            )

            threads_table.add_column("Author", width=16)
            threads_table.add_column("Message", style="dim", min_width=89)
            # print(str(comment['notes'][0].get('body')))
            # print(comment['notes'][0].get('type', 'none'))
            for note in comment["notes"]:
                threads_table.add_row(note["author"]["name"], note["body"])

            if reply_needed:
                threads_table.add_row(
                    "Discussion link",
                    f"{mr['mr_data']['web_url']}#note_{comment['notes'][0]['id']}",
                )

            console.print(threads_table)

    return 0
