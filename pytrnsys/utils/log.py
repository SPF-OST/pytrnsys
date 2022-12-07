import logging as _log
import typing as _tp
import pathlib as _pl


def get_or_create_custom_logger(name: str, level: str, logFilePath: _tp.Optional[_pl.Path] = None) -> _log.Logger:
    if _log.getLogger(name).hasHandlers():
        return _log.getLogger(name)
    else:
        formatter = _log.Formatter(fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s")

        streamHandler = _log.StreamHandler()
        handlers = [streamHandler]
        streamHandler.setFormatter(formatter)

        if logFilePath:
            fileHandler = _log.FileHandler(logFilePath, mode="a")
            handlers.append(fileHandler)

        logger = _log.getLogger(name)
        logger.setLevel(level)

        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger
