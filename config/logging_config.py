import logging
from logging.handlers import RotatingFileHandler
import sys # NEW: Import sys to direct output to the console

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Prevent the logger from propagating to the root logger
logger.propagate = False

# 1. Handler for writing to the log file (existing)
file_handler = RotatingFileHandler('whatsapp_messages.log', maxBytes=10000000, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# 2. Handler for writing to the console (NEW)
stream_handler = logging.StreamHandler(sys.stdout)
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)