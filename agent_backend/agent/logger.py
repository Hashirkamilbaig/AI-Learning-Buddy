import logging
import sys

# 1. Create a logger instance
logger = logging.getLogger("AI_Learning_Buddy")
logger.setLevel(logging.INFO) # Set the lowest level of message to handle

# 2. Create a formatter - this defines the format of our log messages
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 3. Create a handler to write logs to the console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_format)

# 4. Create a handler to write logs to a file
file_handler = logging.FileHandler("agent_run.log")
file_handler.setFormatter(log_format)

# 5. Add the handlers to our logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)