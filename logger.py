import os
import logging
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = datetime.now().strftime("%m_%d_%y_%H_%M_%S") + ".log"
log_path = os.path.join(LOG_DIR, log_filename)

LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - Line %(lineno)d - %(message)s"

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logging.getLogger().addHandler(console_handler)
