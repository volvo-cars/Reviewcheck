# Copyright 2022 Volvo Car Corporation
# Licensed under Apache 2.0.

"""Main file for reviewcheck, where execution starts."""
import sys

from reviewcheck import app

if __name__ == "__main__":
    sys.exit(app.run())
