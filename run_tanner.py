import sys
import threading
import time

import keyboard

from debug import debug
from tools import config
from tools.lib import wait
from tools import client_handler
from tools.client import Client

config.DEBUG = True
debug.reset_stream()

# Constants
EXIT_FLAG = False
def stop():
    global EXIT_FLAG
    EXIT_FLAG = True


def exit_bot(bot):
    print("==== SHUTTING DOWN BOT [%s] ====" % bot["bot"].name)
    bot["bot"].client.exit()
    bot["thread"].join()


# Define bots
from bots import tanner
bot_clients = client_handler.get_clients()
bots = []
for name, client, host in bot_clients:
    client_handler.default_host_size(host)
    bots.append({"bot": tanner.Tanner(Client(name, client, host), tanner.TAN_SOFT_LEATHER), "thread": None})

# Run bots
for bot in bots:
    thread = threading.Thread(target=bot["bot"].run)
    bot["thread"] = thread
    thread.start()
    time.sleep(30)
    print("==== WAITING 30 SECS TO START NEXT BOT ====")

try:
    while True:
        pass
except KeyboardInterrupt:
    stop()

# Exit threads and bots
print("Shutting down bots... waiting for them to finish their loop")
for bot in bots:
    bot["bot"].client.exit()
    bot["thread"].join()
