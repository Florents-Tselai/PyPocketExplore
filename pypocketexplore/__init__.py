from __future__ import absolute_import
from logging import handlers
__author__ = 'Florents Tselai'

import logging

__all__ = ['cli', 'api', 'model', 'parser']


def setup_logger(name):
    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - PID:%(process)d - %(name)s.py:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # create a file handler
    file_handler = handlers.RotatingFileHandler('{}.log'.format(name), maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


log = logger = setup_logger()
