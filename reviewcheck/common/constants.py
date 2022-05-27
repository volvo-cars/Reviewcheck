from pathlib import Path
from typing import List


class Constants:
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

    CONFIG_PATH: Path = Path.home() / ".config" / "reviewcheckrc"

    TUI_MAX_WIDTH = 112
    TUI_AUTHOR_WIDTH = 16
    TUI_TWO_COL_PADDING_WIDTH = 7
