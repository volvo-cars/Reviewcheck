from datetime import datetime

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
