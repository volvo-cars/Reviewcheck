# Copyright 2024 Volvo Car Corporation
# Licensed under Apache 2.0.

"""File containing custom reviewcheck exceptions."""


class RCException(Exception):
    """General exception for hiding stack trace in reviewcheck.

    Base exception to inherit from when creating custom exceptions and
    to use directly when it's not necessary to differentiate excepitons.
    It is caught in main and will print the message in the exceptions.
    """
