"""File containing the Config class for working with config files."""
from typing import Any, Dict, Optional

import yaml

from reviewcheck.common.constants import Constants


class Config:
    """Class for interacting with the configuration file."""

    def __init__(self, reconfigure: bool):
        """Set initial variable state for the Config class.

        :param reconfigure: Whether or not the user has requested to
            update the configuration of reviewcheck.
        """
        self.reconfigure = reconfigure

    def setup_configuration(self) -> None:
        """Let the user configure the application.

        This will be done if the user has requested to configure
        reviewcheck or if no config file can be found.
        """
        # Only attempt to write the configuration file if it does not
        # already exist.
        if self.reconfigure or not Constants.CONFIG_PATH.exists():
            Constants.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

            if not self.reconfigure:
                print(
                    f"No configuration file found at {str(Constants.CONFIG_PATH)}, "
                    "please provide some information to populate it:"
                )

            token = input("GitLab API token: ")
            username = input("Username: ")
            api_url = input("API URL: ")
            jira_url = input("Jira URL: ")
            project_ids = input("Project IDs (space-separated): ")

            if project_ids:
                project_ids_list = [int(i) for i in project_ids.split(" ")]
            else:
                project_ids_list = []

            config_object: Dict[str, Any] = {
                "secret_token": token,
                "user": username,
                "api_url": api_url,
                "jira_url": jira_url,
                "project_ids": project_ids_list,
            }

            with open(Constants.CONFIG_PATH, "w") as f:
                f.write(yaml.safe_dump(config_object))

    def get_configuration(self) -> Optional[Dict[str, Any]]:
        """Read the configuration file into a dictionary.

        Reads the configuration file into a dictionary. If the
        configuration file does not exist, queries the user for
        information and writes it.

        :return: A dict containing the contents of the configuration
            file, or None if the file does not exist.
        """
        self.setup_configuration()
        try:
            with open(Constants.CONFIG_PATH, "r") as f:
                content = yaml.safe_load(f)
        except FileNotFoundError:
            return None

        if isinstance(content, dict):
            return content
        else:
            print(
                f"ERROR - the configuration {Constants.CONFIG_PATH} couldn't"
                "be parsed as a dictionary."
            )

        return None
