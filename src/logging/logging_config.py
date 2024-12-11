import logging

import os

if 'DJANGO_SETTINGS_MODULE' in os.environ:
    logger = logging.getLogger(__name__)
else:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

logger.info('This is a test log message')

