# Copyright 2022 Volvo Car Corporation
# Licensed under Apache 2.0.

"""General test file for reviewcheck."""
from reviewcheck import __version__


def test_version() -> None:
    """Test that the reviewcheck version is set correctly."""
    assert __version__ == "0.5.1"
