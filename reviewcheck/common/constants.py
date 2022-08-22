"""File for holding constants used in reviewcheck."""
import os
from pathlib import Path
from typing import List


class Constants:
    """Class for holding constants used in reviewcheck."""

    COLORS: List[str] = [
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "bright_black",
        "bright_green",
        "bright_yellow",
        "bright_blue",
        "bright_magenta",
        "bright_cyan",
        "bright_white",
        "dark_cyan",
        "turquoise4",
        "spring_green1",
        "slate_blue3",
        "slate_blue3",
        "light_pink4",
        "medium_purple3",
        "light_slate_blue",
        "dark_goldenrod",
        "dark_olive_green3",
        "hot_pink3",
        "thistle3",
        "khaki1",
        "indian_red",
    ]

    CONFIG_DIR: Path = Path(os.environ.get("XDG_CONFIG", Path.home() / ".config"))
    CONFIG_PATH: Path = CONFIG_DIR / "reviewcheckrc"

    CACHE_DIR: Path = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    DATA_DIR: Path = CACHE_DIR / "reviewcheck"
    COMMENT_NOTE_IDS_PATH: Path = DATA_DIR / "old_comment_ids"

    TUI_AUTHOR_WIDTH = 16
    TUI_DATE_WIDTH = 12
    TUI_TWO_COL_PADDING_WIDTH = 7
    TUI_THREE_COL_PADDING_WIDTH = 10

    THREADPOOL_MAXSIZE = 32
