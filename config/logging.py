import logging
from logging.handlers import RotatingFileHandler
import datetime
import os

# Log Levels
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL

# Define log file name format
log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_app_logs.log"

# Define the log directory
log_path = "./logs/"

# Ensure the "logs" directory exists
os.makedirs(log_path, exist_ok=True)

# Configure a rotating file handler
max_log_size = 10 * 1024 * 1024  # 10 MB
backup_count = 5  # Number of backup log files to keep
log_handler = RotatingFileHandler(
    filename=os.path.join(log_path, log_filename),  # Use os.path.join to create a path
    maxBytes=max_log_size,
    backupCount=backup_count
)

# Configure log message format
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

# Configure the root logger with desired settings, including the logging level
logging.basicConfig(
    level=logging.DEBUG,  # Set the desired logging level here
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[log_handler]  # Add the log handler to the root logger
)