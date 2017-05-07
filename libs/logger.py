import os
import logging.handlers

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logfile = "{base_path}/logs/{name}.log".format(base_path=BASE_PATH, name=name)
    handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
