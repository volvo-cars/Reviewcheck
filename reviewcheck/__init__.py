# Copyright 2024 Volvo Car Corporation
# Licensed under Apache 2.0.

"""__init__ file for reviewcheck containing the __version__ variable."""
import tomllib
from pathlib import Path

pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)
    __version__ = pyproject_data["tool"]["poetry"]["version"]
