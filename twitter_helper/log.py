
import logging
import sys
import functools


def filter_max_level(max_level: int, record: logging.LogRecord):
    return record.levelno <= max_level


def setup_logging(verbose: bool = False):
    """
    Set up logging handlers, should only ever be called by __main__.main.

    I like my INFO and lower logs to go to stdout, and my WARNING
    and higher logs to go to stderr. This works well with docker
    because it keeps track of stderr vs stdout, and thus things like
    filebeat can easily distinguish errors.

    I also like my logging level at INFO by default. Verbose sets
    the root logger's log level at DEBUG.

    Personally I don't use WARNING, I just use DEBUG, INFO, and ERROR.
    WARNING is just a cop-out, it's either an ERROR that needs action, or
    INFO about and edge case that is being handled.

    :param verbose: if True, set level to debug.
    """

    root = logging.getLogger()
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    root.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.addFilter(functools.partial(filter_max_level, logging.INFO))
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)
    root.addHandler(stderr_handler)
