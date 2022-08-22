"""General test file for reviewcheck."""
from reviewcheck import __version__


def test_version() -> None:
    """Test that the reviewcheck version is set correctly."""
    assert __version__ == "0.5.1"
