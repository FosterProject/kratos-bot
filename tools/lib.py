import random
import time

from tools import config


def file_name(file_path):
    return file_path.split("/")[-1].split(".")[0]


def debug(debug_message):
    if config.DEBUG:
        print("DEBUG >> %s" % debug_message)


def wait(min, max):
    length = random.uniform(min, max)
    debug(">>>> Sleeping for: %s" % round(random.uniform(min, max), 2))
    time.sleep(length)
