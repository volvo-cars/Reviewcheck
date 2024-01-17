# Copyright 2024 Volvo Car Corporation
# Licensed under Apache 2.0.

"""File containing utility functions."""
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

from reviewcheck.constants import Constants
from reviewcheck.exceptions import RCException


class Utils:
    """Class that contains utility functions for reviewcheck."""

    @staticmethod
    def convert_time(timestamp: str) -> str:
        """Convert GitLab timestamps to human-readable timestamps.

        Convert timestamps from the format that GitLab uses to a human
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
    def download_data(
        params: Tuple[str, str, Optional[str], Any]
    ) -> Tuple[Any, Any, Any]:
        """Download data for MR, and for reaction if requested.

        This function just calls download_gitlab_data() twice. The point
        of this is that it makes it possible to download both reaction
        data and merge request data in the same loop in a multithreading
        executor.
        """
        token, mr_url, reaction_url, metadata = params
        reaction_response = []
        if reaction_url:
            reaction_response = Utils.download_gitlab_data(token, reaction_url)
        mr_response = Utils.download_gitlab_data(token, mr_url)
        return mr_response, reaction_response, metadata

    @staticmethod
    def download_gitlab_data(
        secret_token: str,
        url: str,
    ) -> List[Dict[str, Any]]:
        """Download each page of data for a given GitLab MR.

        Download the data for a given URL. All pages are downloaded and
        then combined to one list. The data mainly contains the comments
        and threads on the MR with associated metadata.

        :param secret_token: Token to access the GitLab API.
        :param url: URLs to download data from.
        :return: All data for the MR as a list.
        """
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
                return response_json

        raise Exception("Malformed data returned from GitLab.")
