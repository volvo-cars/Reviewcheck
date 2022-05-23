import argparse
from argparse import RawTextHelpFormatter, Namespace


class Cli:
    @staticmethod
    def parse_arguments() -> Namespace:
        parser = argparse.ArgumentParser(
            description="""
        This script will tell you which discussions on GitLab you need to respond to.
        You will be shown the discussions from MRs where:

        - You are the author
        - Someone has replied to your comment but you haven't replied back
        - Someone has referenced your @username

        The script needs to be configured before you can use it. Add a ~/.config/reviewcheckrc
        with the following content:

        ```
        secret_token: <get a secret token from your settings in gitlab>
        user: <your username>
        ```
        """,
            formatter_class=RawTextHelpFormatter,
        )
        parser.add_argument(
            "-a",
            "--all",
            help="Show all threads, even when you don't need to reply",
            action="store_true",
            default=False,
            dest="all",
        )
        parser.add_argument(
            "-u",
            "--user",
            help="Username whose reviews you want to analyze",
            action="store",
            default=False,
            dest="user",
        )
        parser.add_argument(
            "-f",
            "--fast-mode",
            help="Enables fast mode, only checking MRs created in the last three weeks",
            action="store_true",
            default=False,
            dest="fast",
        )
        parser.add_argument(
            "-i",
            "--ignore",
            help="Space separated list of MRs to ignore, e.g. '-i 373 371'",
            action="store",
            nargs="+",
            default=[],
            dest="ignore",
        )
        return parser.parse_args()
