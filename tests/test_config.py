"""Tests for config.py."""
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import yaml

from reviewcheck.common.constants import Constants
from reviewcheck.config import Config


class TestConfig(TestCase):
    """Test cases for configuration-related operations."""

    @mock.patch("builtins.input")
    def test_setup_configuration(self, mock_input: mock.MagicMock) -> None:
        """Test the interactive setup configuration.

        Verifies that the interactive configuration setup works as
        expected.
        """
        # The setup_configuration method reads input from the user five
        # times in a row:
        # token, username, api url, jira url, and finally project IDs
        mock_input.side_effect = [
            "very_secret",
            "johndoe",
            "https://httpbin.org/status/200",
            "https://httpbin.org/status/200",
            "123 456",
        ]

        with tempfile.TemporaryDirectory(
            prefix="REVIEWCHECK_TEST_"
        ) as tmpdir, mock.patch(
            "reviewcheck.common.constants.Constants.CONFIG_PATH",
            Path(tmpdir) / "reviewcheckrc",
        ):
            Config(True).setup_configuration()

            with open(Constants.CONFIG_PATH, "r") as f:
                config_obj = yaml.safe_load(f)

            self.assertEqual(5, len(config_obj.values()))
            self.assertIn("secret_token", config_obj)
            self.assertIn("user", config_obj)
            self.assertIn("api_url", config_obj)
            self.assertIn("jira_url", config_obj)
            self.assertIn("project_ids", config_obj)

            self.assertEqual("very_secret", config_obj["secret_token"])
            self.assertEqual("johndoe", config_obj["user"])
            self.assertEqual("https://httpbin.org/status/200", config_obj["api_url"])
            self.assertEqual("https://httpbin.org/status/200", config_obj["jira_url"])
            self.assertEqual(2, len(config_obj["project_ids"]))
            self.assertIn(123, config_obj["project_ids"])
            self.assertIn(456, config_obj["project_ids"])

    def test_setup_configuration_without_reconfigure(self) -> None:
        """Test that configuration file is not altered when not needed.

        Verifies that the configuration setup does not alter anything if
        the file already exists.
        """
        with tempfile.TemporaryDirectory(
            prefix="REVIECHECK_TEST"
        ) as tmpdir, mock.patch(
            "reviewcheck.common.constants.Constants.CONFIG_PATH",
            Path(tmpdir) / "reviewcheckrc",
        ):
            config_obj = {
                "secret_token": "foo",
                "user": "stan",
                "api_url": "https://foo.bar/baz",
                "jira_url": "https://bar.baz/quux",
                "project_ids": [123, 456],
            }

            # Write the config, "mock" that it already exists
            with open(Constants.CONFIG_PATH, "w+") as f:
                f.write(yaml.safe_dump(config_obj))

            config = Config(False)

            # Read the file
            before = config.get_configuration()

            # Attempt to set up configuration
            config.setup_configuration()

            # Read the file again, after setup is finished
            after = config.get_configuration()

            # Verify that nothing has changed
            self.assertIsNotNone(before)
            self.assertIsNotNone(after)
            self.assertEqual(before, after)
