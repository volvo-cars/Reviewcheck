import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

import requests

from reviewcheck.common.constants import Constants
from reviewcheck.common.exceptions import RCException


class Utils:
    @staticmethod
    def convert_time(timestamp: str) -> str:
        """
        Converts timestamps from the format that GitLab uses to a human
        readable one like so:

            <date> <short month> <hour><minute>
        """
        try:
            time = datetime.strptime(
                timestamp,
                "%Y-%m-%dT%H:%M:%S.%f%z",
            )
        except ValueError:
            try:
                time = datetime.strptime(
                    timestamp[0:-6],
                    "%Y-%m-%dT%H:%M:%S.%f",
                )
            except ValueError:
                raise RCException(f"Couldn't parse GitLab timestamp '{timestamp}'")
        human_readable_time = datetime.strftime(
            time,
            "%d %b %H:%M",
        )
        return human_readable_time

    @staticmethod
    def download_gitlab_data(
        get_data: Tuple[str, int, str],
    ) -> Tuple[List[Dict[str, Any]], int]:
        # This is how to create a reusable connection pool with python
        # requests.

        with requests.Session() as session:
            session.mount(
                "https://",
                requests.adapters.HTTPAdapter(
                    pool_maxsize=Constants.THREADPOOL_MAXSIZE,
                    max_retries=3,
                    pool_block=True,
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
                    "request failed, error code %s [%s]",
                    response.status_code,
                    response.url,
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
