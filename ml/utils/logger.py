import logging
import os

from .constants import LOG_DIR


def create_file_logger(log_name: str) -> logging.Logger:

    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, log_name)

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(message)s')

    with open(log_file, 'w'):
        pass

    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(stream_handler)

    logger.addHandler(file_handler)

    return logger
