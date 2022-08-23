class RCException(Exception):
    """
    Base exception to inherit from when creating custom exceptions and
    to use directly when it's not necessary to differentiate excepitons.
    It is caught in main and will print the message in the exceptions.
    """
