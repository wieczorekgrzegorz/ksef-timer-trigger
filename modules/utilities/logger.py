"""Sets up custom logger."""

import logging

log = logging.getLogger(name="log")


def set_up(
    message_format: str = "%(levelname)s, %(name)s.%(funcName)s: %(message)s",
    level: int = logging.INFO,
) -> None:
    """
    Sets up custom logger.

    Parameters:
        format (str, optional): Logging format. Defaults to "%(name)s%(funcName)s: %(message)s".
        level (int, optional): Logging level. Defaults to logging.INFO.

    Returns:
        None
    """
    log.debug(msg="Setting up custom logger.")

    log.setLevel(level=level)

    handler = logging.StreamHandler(stream=None)

    formatter = logging.Formatter(fmt=message_format)
    handler.setFormatter(fmt=formatter)

    if log.hasHandlers():
        log.handlers.clear()

    log.addHandler(hdlr=handler)
