import logging
import os

from src.config_loader.configLoader import YmlLoader


def set_log_level(level):
    """
    Sets the log level for logger (logging)
    Args:
        level: the log level

    Returns:

    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

if 'DJANGO_SETTINGS_MODULE' in os.environ:
    logger = logging.getLogger(__name__)
else:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

logger.info('This is a test log message')

YmlLoader = YmlLoader("test.yml")
