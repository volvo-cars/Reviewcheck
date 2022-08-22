"""Parse the command line arguments given to reviewcheck."""
import argparse
from argparse import Namespace, RawTextHelpFormatter

import shtab


class Cli:
    """Class with the functions associated with argument parsing."""

    @staticmethod
    def check_positive_int(value: str) -> int:
        """Return positive int if possible, otherwise raise exception.

        Validator for checking that a variable is a positive integer and
        converting it to the int type.

        :param value: The value given on command line.

        :raises:ArgumentTypeError: Raised when the value cannot be
            converted to a positive integer.

        :return: The value as a positive int if possible.
        """
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
        """Parse the arguments given on the command line.

        Create an argument parser and use it to parse the arguments
        given on the command line.

        :return: The parsed arguments as a Namespace object.
        """
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

        There is also some optional configuration:

        ```
        ignored_mrs: [123, 546, 789] (defult: empty list)
        show_all_discussions: true (defult: false)
        hide_replied_discussions: true (default: false)
        ```
        """,
            formatter_class=RawTextHelpFormatter,
        )

        parser.add_argument(
            "--version",
            help="Show version",
            dest="print_version",
            required=False,
            action="store_true",
            default=False,
        )

        shtab.add_argument_to(parser, ["-s", "--print-completion"])  # type: ignore

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

        parser.add_argument(
            "-m",
            "--minimal",
            help="Only show discussion where a reply is needed.",
            action="store_true",
            default=False,
            dest="minimal",
        )

        parser.add_argument(
            "-w",
            "--width",
            help="Terminal display width",
            type=Cli.check_positive_int,
            action="store",
            dest="output_width",
        )

        subparsers = parser.add_subparsers(dest="command")

        subparsers.add_parser(
            "configure",
            help="Interactively set up configuration file",
            description="Asks for input to write to the configuration file.",
        )

        return parser.parse_args()
