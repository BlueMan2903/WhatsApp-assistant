import logging
from logging.handlers import RotatingFileHandler
import sys
from bidi.algorithm import get_display # Ensure python-bidi is installed

class BidiFormatter(logging.Formatter):
    """
    Custom formatter to handle Hebrew RTL text in LTR terminals.
    It applies the Unicode Bidirectional Algorithm to the message.
    """
    def format(self, record):
        msg = super().format(record)
        try:
            # get_display converts logical Hebrew to visual Hebrew
            return get_display(msg)
        except:
            return msg

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

# 1. File Handler (Keep logical order, ensure UTF-8)
file_handler = RotatingFileHandler(
    'whatsapp_messages.log', 
    maxBytes=10000000, 
    backupCount=5, 
    encoding='utf-8' # CRITICAL: Fixes encoding issues
)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# 2. Console Handler (Visual order for human reading)
stream_handler = logging.StreamHandler(sys.stdout)
# Use our new BidiFormatter for the console output
stream_formatter = BidiFormatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)