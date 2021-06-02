# pylint: skip-file
# type: ignore

import logging


def setup_custom_logger(name, level):
    if logging.getLogger(name).hasHandlers():
        return logging.getLogger(name)
    else:
        formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger
