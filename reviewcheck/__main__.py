"""Main file for reviewcheck, where execution starts."""
import sys

from reviewcheck import app

if __name__ == "__main__":
    sys.exit(app.run())
