import yaml

from reviewcheck.common.constants import Constants


class Config:
    """
    Class for interacting with the configuration file.
    """

    def __init__(self, reconfigure: bool):
        self.reconfigure = reconfigure

    def get_configuration(self) -> dict:
        """
        Reads the configuration file into a dictionary. If the configuration file does
        not exist, queries the user for information and writes it.

        :param reconfigure: If True, forces reconfiguration.

        :return: A dict containing the contents of the configuration file.
        """

        # Only attempt to write the configuration file if it does not already exist
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
                project_ids = [int(i) for i in project_ids.split(" ")]

            config_object = {
                "secret_token": token,
                "user": username,
                "api_url": api_url,
                "jira_url": jira_url,
                "project_ids": project_ids,
            }

            with open(Constants.CONFIG_PATH, "w") as f:
                f.write(yaml.safe_dump(config_object))

        with open(Constants.CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
