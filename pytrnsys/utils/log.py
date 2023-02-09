import logging as _log
import typing as _tp
import pathlib as _pl


FORMAT = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"


def getOrCreateCustomLogger(name: str, level: str, logFilePath: _tp.Optional[_pl.Path] = None) -> _log.Logger:
    logger = _log.getLogger(name)

    if logger.hasHandlers():
        return logger

    formatter = _log.Formatter(fmt=FORMAT)

    streamHandler = _log.StreamHandler()
    handlers: list[_log.Handler] = [streamHandler]

    if logFilePath:
        fileHandler = _log.FileHandler(logFilePath, mode="a")
        handlers.append(fileHandler)

    logger.setLevel(level)

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
