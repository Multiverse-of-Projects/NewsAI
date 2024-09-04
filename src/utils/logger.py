import logging
from logging.handlers import RotatingFileHandler

import colorlog


def setup_logger(log_file="app.log"):
    logger = logging.getLogger("news_api_logger")

    # Check if the logger already has handlers to avoid duplicate logs
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)

        # Create console handler with color coding
        handler = colorlog.StreamHandler()
        handler.setLevel(logging.DEBUG)

        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s%(reset)s: [%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        handler.setFormatter(formatter)

        # Create rotating file handler
        file_handler = RotatingFileHandler(log_file, maxBytes=5000000, backupCount=5)
        file_handler.setFormatter(
            logging.Formatter(
                "%(levelname)s: [%(asctime)s] %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

        # Add handlers to the logger
        logger.addHandler(handler)
        logger.addHandler(file_handler)

    return logger
