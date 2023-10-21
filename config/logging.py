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

# Define the log directory
log_path = "./logs/"

# Ensure the "logs" directory exists
os.makedirs(log_path, exist_ok=True)

# Define log file name format and path
log_filename = datetime.datetime.now().strftime("%Y-%m-%d") + "_app_logs.log"
log_file_path = os.path.join(log_path, log_filename)

# Configure a rotating file handler
max_log_size = 10 * 1024 * 1024  # 10 MB
backup_count = 5  # Number of backup log files to keep

# Check if the log file for today already exists and if it's less than the size limit
if os.path.exists(log_file_path):
    if os.path.getsize(log_file_path) >= max_log_size:
        # Rotate the log file and create a new one
        for i in range(backup_count, 0, -1):
            # Rename existing backup files
            if os.path.exists(log_file_path + f".{i}"):
                os.rename(log_file_path + f".{i}", log_file_path + f".{i+1}")
        os.rename(log_file_path, log_file_path + ".1")

log_handler = RotatingFileHandler(
    filename=log_file_path,
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