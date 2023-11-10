"""Sets up custom logger."""

import logging

log = logging.getLogger(name="log")


def get_logger_level(level_string: str, default_value: int = logging.INFO) -> int:
    """Translates global env. "LOGGER_LEVEL" string value to int value for logging level.
    If the string value is not recognized, the default value is returned."""

    logger_level = getattr(logging, level_string.upper(), None)
    if not isinstance(logger_level, int):
        log.warning(
            msg=f"Logger level {level_string} not recognized. Falling back to default value: {default_value}. Check the value of the LOGGER_LEVEL environmental variable."  # pylint: disable=line-too-long
        )
        logger_level = default_value
    return logger_level


def set_up(
    message_format: str = "%(levelname)s, %(name)s.%(funcName)s: %(message)s",
    level_string: "str" = "INFO",
) -> None:
    """
    Sets up custom logger.

    Parameters:
        format (str, optional): Logging format. Defaults to "%(levelname)s, %(name)s.%(funcName)s: %(message)s".
        level_string (int, optional): Logging level. Defaults to logging.INFO.

    Returns:
        None
    """
    log.debug(msg="Setting up custom logger.")

    handler = logging.StreamHandler(stream=None)

    formatter = logging.Formatter(fmt=message_format)
    handler.setFormatter(fmt=formatter)

    if log.hasHandlers():
        log.handlers.clear()

    log.addHandler(hdlr=handler)

    level = get_logger_level(level_string=level_string)

    log.setLevel(level=level)
