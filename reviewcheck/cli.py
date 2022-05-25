import argparse
from argparse import Namespace, RawTextHelpFormatter

import shtab


class Cli:
    @staticmethod
    def check_positive_int(value: str) -> int:
        try:
            ivalue = int(value)
        except Exception:
            raise argparse.ArgumentTypeError("Flag argument must be a positive integer")

        if ivalue > 0:
            return ivalue
        else:
            raise argparse.ArgumentTypeError("Flag argument must be a positive integer")

    @staticmethod
    def parse_arguments() -> Namespace:
        parser = argparse.ArgumentParser(
            description="""
        This script will tell you which discussions on GitLab you need to respond to.
        You will be shown the discussions from MRs where:

        - You are the author
        - Someone has replied to your comment but you haven't replied back
        - Someone has referenced your @username

        The script needs to be configured before you can use it. Add a
        ~/.config/reviewcheckrc with the following content:

        ```
        secret_token: <get a secret token from your settings in gitlab>
        user: <your username>
        ```
        """,
            formatter_class=RawTextHelpFormatter,
        )

        shtab.add_argument_to(parser, ["-s", "--print-completion"])

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

        parser.add_argument(
            "-r",
            "--refresh",
            help="If set, data will be refreshed at an interval specified in minutes",
            type=Cli.check_positive_int,
            action="store",
            default=None,
            dest="refresh_time",
        )

        subparsers = parser.add_subparsers(dest="command")

        subparsers.add_parser(
            "configure",
            help="Interactively set up configuration file",
            description="Asks for input to write to the configuration file.",
        )

        return parser.parse_args()
